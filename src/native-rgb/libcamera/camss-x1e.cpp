/* SPDX-License-Identifier: GPL-2.0-only
 * Experimental SP11 front hardware-ISP pipeline. Fixed manual IQ only.
 * The kernel loads data-only tuning; this handler supplies semantic parameters.
 */
#include <array>
#include <cerrno>
#include <cstdint>
#include <cmath>
#include <deque>
#include <limits>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <vector>

#include <linux/media-bus-format.h>

#include <libcamera/base/log.h>
#include <libcamera/base/span.h>
#include <libcamera/camera.h>
#include <libcamera/control_ids.h>
#include <libcamera/formats.h>
#include <libcamera/framebuffer.h>
#include <libcamera/property_ids.h>
#include <libcamera/ipa/camss_x1e_ipa_interface.h>
#include <libcamera/ipa/camss_x1e_ipa_proxy.h>
#include <libcamera/request.h>
#include <libcamera/stream.h>

#include "libcamera/internal/camera.h"
#include "libcamera/internal/device_enumerator.h"
#include "libcamera/internal/framebuffer.h"
#include "libcamera/internal/mapped_framebuffer.h"
#include "libcamera/internal/ipa_manager.h"
#include "libcamera/internal/media_device.h"
#include "libcamera/internal/pipeline_handler.h"
#include "libcamera/internal/request.h"
#include "libcamera/internal/v4l2_subdevice.h"
#include "libcamera/internal/v4l2_videodevice.h"

extern "C" {
#include "native-front-params.h"
#include "native-front-stats.h"
}

namespace libcamera {
LOG_DEFINE_CATEGORY(CAMSSX1E)

namespace {
constexpr Size kOutput{ 2560, 1440 };
constexpr Size kInput{ 3840, 2160 };
constexpr unsigned int kStartup = 4;
constexpr unsigned int kMetadataBuffers = 8;
constexpr uint32_t kParams = V4L2_CID_USER_BASE + 0x1243;
constexpr uint32_t kRawCommands = V4L2_CID_USER_BASE + 0x1240;

struct StatsIdentity {
 uint64_t stream;
 uint64_t timestamp;
 uint32_t source;
};
struct FrameState {
 FrameBuffer *image = nullptr;
 std::optional<StatsIdentity> stats;
 FrameBuffer *metadata = nullptr;
 std::optional<float> luma;
};
}

class PipelineHandlerCamssX1E;

class CamssX1ECameraData final : public Camera::Private
{
public:
 CamssX1ECameraData(PipelineHandler *pipe, std::shared_ptr<MediaDevice> media)
  : Camera::Private(pipe), media_(std::move(media)) {}
 int init();
 int openDevices();
 void closeDevices();
 int configure();
 int start();
 void stop();
 int submitParameters();
 int queueImage(FrameBuffer *buffer);
 int ensureSpare();
 void imageReady(FrameBuffer *buffer);
 void statisticsReady(FrameBuffer *buffer);
 void meteringReady(uint32_t bufferId, uint64_t stream, uint32_t sequence,
                    uint64_t timestamp, int32_t ret, float luma);
 void tryComplete(uint32_t sequence);
 void fail(const char *reason);
 void cancelImage(FrameBuffer *buffer);

 std::unique_ptr<ipa::camss_x1e::IPAProxyCamssX1E> ipa_;
 bool ipaStarted_ = false;
 std::vector<uint32_t> ipaBufferIds_;
 std::shared_ptr<MediaDevice> media_;
 std::unique_ptr<V4L2Subdevice> sensor_, phy_, csid_, vfe_;
 std::unique_ptr<V4L2VideoDevice> video_, statistics_;
 std::string sensorName_;
 Stream stream_;
 bool running_ = false;
 bool failed_ = false;
 bool videoAllocated_ = false, statisticsAllocated_ = false;
 uint64_t nextParameter_ = 5;
 uint64_t streamId_ = 0;
 unsigned int pixelsQueued_ = 0;
 std::deque<FrameBuffer *> availableStartup_;
 std::map<uint32_t, FrameState> frames_;
 std::vector<std::unique_ptr<FrameBuffer>> startup_, metadata_;
 std::map<FrameBuffer *, std::unique_ptr<MappedFrameBuffer>> mappings_;
};

class CamssX1ECameraConfiguration final : public CameraConfiguration
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
  StreamConfiguration &cfg = config_[0];
  if (cfg.pixelFormat != formats::NV12 || cfg.size != kOutput ||
      cfg.bufferCount != 4) {
   cfg.pixelFormat = formats::NV12;
   cfg.size = kOutput;
   cfg.bufferCount = 4;
   status = Adjusted;
  }
  cfg.stride = 2560;
  cfg.frameSize = 5529600;
  return status;
 }
};

class PipelineHandlerCamssX1E final : public PipelineHandler
{
public:
 PipelineHandlerCamssX1E(CameraManager *manager) : PipelineHandler(manager) {}
 std::unique_ptr<CameraConfiguration> generateConfiguration(Camera *, Span<const StreamRole> roles) override
 {
  auto config = std::make_unique<CamssX1ECameraConfiguration>();
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
  if (controls && !controls->empty())
   return -EOPNOTSUPP; /* No unqualified automatic/manual control is advertised. */
  return cameraData(camera)->start();
 }
 void stopDevice(Camera *camera) override { cameraData(camera)->stop(); }
 int queueRequestDevice(Camera *camera, Request *request) override
 {
  auto *data = cameraData(camera);
  if (!data->running_ || data->failed_)
   return -ESHUTDOWN;
  if (!request->controls().empty())
   return -EOPNOTSUPP;
  FrameBuffer *buffer = request->findBuffer(&data->stream_);
  if (!buffer)
   return -ENOENT;
  return data->queueImage(buffer);
 }
 bool match(DeviceEnumerator *enumerator) override
 {
  DeviceMatch match("qcom-camss");
  for (const char *name : { "msm_csiphy2", "msm_csid1", "msm_vfe1_pix", "msm_vfe1_stats" })
   match.add(name);
  auto media = acquireMediaDevice(enumerator, match);
  if (!media)
   return false;
  auto data = std::make_unique<CamssX1ECameraData>(this, media);
  if (data->init())
   return false;
  data->ipa_ = IPAManager::createIPA<ipa::camss_x1e::IPAProxyCamssX1E>(this, 0, 0);
  if (!data->ipa_)
   return false;
  data->ipa_->statisticsProcessed.connect(data.get(), &CamssX1ECameraData::meteringReady);
  IPASettings settings{};
  settings.sensorModel = "imx681";
  if (data->ipa_->init(settings))
   return false;
  std::set<Stream *> streams{ &data->stream_ };
  auto camera = Camera::create(std::move(data), "sp11-front-imx681", streams);
  registerCamera(std::move(camera));
  return true;
 }
private:
 bool acquireDevice(Camera *camera) override { return cameraData(camera)->openDevices() == 0; }
 void releaseDevice(Camera *camera) override
 {
  auto *data = cameraData(camera);
  data->closeDevices();
  if (data->media_->disableLinks())
   LOG(CAMSSX1E, Error) << "Could not restore neutral media links";
 }
 CamssX1ECameraData *cameraData(Camera *camera)
 {
  return static_cast<CamssX1ECameraData *>(camera->_d());
 }
};

int CamssX1ECameraData::init()
{
 MediaEntity *sensor = nullptr;
 for (MediaEntity *entity : media_->entities()) {
  if (entity->function() == MEDIA_ENT_F_CAM_SENSOR &&
      entity->name().compare(0, 7, "imx681 ") == 0) {
   if (sensor)
    return -ENODEV;
   sensor = entity;
  }
 }
 if (!sensor)
  return -ENODEV;
 sensorName_ = sensor->name();
 sensor_ = std::make_unique<V4L2Subdevice>(sensor);
 phy_ = V4L2Subdevice::fromEntityName(media_.get(), "msm_csiphy2");
 csid_ = V4L2Subdevice::fromEntityName(media_.get(), "msm_csid1");
 vfe_ = V4L2Subdevice::fromEntityName(media_.get(), "msm_vfe1_pix");
 statistics_ = V4L2VideoDevice::fromEntityName(media_.get(), "msm_vfe1_stats");
 MediaEntity *pixel = media_->getEntityByName("msm_vfe1_pix");
 if (!phy_ || !csid_ || !vfe_ || !statistics_ || !pixel)
  return -ENODEV;
 /* Find the immutable pixel sink by type. The first remote is the metadata
  * sink on the qualified graph, so an untyped first-link lookup is incorrect.
  */
 const MediaEntity *output = nullptr;
 for (const MediaPad *pad : pixel->pads()) {
  if (!(pad->flags() & MEDIA_PAD_FL_SOURCE))
   continue;
  for (const MediaLink *link : pad->links()) {
   const MediaEntity *sink = link->sink()->entity();
   if (sink->type() == MediaEntity::Type::V4L2VideoDevice &&
       sink->name() != "msm_vfe1_stats") {
    if (output)
     return -ENODEV;
    output = sink;
   }
  }
 }
 if (!output)
  return -ENODEV;
 video_ = std::make_unique<V4L2VideoDevice>(output);
 int ret = openDevices();
 if (ret)
  return ret;
 if (!video_->controlInfo(kParams) || video_->controlInfo(kRawCommands) ||
     !statistics_->caps().isMetaCapture())
  return -EOPNOTSUPP; /* Match only the qualified data-only driver mode. */
 V4L2DeviceFormat metadata;
 ret = statistics_->getFormat(&metadata);
 if (ret || metadata.fourcc != V4L2PixelFormat(NATIVE_FRONT_STATS_MAGIC) ||
     metadata.planes[0].size != NATIVE_FRONT_STATS_BYTES)
  return ret ? ret : -EINVAL;
 controlInfo_ = ControlInfoMap({}, controls::controls);
 properties_.set(properties::Model, std::string("IMX681"));
 properties_.set(properties::Location, properties::CameraLocationFront);
 video_->bufferReady.connect(this, &CamssX1ECameraData::imageReady);
 statistics_->bufferReady.connect(this, &CamssX1ECameraData::statisticsReady);
 closeDevices();
 return 0;
}

int CamssX1ECameraData::openDevices()
{
 for (V4L2Subdevice *device : { sensor_.get(), phy_.get(), csid_.get(), vfe_.get() }) {
  int ret = device->open();
  if (ret) {
   closeDevices();
   return ret;
  }
 }
 int ret = video_->open();
 if (!ret)
  ret = statistics_->open();
 if (ret)
  closeDevices();
 return ret;
}

void CamssX1ECameraData::closeDevices()
{
 statistics_->close();
 video_->close();
 for (V4L2Subdevice *device : { sensor_.get(), phy_.get(), csid_.get(), vfe_.get() })
  device->close();
}

int CamssX1ECameraData::configure()
{
 if (running_)
  return -EBUSY;
 int ret = media_->disableLinks();
 if (ret)
  return ret;
 const std::array<std::pair<MediaEntity *, MediaEntity *>, 2> edges{
      std::make_pair(media_->getEntityByName("msm_csiphy2"), media_->getEntityByName("msm_csid1")),
      std::make_pair(media_->getEntityByName("msm_csid1"), media_->getEntityByName("msm_vfe1_pix")) };
 for (const auto &edge : edges) {
  unsigned int source = edge.first->name() == "msm_csiphy2" ? 1 : 4;
  MediaLink *link = media_->link(edge.first, source, edge.second, 0);
  if (!link)
   return -ENODEV;
  ret = link->setEnabled(true);
  if (ret)
   return ret;
 }
 V4L2SubdeviceFormat raw{};
 raw.code = MEDIA_BUS_FMT_SRGGB10_1X10;
 raw.size = kInput;
 ret = sensor_->setFormat(0, &raw);
 if (ret || raw.size != kInput || raw.code != MEDIA_BUS_FMT_SRGGB10_1X10)
  return ret ? ret : -EINVAL;
 for (auto [device, pad] : std::array<std::pair<V4L2Subdevice *, unsigned int>, 5>{
      std::make_pair(phy_.get(), 0), std::make_pair(phy_.get(), 1),
      std::make_pair(csid_.get(), 0), std::make_pair(csid_.get(), 4),
      std::make_pair(vfe_.get(), 0) }) {
  ret = device->setFormat(pad, &raw);
  if (ret || raw.size != kInput || raw.code != MEDIA_BUS_FMT_SRGGB10_1X10)
   return ret ? ret : -EINVAL;
 }
 Rectangle compose(kOutput), crop(kOutput);
 ret = vfe_->setSelection(0, V4L2_SEL_TGT_COMPOSE, &compose);
 if (ret || compose != Rectangle(kOutput))
  return ret ? ret : -EINVAL;
 ret = vfe_->setSelection(1, V4L2_SEL_TGT_CROP, &crop);
 if (ret || crop != Rectangle(kOutput))
  return ret ? ret : -EINVAL;
 V4L2DeviceFormat format{};
 format.fourcc = V4L2PixelFormat(V4L2_PIX_FMT_NV12);
 format.size = kOutput;
 ret = video_->setFormat(&format);
 if (ret || format.size != kOutput || format.fourcc != V4L2PixelFormat(V4L2_PIX_FMT_NV12) ||
     format.planesCount != 1 || format.planes[0].bpl != 2560 || format.planes[0].size != 5529600)
  return ret ? ret : -EINVAL;
 ControlList sensorControls(sensor_->controls());
 sensorControls.set(V4L2_CID_VBLANK, int32_t(1394));
 sensorControls.set(V4L2_CID_EXPOSURE, int32_t(1000));
 sensorControls.set(V4L2_CID_ANALOGUE_GAIN, int32_t(0));
 sensorControls.set(V4L2_CID_DIGITAL_GAIN, int32_t(256));
 ret = sensor_->setControls(&sensorControls);
 return ret ? (ret < 0 ? ret : -EINVAL) : 0;
}

int CamssX1ECameraData::submitParameters()
{
 if (nextParameter_ > std::numeric_limits<uint32_t>::max())
  return -EOVERFLOW;
 std::vector<uint8_t> packet;
 int ret = ipa_->computeParameters(nextParameter_, &packet);
 if (ret)
  return ret;
 ret = native_front_params_validate(packet.data(), packet.size());
 if (ret || native_front_stats_u64(packet.data() + 8) != nextParameter_)
  return ret ? ret : -ESTALE;
 ControlList parameters(video_->controls());
 parameters.set(kParams, ControlValue(Span<const uint8_t>(packet)));
 ret = video_->setControls(&parameters);
 if (!ret)
  nextParameter_++;
 return ret ? (ret < 0 ? ret : -EINVAL) : 0;
}

int CamssX1ECameraData::start()
{
 if (running_ || !startup_.empty() || !metadata_.empty())
  return -EBUSY;
 nextParameter_ = 5;
 streamId_ = 0;
 pixelsQueued_ = 0;
 availableStartup_.clear();
 failed_ = false;
 frames_.clear();
 std::vector<IPABuffer> ipaBuffers;
 uint32_t bufferId = 0;
 int ret = video_->exportBuffers(kStartup, &startup_);
 if (ret != int(kStartup)) {
  startup_.clear();
  return ret < 0 ? ret : -ENOMEM;
 }
 ret = video_->importBuffers(kStartup + stream_.configuration().bufferCount);
 if (ret)
  goto error;
 videoAllocated_ = true;
 ret = statistics_->allocateBuffers(kMetadataBuffers, &metadata_);
 if (ret != int(kMetadataBuffers)) {
  ret = ret < 0 ? ret : -ENOMEM;
  goto error;
 }
 statisticsAllocated_ = true;
 for (const auto &buffer : metadata_) {
  buffer->setCookie(++bufferId);
  const auto &planes = buffer->planes();
  ipaBuffers.emplace_back(buffer->cookie(),
                          std::vector<FrameBuffer::Plane>{ planes.begin(), planes.end() });
  auto map = std::make_unique<MappedFrameBuffer>(buffer.get(), MappedFrameBuffer::MapFlag::Read);
  if (!map->isValid()) {
   ret = map->error();
   goto error;
  }
  mappings_.emplace(buffer.get(), std::move(map));
 }
 ret = ipa_->mapBuffers(ipaBuffers);
 if (ret)
  goto error;
 for (const IPABuffer &buffer : ipaBuffers)
  ipaBufferIds_.push_back(buffer.id);
 ret = ipa_->start();
 if (ret)
  goto error;
 ipaStarted_ = true;
 for (const auto &buffer : metadata_) {
  ret = statistics_->queueBuffer(buffer.get());
  if (ret)
   goto error;
 }
 for (const auto &buffer : startup_) {
  ret = queueImage(buffer.get());
  if (ret)
   goto error;
 }
 for (unsigned int i = 0; i < kStartup; i++) {
  ret = submitParameters();
  if (ret)
   goto error;
 }
 ret = statistics_->streamOn();
 if (ret)
  goto error;
 running_ = true;
 ret = video_->streamOn();
 if (ret)
  goto error;
 return 0;
error:
 stop();
 return ret;
}

int CamssX1ECameraData::queueImage(FrameBuffer *buffer)
{
 int ret = video_->queueBuffer(buffer);
 if (!ret)
  pixelsQueued_++;
 return ret;
}

int CamssX1ECameraData::ensureSpare()
{
 /* The qualified kernel binds N+1 before returning N. A finite application
  * request limit must not prevent retirement of its last image. Keep two
  * outputs admitted, using only fully paired/retired internal buffers when
  * application buffers are unavailable. No application frame is fabricated.
  */
 while (running_ && pixelsQueued_ < 2 && !availableStartup_.empty()) {
  FrameBuffer *buffer = availableStartup_.front();
  availableStartup_.pop_front();
  int ret = queueImage(buffer);
  if (ret) {
   availableStartup_.push_front(buffer);
   return ret;
  }
  LOG(CAMSSX1E, Debug) << "CAMSS_X1E_SPARE queued=" << pixelsQueued_;
 }
 return 0;
}

void CamssX1ECameraData::cancelImage(FrameBuffer *buffer)
{
 Request *request = buffer->request();
 if (!request)
  return;
 buffer->_d()->cancel();
 auto *handler = static_cast<PipelineHandlerCamssX1E *>(pipe());
 handler->completeBuffer(request, buffer);
 handler->completeRequest(request);
}

void CamssX1ECameraData::stop()
{
 running_ = false;
 availableStartup_.clear();
 std::vector<FrameBuffer *> held;
 for (const auto &[sequence, frame] : frames_) {
  (void)sequence;
  if (frame.image)
   held.push_back(frame.image);
 }
 frames_.clear();
 /* Pixel STREAMOFF stops hardware before any statistics/storage is released. */
 int ret = videoAllocated_ ? video_->streamOff() : 0;
 int statsRet = statisticsAllocated_ ? statistics_->streamOff() : 0;
 /* stop() is a synchronous IPA barrier: no shared mapping is released while
  * an asynchronous statistics invocation can still be reading it. */
 if (ipaStarted_) {
  ipa_->stop();
  ipaStarted_ = false;
 }
 if (!ipaBufferIds_.empty()) {
  ipa_->unmapBuffers(ipaBufferIds_);
  ipaBufferIds_.clear();
 }
 for (FrameBuffer *buffer : held)
  cancelImage(buffer);
 if (ret || statsRet) {
  failed_ = true;
  LOG(CAMSSX1E, Error) << "Capture stop failed; retain internal buffers until device close";
  return;
 }
 mappings_.clear();
 if (statisticsAllocated_) {
  statistics_->releaseBuffers();
  statisticsAllocated_ = false;
 }
 metadata_.clear();
 if (videoAllocated_) {
  video_->releaseBuffers();
  videoAllocated_ = false;
 }
 startup_.clear();
 pixelsQueued_ = 0;
}

void CamssX1ECameraData::fail(const char *reason)
{
 if (!failed_) {
  failed_ = true;
  LOG(CAMSSX1E, Error) << reason;
 }
 stop();
}

void CamssX1ECameraData::imageReady(FrameBuffer *buffer)
{
 if (pixelsQueued_)
  pixelsQueued_--;
 if (!running_ || buffer->metadata().status != FrameMetadata::FrameSuccess) {
  cancelImage(buffer);
  if (running_)
   fail("Processed image failed");
  return;
 }
 uint32_t sequence = buffer->metadata().sequence;
 FrameState &frame = frames_[sequence];
 if (frame.image || frames_.size() > 16) {
  cancelImage(buffer);
  fail("Duplicate or unpaired processed image");
  return;
 }
 frame.image = buffer;
 /* Replenish the bounded semantic FIFO once per hardware video completion. */
 if (ensureSpare()) {
  fail("Internal spare output admission failed");
  return;
 }
 if (submitParameters()) {
  fail("Typed parameter queue rejected");
  return;
 }
 tryComplete(sequence);
}

void CamssX1ECameraData::statisticsReady(FrameBuffer *buffer)
{
 if (!running_)
  return;
 auto it = mappings_.find(buffer);
 if (buffer->metadata().status != FrameMetadata::FrameSuccess || it == mappings_.end() ||
     buffer->metadata().planes().size() != 1 ||
     buffer->metadata().planes()[0].bytesused != NATIVE_FRONT_STATS_BYTES) {
  fail("Statistics capture failed");
  return;
 }
 const auto &planes = it->second->planes();
 if (planes.size() != 1 || planes[0].size() < NATIVE_FRONT_STATS_BYTES) {
  fail("Statistics storage is invalid");
  return;
 }
 const uint8_t *data = planes[0].data();
 uint32_t sequence = native_front_stats_u32(data+24);
 uint64_t stream = native_front_stats_u64(data+8);
 if (!streamId_)
  streamId_ = stream;
 if (native_front_stats_validate(data, NATIVE_FRONT_STATS_BYTES, streamId_, sequence) ||
     sequence == std::numeric_limits<uint32_t>::max() ||
     native_front_stats_u32(data+28) != sequence+1) {
  fail("Statistics identity or continuity rejected");
  return;
 }
 FrameState &frame = frames_[sequence];
 if (frame.stats || frames_.size() > 16) {
  fail("Duplicate or unpaired statistics");
  return;
 }
 frame.stats = StatsIdentity{ stream, native_front_stats_u64(data+16),
                               native_front_stats_u32(data+28) };
 frame.metadata = buffer;
 /* Hold this kernel buffer until the matching IPA result arrives. The IPA
  * receives an ID for its read-only shared mapping, never a CPU pixel image. */
 ipa_->processStatistics(buffer->cookie(), stream, sequence, frame.stats->timestamp);
}

void CamssX1ECameraData::meteringReady(uint32_t bufferId, uint64_t stream,
                                      uint32_t sequence, uint64_t timestamp,
                                      int32_t ret, float luma)
{
 auto it = frames_.find(sequence);
 if (!running_ || it == frames_.end() || !it->second.stats)
  return;
 FrameState &frame = it->second;
 /* A queued callback from a stopped stream must not complete a new frame. */
 if (frame.stats->stream != stream || frame.stats->timestamp != timestamp)
  return;
 if (!frame.metadata || frame.metadata->cookie() != bufferId || frame.luma ||
     ret || !std::isfinite(luma) || luma < 0.0f) {
  fail("IPA metering result rejected");
  return;
 }
 FrameBuffer *buffer = frame.metadata;
 frame.luma = luma;
 frame.metadata = nullptr;
 LOG(CAMSSX1E, Debug) << "CAMSS_X1E_IPA_METER frame=" << sequence
                     << " stream=" << stream << " timestamp=" << timestamp
                     << " luma=" << luma;
 /* Requeue only after the IPA has finished reading this exact buffer. */
 if (statistics_->queueBuffer(buffer)) {
  fail("Statistics requeue after IPA failed");
  return;
 }
 tryComplete(sequence);
}

void CamssX1ECameraData::tryComplete(uint32_t sequence)
{
 auto it = frames_.find(sequence);
 if (it == frames_.end() || !it->second.image || !it->second.stats || !it->second.luma)
  return;
 FrameBuffer *image = it->second.image;
 StatsIdentity stats = *it->second.stats;
 if (stats.timestamp / 1000 * 1000 != image->metadata().timestamp) {
  fail("Video and statistics timestamps differ");
  return;
 }
 frames_.erase(it);
 Request *request = image->request();
 if (!request) {
  availableStartup_.push_back(image);
  if (ensureSpare())
   fail("Retired internal output requeue failed");
  return; /* Internal startup/spare frames never escape to an app. */
 }
 /* Buffer-return time is sufficient for pair identity, but is not the
  * first-row exposure/CLOCK_BOOTTIME time required by SensorTimestamp.
  * Do not publish that control until source-qualified sensor timing exists.
  */
 LOG(CAMSSX1E, Debug) << "CAMSS_X1E_PAIR request=" << request->sequence()
                     << " frame=" << sequence << " source=" << stats.source
                     << " stream=" << stats.stream << " timestamp_match=1";
 auto *handler = static_cast<PipelineHandlerCamssX1E *>(pipe());
 handler->completeBuffer(request, image);
 handler->completeRequest(request);
}

REGISTER_PIPELINE_HANDLER(PipelineHandlerCamssX1E, "camss-x1e")
} /* namespace libcamera */
