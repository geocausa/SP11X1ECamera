/* SPDX-License-Identifier: GPL-2.0-only */
/* SP11 rear public-request transport qualification.
 * Continuous hardware ISP with bounded manual exposure/gain qualification.
 * Automatic IPA and per-frame sensor exposure timestamps are not implemented.
 * No CPU image mapping, software ISP, sensor group-hold or fictitious metadata.
 */
#include <array>
#include <cstdlib>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <chrono>
#include "rear-manual-controls.h"
#include <cerrno>
#include <memory>
#include <map>
#include <libcamera/ipa/camss_x1e_rear_ipa_interface.h>
#include <libcamera/ipa/camss_x1e_rear_ipa_proxy.h>
#include "libcamera/internal/ipa_manager.h"
#include "libcamera/internal/mapped_framebuffer.h"
#include "libcamera/internal/framebuffer.h"
#include "native-rear-stats.h"
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <linux/media-bus-format.h>
#include <libcamera/base/log.h>
#include <libcamera/camera.h>
#include <libcamera/control_ids.h>
#include <libcamera/formats.h>
#include <libcamera/framebuffer.h>
#include <libcamera/property_ids.h>
#include <libcamera/request.h>
#include <libcamera/stream.h>
#include "libcamera/internal/camera.h"
#include "libcamera/internal/device_enumerator.h"
#include "libcamera/internal/media_device.h"
#include "libcamera/internal/pipeline_handler.h"
#include "libcamera/internal/v4l2_subdevice.h"
#include "libcamera/internal/v4l2_videodevice.h"

namespace libcamera {
LOG_DEFINE_CATEGORY(CAMSSX1ERear)
namespace {
constexpr Size kInput{ 4064, 2286 };
constexpr Size kOutput{ 3840, 2160 };
constexpr unsigned int kStride = 3840, kImageBytes = 12441600;
}
class PipelineHandlerCamssX1ERear;
class RearData final : public Camera::Private
{
public:
 RearData(PipelineHandler *pipe, std::shared_ptr<MediaDevice> media)
  : Camera::Private(pipe), media_(std::move(media)) {}
 int init();
 int open();
 void close();
 int configure();
 int applyControls(const ControlList &controls);
 int64_t lastCompleted_ = -1;
 void ready(FrameBuffer *buffer);
 int startStatistics();
 void stop();
 void cancelImage(FrameBuffer *);
 void fail(const char *);
 void statisticsReady(FrameBuffer *);
 void statisticsValidated(uint32_t,uint64_t,uint32_t,uint64_t,int32_t,uint64_t,uint64_t);
 void finish();
 struct Frame {FrameBuffer *image=nullptr,*meta=nullptr;uint64_t timestamp=0,owner=0,generation=0;bool validated=false;};
 std::map<uint32_t,Frame> frames_;
 std::unique_ptr<V4L2VideoDevice> statistics_;
 std::unique_ptr<ipa::camss_x1e_rear::IPAProxyCamssX1ERear> ipa_;
 std::vector<std::unique_ptr<FrameBuffer>> metadata_;
 std::map<FrameBuffer *,std::unique_ptr<MappedFrameBuffer>> mappings_;
 std::vector<uint32_t> ipaIds_;
 bool statisticsAllocated_=false,statisticsOn_=false,ipaStarted_=false,failed_=false;
 uint64_t streamId_=0,ownerId_=0;
 uint32_t received_=0,joined_=0,privateSaved_=0;
 int privateDirectory_=-1;
 int openPrivateStatistics();
 int savePrivateStatistics(uint32_t,const uint8_t *);
 std::shared_ptr<MediaDevice> media_;
 std::unique_ptr<V4L2Subdevice> sensor_, phy_, csid_, vfe_;
 std::unique_ptr<V4L2VideoDevice> video_;
 Stream stream_;
 bool running_ = false, allocated_ = false;
 unsigned int admitted_ = 0;
};
class RearConfiguration final : public CameraConfiguration
{
public:
 Status validate() override
 {
  if (config_.empty() || sensorConfig)
   return Invalid;
  Status status = Valid;
  if (config_.size() != 1) {
   config_.resize(1);
   status = Adjusted;
  }
  if (orientation != Orientation::Rotate0) {
   orientation = Orientation::Rotate0;
   status = Adjusted;
  }
  auto &cfg = config_[0];
  if (cfg.pixelFormat != formats::NV12 || cfg.size != kOutput || cfg.bufferCount != 4) {
   cfg.pixelFormat = formats::NV12;
   cfg.size = kOutput;
   cfg.bufferCount = 4;
   status = Adjusted;
  }
  cfg.stride = kStride;
  cfg.frameSize = kImageBytes;
  return status;
 }
};
class PipelineHandlerCamssX1ERear final : public PipelineHandler
{
public:
 PipelineHandlerCamssX1ERear(CameraManager *manager) : PipelineHandler(manager) {}
 std::unique_ptr<CameraConfiguration> generateConfiguration(Camera *, Span<const StreamRole> roles) override
 {
  auto config = std::make_unique<RearConfiguration>();
  if (roles.empty())
   return config;
  StreamFormats formatsMap({ { formats::NV12, { SizeRange(kOutput) } } });
  StreamConfiguration cfg(formatsMap);
  cfg.pixelFormat = formats::NV12;
  cfg.size = kOutput;
  cfg.bufferCount = 4;
  config->addConfiguration(cfg);
  config->validate();
  return config;
 }
 int configure(Camera *camera, CameraConfiguration *config) override
 {
  auto *data = cameraData(camera);
  int ret = data->configure();
  if (!ret)
   config->at(0).setStream(&data->stream_);
  return ret;
 }
 int exportFrameBuffers(Camera *camera, Stream *stream,
                        std::vector<std::unique_ptr<FrameBuffer>> *buffers) override
 {
  return cameraData(camera)->video_->exportBuffers(stream->configuration().bufferCount, buffers);
 }
 int start(Camera *camera, const ControlList *controls) override
 {
  auto *data = cameraData(camera);
  if (controls) {
   int ret = data->applyControls(*controls);
   if (ret) return ret;
  }
  if (data->running_ || data->allocated_ || data->statisticsAllocated_)
   return -EBUSY;
  int ret=data->startStatistics();
  if(ret){data->stop();return ret;}
  ret = data->video_->importBuffers(data->stream_.configuration().bufferCount);
  if (ret){data->stop();return ret;}
  data->allocated_ = true;
  /* The driver requires two queued buffers before hardware start, so empty
   * STREAMON arms the queue; ordinary camera requests supply those buffers.
   */
  ret = data->video_->streamOn();
  if (ret) {
   data->stop();
   return ret;
  }
  data->admitted_ = 0;
  data->lastCompleted_ = -1;
  data->running_ = true;
  return 0;
 }
 void stopDevice(Camera *camera) override { cameraData(camera)->stop(); }
 int queueRequestDevice(Camera *camera, Request *request) override
 {
  auto *data = cameraData(camera);
  if (!data->running_ || data->failed_)
   return -ESHUTDOWN;
  /* Requests may reuse application buffers after exact live retirement. */
  auto *buffer = request->findBuffer(&data->stream_);
  if (!buffer)
   return -ENOENT;
  int controlsRet = data->applyControls(request->controls());
  if (controlsRet) return controlsRet;
  int ret = data->video_->queueBuffer(buffer);
  if (!ret)
   data->admitted_++;
  return ret;
 }
 bool match(DeviceEnumerator *enumerator) override
 {
  DeviceMatch match("qcom-camss");
  for (const char *name : { "msm_csiphy1", "msm_csid1", "msm_vfe1_pix", "msm_vfe1_stats" })
   match.add(name);
  auto media = acquireMediaDevice(enumerator, match);
  if (!media)
   return false;
  auto data = std::make_unique<RearData>(this, media);
  if (data->init())
   return false;
  data->ipa_=IPAManager::createIPA<ipa::camss_x1e_rear::IPAProxyCamssX1ERear>(this,0,0);
  if(!data->ipa_)return false;
  data->ipa_->statisticsValidated.connect(data.get(),&RearData::statisticsValidated);
  IPASettings settings{};settings.sensorModel="ov13858";
  if(data->ipa_->init(settings))return false;
  std::set<Stream *> streams{ &data->stream_ };
  auto camera = Camera::create(std::move(data), "sp11-rear-ov13858-qualification", streams);
  registerCamera(std::move(camera));
  return true;
 }
private:
 bool acquireDevice(Camera *camera) override { return cameraData(camera)->open() == 0; }
 void releaseDevice(Camera *camera) override
 {
  auto *data = cameraData(camera);
  data->close();
  if (data->media_->disableLinks())
   LOG(CAMSSX1ERear, Error) << "Could not restore neutral media links";
 }
 RearData *cameraData(Camera *camera) { return static_cast<RearData *>(camera->_d()); }
};

int RearData::init()
{
 MediaEntity *sensor = nullptr;
 for (auto *entity : media_->entities()) {
  if (entity->function() == MEDIA_ENT_F_CAM_SENSOR && entity->name().compare(0, 8, "ov13858 ") == 0) {
   if (sensor)
    return -ENODEV;
   sensor = entity;
  }
 }
 if (!sensor)
  return -ENODEV;
 sensor_ = std::make_unique<V4L2Subdevice>(sensor);
 phy_ = V4L2Subdevice::fromEntityName(media_.get(), "msm_csiphy1");
 csid_ = V4L2Subdevice::fromEntityName(media_.get(), "msm_csid1");
 vfe_ = V4L2Subdevice::fromEntityName(media_.get(), "msm_vfe1_pix");
 auto *pixel = media_->getEntityByName("msm_vfe1_pix");
 if (!phy_ || !csid_ || !vfe_ || !pixel)
  return -ENODEV;
 const MediaEntity *output = nullptr;
 for (const auto *pad : pixel->pads()) {
  if (!(pad->flags() & MEDIA_PAD_FL_SOURCE))
   continue;
  for (const auto *link : pad->links()) {
   auto *sink = link->sink()->entity();
   if (sink->type() == MediaEntity::Type::V4L2VideoDevice && sink->name() != "msm_vfe1_stats") {
    if (output)
     return -ENODEV;
    output = sink;
   }
  }
 }
 if (!output)
  return -ENODEV;
 video_ = std::make_unique<V4L2VideoDevice>(output);
 statistics_=V4L2VideoDevice::fromEntityName(media_.get(),"msm_vfe1_stats");
 if(!statistics_)return -ENODEV;
 int ret = open();
 if (ret)
  return ret;
 /* The ordinary front default advertises 2560x1440, not this candidate's
  * exact 4K geometry. Enumeration is read-only and cannot start hardware.
  */
 auto supported = video_->formats();
 auto it = supported.find(V4L2PixelFormat(V4L2_PIX_FMT_NV12));
 bool exact = it != supported.end() && it->second.size() == 1 &&
              it->second[0].min == kOutput && it->second[0].max == kOutput;
 if (!exact || !video_->caps().isVideoCapture()) {
  close();
  return -EOPNOTSUPP;
 }
 ControlInfoMap::Map manual;
 manual.emplace(&controls::ExposureTime, ControlInfo{RearManual::exposureUs(RearManual::MinLines), RearManual::exposureUs(RearManual::MaxLines), RearManual::exposureUs(RearManual::DefaultLines)});
 manual.emplace(&controls::AnalogueGain, ControlInfo{1.0f,8.0f,1.0f});
 controlInfo_ = ControlInfoMap(std::move(manual), controls::controls);
 properties_.set(properties::Model, std::string("OV13858"));
 properties_.set(properties::Location, properties::CameraLocationBack);
 video_->bufferReady.connect(this, &RearData::ready);
 statistics_->bufferReady.connect(this,&RearData::statisticsReady);
 close();
 return 0;
}
int RearData::open()
{
 for (auto *device : { sensor_.get(), phy_.get(), csid_.get(), vfe_.get() }) {
  int ret = device->open();
  if (ret) {
   close();
   return ret;
  }
 }
 int ret = video_->open();
 if(!ret)ret=statistics_->open();
 if (ret)
  close();
 return ret;
}
void RearData::close()
{
 if(statistics_)statistics_->close();
 if (video_)
  video_->close();
 for (auto *device : { sensor_.get(), phy_.get(), csid_.get(), vfe_.get() })
  if (device)
   device->close();
}
int RearData::configure()
{
 if (running_ || allocated_ || statisticsAllocated_)
  return -EBUSY;
 int ret = media_->disableLinks();
 if (ret)
  return ret;
 for (auto [source, pad, sink] :
      std::array<std::tuple<const char *, unsigned int, const char *>, 2>{
       std::make_tuple("msm_csiphy1", 1U, "msm_csid1"),
       std::make_tuple("msm_csid1", 4U, "msm_vfe1_pix") }) {
  auto *link = media_->link(source, pad, sink, 0);
  if (!link)
   return -ENOLINK;
  ret = link->setEnabled(true);
  if (ret)
   return ret;
 }
 for (auto [device, pad] :
      std::array<std::pair<V4L2Subdevice *, unsigned int>, 7>{
       std::make_pair(sensor_.get(), 0), std::make_pair(phy_.get(), 0),
       std::make_pair(phy_.get(), 1), std::make_pair(csid_.get(), 0),
       std::make_pair(csid_.get(), 4), std::make_pair(vfe_.get(), 0),
       std::make_pair(vfe_.get(), 1) }) {
  V4L2SubdeviceFormat raw{};
  raw.code = MEDIA_BUS_FMT_SGRBG10_1X10;
  raw.size = kInput;
  ret = device->setFormat(pad, &raw);
  if (ret || raw.size != kInput || raw.code != MEDIA_BUS_FMT_SGRBG10_1X10)
   return ret ? ret : -EINVAL;
 }
 V4L2DeviceFormat format{};
 format.fourcc = V4L2PixelFormat(V4L2_PIX_FMT_NV12);
 format.size = kOutput;
 ret = video_->setFormat(&format);
 if (ret || format.size != kOutput || format.fourcc != V4L2PixelFormat(V4L2_PIX_FMT_NV12) ||
     format.planesCount != 1 || format.planes[0].bpl != kStride || format.planes[0].size != kImageBytes)
  return ret ? ret : -EINVAL;
 V4L2DeviceFormat meta{};
 ret=statistics_->getFormat(&meta);
 if(ret||meta.fourcc!=V4L2PixelFormat(NATIVE_REAR_STATS_MAGIC)||
    meta.planesCount!=1||meta.planes[0].size!=NATIVE_REAR_STATS_BYTES)
  return ret?ret:-EPROTO;
 const std::array<uint32_t,3> timingIds{V4L2_CID_PIXEL_RATE,V4L2_CID_HBLANK,V4L2_CID_VBLANK};
 ControlList timing=sensor_->getControls(timingIds);
 if (timing.size()!=3 || timing.get(V4L2_CID_PIXEL_RATE).get<int64_t>() != int64_t(RearManual::PixelRate) ||
     timing.get(V4L2_CID_HBLANK).get<int32_t>() != 424 || timing.get(V4L2_CID_VBLANK).get<int32_t>() != 928)
  return -EPROTO;
 return 0;
}
int RearData::applyControls(const ControlList &requestControls)
{
 if (requestControls.empty())
  return 0;
 ControlList values(sensor_->controls());
 for (const auto &entry : requestControls) {
  if (entry.second.isArray()) return -ERANGE;
  int32_t code = 0;
  if (entry.first == controls::ExposureTime) {
   if (entry.second.type() != ControlTypeInteger32 ||
       !RearManual::exposureLines(entry.second.get<int32_t>(), &code))
    return -ERANGE;
   values.set(V4L2_CID_EXPOSURE, code);
  } else if (entry.first == controls::AnalogueGain) {
   if (entry.second.type() != ControlTypeFloat ||
       !RearManual::gainCode(entry.second.get<float>(), &code))
    return -ERANGE;
   values.set(V4L2_CID_ANALOGUE_GAIN, code);
  } else {
   return -EOPNOTSUPP;
  }
 }
 const auto before = std::chrono::steady_clock::now();
 int ret = sensor_->setControls(&values);
 const auto after = std::chrono::steady_clock::now();
 if (ret)
  return ret < 0 ? ret : -EIO;
 std::vector<uint32_t> ids;
 for (const auto &entry : values)
  ids.push_back(entry.first);
 ControlList cached = sensor_->getControls(ids);
 if (cached.size() != values.size())
  return -EIO;
 for (const auto &entry : values) {
  if (!cached.contains(entry.first) || cached.get(entry.first) != entry.second)
   return -EPROTO;
  LOG(CAMSSX1ERear, Info) << "NATIVE_REAR_LIBCAMERA_CONTROL id=" << entry.first
   << " value=" << entry.second.get<int32_t>()
   << " last_completed_sequence=" << lastCompleted_
   << " before_ns=" << std::chrono::duration_cast<std::chrono::nanoseconds>(before.time_since_epoch()).count()
   << " after_ns=" << std::chrono::duration_cast<std::chrono::nanoseconds>(after.time_since_epoch()).count()
   << " cached_readback=1 per_frame_association=0";
 }
 return 0;
}

int RearData::startStatistics()
{
 if(statisticsAllocated_||ipaStarted_||!metadata_.empty())return -EBUSY;
 int ret=openPrivateStatistics();
 if(ret)return ret;
 ret=statistics_->allocateBuffers(8,&metadata_);
 if(ret!=8){
  if(ret>=0)statisticsAllocated_=true;
  return ret<0?ret:-ENOMEM;
 }
 statisticsAllocated_=true;
 std::vector<IPABuffer> buffers;
 uint32_t id=0;
 for(const auto &b:metadata_){
  b->setCookie(++id);
  auto map=std::make_unique<MappedFrameBuffer>(b.get(),MappedFrameBuffer::MapFlag::Read);
  if(!map->isValid()||map->planes().size()!=1||
     map->planes()[0].size()<NATIVE_REAR_STATS_BYTES)return -EINVAL;
  mappings_.emplace(b.get(),std::move(map));
  buffers.emplace_back(id,std::vector<FrameBuffer::Plane>{b->planes().begin(),b->planes().end()});
 }
 ret=ipa_->mapBuffers(buffers);
 if(ret)return ret;
 for(const auto &b:buffers)ipaIds_.push_back(b.id);
 ret=ipa_->start();
 if(ret)return ret;
 ipaStarted_=true;
 for(const auto &b:metadata_){
  ret=statistics_->queueBuffer(b.get());
  if(ret)return ret;
 }
 ret=statistics_->streamOn();
 if(ret)return ret;
 statisticsOn_=true;
 streamId_=ownerId_=0;received_=joined_=0;failed_=false;frames_.clear();
 return 0;
}
int RearData::openPrivateStatistics()
{
 if(privateDirectory_>=0)return -EBUSY;
 const char *value=std::getenv("SP11_REAR_STATISTICS_DIR");
 if(!value)return -EINVAL;
 const std::string root="/var/lib/sp11-camera-native-rear-generation-20261007-58/private-statistics/session-";
 std::string path=value;
 if(path!=root+"1"&&path!=root+"2"&&path!=root+"3")return -EPERM;
 privateDirectory_=::open(path.c_str(),O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
 if(privateDirectory_<0)return -errno;
 struct stat st{};
 if(::fstat(privateDirectory_,&st)||!S_ISDIR(st.st_mode)||st.st_uid!=::geteuid()||
    (st.st_mode&0777)!=0700){::close(privateDirectory_);privateDirectory_=-1;return -EPERM;}
 privateSaved_=0;
 return 0;
}
int RearData::savePrivateStatistics(uint32_t sequence,const uint8_t *data)
{
 /* Same temporal windows as private whole-frame scalar Y samples. */
 bool selected=false;
 for(uint32_t begin:{56U,120U,184U,248U})
  for(uint32_t offset:{0U,7U,10U,11U,12U,23U})
   if(sequence==begin+offset)selected=true;
 if(!selected)return 0;
 if(privateDirectory_<0||privateSaved_>=24)return -EINVAL;
 std::string name="statistics-"+std::to_string(sequence)+".qxr1";
 int fd=::openat(privateDirectory_,name.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);
 if(fd<0)return -errno;
 size_t written=0;
 while(written<NATIVE_REAR_STATS_BYTES){
  ssize_t n=::write(fd,data+written,NATIVE_REAR_STATS_BYTES-written);
  if(n<0&&errno==EINTR)continue;
  if(n<=0){int ret=n<0?-errno:-EIO;::close(fd);return ret;}
  written+=n;
 }
 if(::close(fd))return -errno;
 ++privateSaved_;
 return 0;
}
void RearData::cancelImage(FrameBuffer *b)
{
 Request *r=b->request();
 if(!r)return;
 b->_d()->cancel();
 auto *handler=static_cast<PipelineHandlerCamssX1ERear *>(pipe());
 handler->completeBuffer(r,b);
 handler->completeRequest(r);
}
void RearData::stop()
{
 running_=false;
 if(privateDirectory_>=0){::close(privateDirectory_);privateDirectory_=-1;}
 int videoRet=allocated_?video_->streamOff():0;
 int statsRet=statisticsAllocated_?statistics_->streamOff():0;
 statisticsOn_=false;
 /* Synchronous IPA stop prevents shared mappings from being released while
  * an asynchronous receiver still accesses them. */
 if(ipaStarted_){ipa_->stop();ipaStarted_=false;}
 if(!ipaIds_.empty()){ipa_->unmapBuffers(ipaIds_);ipaIds_.clear();}
 for(auto &[sequence,frame]:frames_){
  (void)sequence;
  if(frame.image)cancelImage(frame.image);
 }
 frames_.clear();
 LOG(CAMSSX1ERear,Info)<<"NATIVE_REAR_STATISTICS_JOIN received="<<received_
  <<" joined="<<joined_<<" stream="<<streamId_<<" owner="<<ownerId_
  <<" failed="<<failed_<<" private_saved="<<privateSaved_<<" decoded_photometry=0 automatic_exposure=0";
 if(videoRet||statsRet){
  failed_=true;
  LOG(CAMSSX1ERear,Error)<<"Statistics/capture stop failed; retain buffers";
  return;
 }
 mappings_.clear();
 if(statisticsAllocated_){
  if(statistics_->releaseBuffers()){failed_=true;return;}
  statisticsAllocated_=false;
 }
 metadata_.clear();
 if(allocated_){
  if(video_->releaseBuffers()){failed_=true;return;}
  allocated_=false;
 }
}
void RearData::fail(const char *why)
{
 failed_=true;
 LOG(CAMSSX1ERear,Error)<<why;
 stop();
}
void RearData::ready(FrameBuffer *buffer)
{
 if(!buffer->request())return;
 if(!running_||buffer->metadata().status!=FrameMetadata::FrameSuccess){
  cancelImage(buffer);return;
 }
 uint32_t sequence=buffer->metadata().sequence;
 if(sequence<joined_||frames_.size()>=16||frames_[sequence].image){
  cancelImage(buffer);fail("Duplicate or unbounded image association");return;
 }
 frames_[sequence].image=buffer;
 finish();
}
void RearData::statisticsReady(FrameBuffer *buffer)
{
 if(!running_)return;
 auto it=mappings_.find(buffer);
 if(it==mappings_.end()||buffer->metadata().status!=FrameMetadata::FrameSuccess||
    buffer->metadata().planes().size()!=1||
    buffer->metadata().planes()[0].bytesused!=NATIVE_REAR_STATS_BYTES){
  fail("Invalid rear statistics buffer completion");return;
 }
 const auto *p=it->second->planes()[0].data();
 uint64_t stream=native_rear_stats_u64(p+8);
 uint32_t sequence=native_rear_stats_u32(p+40);
 uint64_t time=native_rear_stats_u64(p+16);
 if(native_rear_stats_validate(p,NATIVE_REAR_STATS_BYTES,stream,sequence,
                               buffer->metadata().timestamp)||
    buffer->metadata().sequence!=sequence||sequence!=received_||
    (streamId_&&stream!=streamId_)||sequence<joined_||frames_.size()>=16){
  fail("Stale, dropped or malformed rear statistics identity");return;
 }
 auto &frame=frames_[sequence];
 if(frame.meta||frame.validated){fail("Duplicate rear statistics association");return;}
 streamId_=stream;received_++;
 frame.meta=buffer;frame.timestamp=time;
 frame.owner=native_rear_stats_u64(p+24);
 frame.generation=native_rear_stats_u64(p+32);
 if(savePrivateStatistics(sequence,p)){fail("Private rear statistics recording failed");return;}
 ipa_->processStatistics(buffer->cookie(),stream,sequence,time);
}
void RearData::statisticsValidated(uint32_t id,uint64_t stream,uint32_t sequence,
 uint64_t timestamp,int32_t ret,uint64_t owner,uint64_t generation)
{
 if(!running_)return;
 auto it=frames_.find(sequence);
 if(ret||it==frames_.end()||stream!=streamId_){
  fail("Rear IPA rejected statistics envelope");return;
 }
 auto &f=it->second;
 if(!f.meta||f.meta->cookie()!=id||f.validated||f.timestamp!=timestamp||
    owner!=f.owner||generation!=f.generation||(ownerId_&&owner!=ownerId_)){
  fail("Foreign or duplicate rear IPA receipt");return;
 }
 ownerId_=owner;
 FrameBuffer *meta=f.meta;
 f.meta=nullptr;f.validated=true;
 if(statistics_->queueBuffer(meta)){fail("Rear statistics requeue failed");return;}
 finish();
}
void RearData::finish()
{
 for(;;){
  auto it=frames_.find(joined_);
  if(it==frames_.end()||!it->second.image||!it->second.validated)return;
  auto &f=it->second;
  if(f.image->metadata().timestamp/1000!=f.timestamp/1000){
   fail("Image and rear statistics completion timestamps disagree");return;
  }
  FrameBuffer *image=f.image;
  Request *request=image->request();
  if(!request){fail("Image lost its application request");return;}
  frames_.erase(it);
  lastCompleted_=joined_++;
  auto *handler=static_cast<PipelineHandlerCamssX1ERear *>(pipe());
  handler->completeBuffer(request,image);
  handler->completeRequest(request);
 }
}

REGISTER_PIPELINE_HANDLER(PipelineHandlerCamssX1ERear, "camss-x1e-rear")
} /* namespace libcamera */
