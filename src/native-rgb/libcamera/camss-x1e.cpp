/* SPDX-License-Identifier: GPL-2.0-only
 * Experimental SP11 front hardware-ISP pipeline. Fixed manual IQ only.
 * The kernel loads data-only tuning; this handler supplies semantic parameters.
 */
#include <array>
#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <ctime>
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
#include "libcamera/internal/delayed_controls.h"
#include "camss-x1e-controls.h"
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
enum class ControlTimingTrial { None, FrameLength, ExposureGain };
constexpr uint32_t kParams = V4L2_CID_USER_BASE + 0x1243;
uint64_t controlTimingNow()
{
 struct timespec timestamp{};
 if (clock_gettime(CLOCK_MONOTONIC, &timestamp))
  return 0;
 return uint64_t(timestamp.tv_sec) * 1000000000ULL + timestamp.tv_nsec;
}

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
 std::optional<CamssX1EManual> appliedControls;
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
 int start(const ControlList *controls);
 void stop();
 int submitParameters();
 int queueImage(FrameBuffer *buffer);
 int queueApplicationImage(FrameBuffer *buffer);
 int pumpPending();
 int ensureSpare();
 void frameStart(uint32_t sequence);
 int controlTimingStep(uint32_t sequence);
 void imageReady(FrameBuffer *buffer);
 void statisticsReady(FrameBuffer *buffer);
 void meteringReady(uint32_t bufferId, uint64_t stream, uint32_t sequence,
                    uint64_t timestamp, int32_t ret, float luma);
 void tryComplete(uint32_t sequence);
 void fail(const char *reason);
 void cancelImage(FrameBuffer *buffer);

 std::unique_ptr<DelayedControls> delayedControls_;
 CamssX1EControlSchedule controlSchedule_;
 CamssX1EOrderedAdmission<FrameBuffer> pendingRequests_;
 std::map<FrameBuffer *, uint32_t> admittedImages_;
 std::optional<CamssX1EManual> expectedWrite_;
 std::unique_ptr<ipa::camss_x1e::IPAProxyCamssX1E> ipa_;
 bool ipaStarted_ = false;
 bool sofEnabled_ = false;
 ControlTimingTrial controlTimingTrial_ = ControlTimingTrial::None;
 uint32_t nextSofSequence_ = 0;
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
  return cameraData(camera)->start(controls);
 }
 void stopDevice(Camera *camera) override { cameraData(camera)->stop(); }
 int queueRequestDevice(Camera *camera, Request *request) override
 {
  auto *data = cameraData(camera);
  if (!data->running_ || data->failed_)
   return -ESHUTDOWN;
  FrameBuffer *buffer = request->findBuffer(&data->stream_);
  if (!buffer)
   return -ENOENT;
  return data->queueApplicationImage(buffer);
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
 controlInfo_ = ControlInfoMap({
  { &controls::AeEnable, ControlInfo(false, false, false) },
  { &controls::ExposureTimeMode, ControlInfo(controls::ExposureTimeModeManual, controls::ExposureTimeModeManual, controls::ExposureTimeModeManual) },
  { &controls::AnalogueGainMode, ControlInfo(controls::AnalogueGainModeManual, controls::AnalogueGainModeManual, controls::AnalogueGainModeManual) },
  { &controls::ExposureTime, ControlInfo(int32_t(CamssX1EManual::duration(4)), int32_t(CamssX1EManual::duration(7104)), int32_t(CamssX1EManual::duration(1000))) },
  { &controls::AnalogueGain, ControlInfo(1.0f, 16.0f, 1.0f) },
  { &controls::DigitalGain, ControlInfo(1.0f, 15.0f, 1.0f) },
  { &controls::FrameDurationLimits, ControlInfo(CamssX1EManual::duration(3554), CamssX1EManual::duration(7108), CamssX1EManual::duration(3554)) },
 }, controls::controls);
 properties_.set(properties::Model, std::string("IMX681"));
 properties_.set(properties::Location, properties::CameraLocationFront);
 video_->bufferReady.connect(this, &CamssX1ECameraData::imageReady);
 statistics_->bufferReady.connect(this, &CamssX1ECameraData::statisticsReady);
 csid_->frameStart.connect(this, &CamssX1ECameraData::frameStart);
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
 delayedControls_.reset();
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

int CamssX1ECameraData::start(const ControlList *controls)
{
 if (running_ || !startup_.empty() || !metadata_.empty() || pendingRequests_.size())
  return -EBUSY;
 const char *timing = std::getenv("LIBCAMERA_CAMSS_X1E_CONTROL_TIMING");
 controlTimingTrial_ = ControlTimingTrial::None;
 if (timing) {
  if (!std::strcmp(timing, "frame-length-v1"))
   controlTimingTrial_ = ControlTimingTrial::FrameLength;
  else if (!std::strcmp(timing, "exposure-gain-v1"))
   controlTimingTrial_ = ControlTimingTrial::ExposureGain;
  else
   return -EINVAL;
 }
 /* Diagnostic timing runs and standard request scheduling are exclusive. */
 if (controlTimingTrial_ != ControlTimingTrial::None && controls && !controls->empty())
  return -EOPNOTSUPP;
 CamssX1EManual initial;
 if (controls) {
  int ret = camssX1EManualRequest(*controls, initial, &initial);
  if (ret) return ret;
 }
 ControlList initialControls = initial.sensorControls(sensor_->controls());
 int controlRet = sensor_->setControls(&initialControls);
 if (controlRet) return controlRet < 0 ? controlRet : -EINVAL;
 controlSchedule_.reset(initial);
 admittedImages_.clear();
 expectedWrite_.reset();
 if (controlTimingTrial_ == ControlTimingTrial::None) {
  for (uint32_t id : { V4L2_CID_VBLANK, V4L2_CID_EXPOSURE, V4L2_CID_ANALOGUE_GAIN, V4L2_CID_DIGITAL_GAIN })
   if (sensor_->controls().find(id) == sensor_->controls().end()) return -EOPNOTSUPP;
  delayedControls_ = std::make_unique<DelayedControls>(sensor_.get(),
   std::unordered_map<uint32_t, DelayedControls::ControlParams>{
    { V4L2_CID_VBLANK, { 2, false } }, { V4L2_CID_EXPOSURE, { 2, false } },
    { V4L2_CID_ANALOGUE_GAIN, { 2, false } }, { V4L2_CID_DIGITAL_GAIN, { 2, false } },
   });
  auto seed = CamssX1EManual::fromSensor(delayedControls_->get(0));
  if (!seed || !(*seed == initial)) { delayedControls_.reset(); return -EIO; }
 } else delayedControls_.reset();
 nextParameter_ = 5;
 nextSofSequence_ = 0;
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
 ret = csid_->setFrameStartEnabled(true);
 if (ret)
  goto error;
 sofEnabled_ = true;
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
 CamssX1EManual values;
 Request *request = buffer->request();
 ControlList empty(controls::controls);
 const ControlList &requested = request ? request->controls() : empty;
 if (controlTimingTrial_ != ControlTimingTrial::None && !requested.empty()) return -EOPNOTSUPP;
 int ret = controlSchedule_.prepare(requested, &values);
 if (ret) {
  if (request)
   LOG(CAMSSX1E, Debug) << "CAMSS_X1E_ADMISSION_WAIT request=" << request->sequence()
    << " target=" << controlSchedule_.nextImage() << " next_sof=" << nextSofSequence_
    << " error=" << ret;
  return ret;
 }
 const uint32_t target = controlSchedule_.nextImage();
 ret = video_->queueBuffer(buffer);
 if (!ret) {
  pixelsQueued_++;
  admittedImages_.emplace(buffer, target);
  controlSchedule_.admitted(values, !requested.empty());
  if (!requested.empty())
   LOG(CAMSSX1E, Debug) << "CAMSS_X1E_REQUEST_CONTROL request=" << request->sequence()
    << " target=" << target << " fll=" << values.fll << " exposure=" << values.exposure
    << " again=" << values.analogue << " dgain=" << values.digital;
 }
 return ret;
}

int CamssX1ECameraData::queueApplicationImage(FrameBuffer *buffer)
{
 Request *request = buffer->request();
 if (!request) return -EINVAL;
 if (controlTimingTrial_ != ControlTimingTrial::None && !request->controls().empty()) return -EOPNOTSUPP;
 /* Reject invalid controls before acceptance. Valid late controls are retained
  * and converted again against the preceding admitted request at their turn. */
 CamssX1EManual values;
 int ret = controlSchedule_.prepare(request->controls(), &values);
 if (ret && ret != -ETIME) return ret;
 ret = pendingRequests_.push(buffer, stream_.configuration().bufferCount);
 if (ret) return ret;
 ret = pumpPending();
 if (ret) fail("Pending app request admission failed");
 /* Accepted requests are completed or explicitly cancelled by stop(). Returning
  * an error here after fail() would make PipelineHandler cancel twice. */
 return 0;
}

int CamssX1ECameraData::pumpPending()
{
 return pendingRequests_.drain([this](FrameBuffer *buffer) { return queueImage(buffer); },
  [this]() {
   if (availableStartup_.empty()) return -EAGAIN;
   FrameBuffer *buffer = availableStartup_.front();
   availableStartup_.pop_front();
   int ret = queueImage(buffer);
   if (ret) { availableStartup_.push_front(buffer); return ret; }
   LOG(CAMSSX1E, Debug) << "CAMSS_X1E_CONTROL_PAD target=" << controlSchedule_.nextImage()-1
    << " pending=" << pendingRequests_.size() << " queued=" << pixelsQueued_;
   return 0;
  });
}

int CamssX1ECameraData::ensureSpare()
{
 /* The qualified kernel binds N+1 before returning N. A finite application
  * request limit must not prevent retirement of its last image. Keep two
  * outputs admitted, using only fully paired/retired internal buffers when
  * application buffers are unavailable. No application frame is fabricated.
  */
 int pendingRet = pumpPending();
 if (pendingRet) return pendingRet;
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
 auto pending = pendingRequests_.take();
 std::vector<FrameBuffer *> held;
 for (const auto &[sequence, frame] : frames_) {
  (void)sequence;
  if (frame.image)
   held.push_back(frame.image);
 }
 frames_.clear();
 admittedImages_.clear();
 controlSchedule_.reset();
 expectedWrite_.reset();
 delayedControls_.reset();
 /* Pixel STREAMOFF stops hardware before any statistics/storage is released. */
 int ret = videoAllocated_ ? video_->streamOff() : 0;
 int statsRet = statisticsAllocated_ ? statistics_->streamOff() : 0;
 if (sofEnabled_) {
  int eventRet = csid_->setFrameStartEnabled(false);
  if (eventRet)
   LOG(CAMSSX1E, Error) << "Frame-start unsubscribe failed: " << eventRet;
  sofEnabled_ = false;
 }
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
 for (FrameBuffer *buffer : pending)
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

int CamssX1ECameraData::controlTimingStep(uint32_t sequence)
{
 /* Explicit bounded development experiments; no automatic control.
  * All four sensor controls use one normal V4L2 cluster transaction.
  * Every second plateau restores baseline; each field has three up/down cycles.
  */
 const uint32_t last = controlTimingTrial_ == ControlTimingTrial::FrameLength ? 96 : 288;
 if (controlTimingTrial_ == ControlTimingTrial::None ||
     sequence < 16 || sequence > last || sequence % 16)
  return 0;
 const uint32_t step = sequence / 16;
 int32_t vblank = 1394, exposure = 1000, analogue = 0, digital = 256;
 const char *field = "frame-length";
 if (controlTimingTrial_ == ControlTimingTrial::FrameLength) {
  vblank = step % 2 ? 4948 : 1394;
 } else {
  const uint32_t index = (step - 1) / 6;
  if (index == 0) {
   field = "exposure";
   exposure = step % 2 ? 2000 : 1000;
  } else if (index == 1) {
   field = "analogue";
   analogue = step % 2 ? 512 : 0;
  } else {
   field = "digital";
   digital = step % 2 ? 512 : 256;
  }
 }
 ControlList values(sensor_->controls());
 values.set(V4L2_CID_VBLANK, vblank);
 values.set(V4L2_CID_EXPOSURE, exposure);
 values.set(V4L2_CID_ANALOGUE_GAIN, analogue);
 values.set(V4L2_CID_DIGITAL_GAIN, digital);
 const uint64_t begin = controlTimingNow();
 if (!begin)
  return -EIO;
 int ret = sensor_->setControls(&values);
 const uint64_t end = controlTimingNow();
 LOG(CAMSSX1E, Debug) << "CAMSS_X1E_CONTROL_TIMING step=" << step
  << " sof=" << sequence << " begin=" << begin << " end=" << end
  << " fll=" << vblank + 2160 << " exposure=" << exposure
  << " again=" << analogue << " dgain=" << digital << " error=" << ret << " field=" << field;
 return ret ? (ret < 0 ? ret : -EINVAL) : (!end || end < begin ? -EIO : 0);
}

void CamssX1ECameraData::frameStart(uint32_t sequence)
{
 if (!running_)
  return;
 if (sequence != nextSofSequence_ ||
     nextSofSequence_ == std::numeric_limits<uint32_t>::max()) {
  fail("Native frame-start sequence discontinuity");
  return;
 }
 nextSofSequence_++;
 LOG(CAMSSX1E, Debug) << "CAMSS_X1E_SOF frame=" << sequence;
 if (controlTimingStep(sequence)) {
  fail("Grouped sensor control timing experiment failed");
  return;
 }
 if (delayedControls_) {
  std::optional<CamssX1EManual> upcoming;
  if (controlSchedule_.frameStart(sequence, &upcoming)) {
   fail("Request control schedule discontinuity"); return;
  }
  delayedControls_->applyControls(sequence);
  /* Upstream applyControls() is void. Cached V4L2 readback must match after
   * each queued write; the diagnostic CCI trace independently checks hardware.
   * Do not claim that this ioctl reads the physical registers itself. */
  if (expectedWrite_) {
   const std::array<uint32_t, 4> ids{ V4L2_CID_VBLANK, V4L2_CID_EXPOSURE, V4L2_CID_ANALOGUE_GAIN, V4L2_CID_DIGITAL_GAIN };
   auto observed = CamssX1EManual::fromSensor(sensor_->getControls(ids));
   if (!observed || !(*observed == *expectedWrite_)) {
    fail("Delayed sensor write/readback mismatch"); return;
   }
   LOG(CAMSSX1E, Debug) << "CAMSS_X1E_DELAYED_WRITE sof=" << sequence
    << " effective=" << sequence + 2 << " fll=" << observed->fll
    << " exposure=" << observed->exposure << " again=" << observed->analogue
    << " dgain=" << observed->digital << " cache_match=1";
  }
  auto applied = CamssX1EManual::fromSensor(delayedControls_->get(sequence));
  if (!applied || frames_.size() > 16) {
   fail("Applied control identity unavailable"); return;
  }
  frames_[sequence].appliedControls = *applied;
  expectedWrite_ = upcoming;
  ControlList queued = upcoming ? upcoming->sensorControls(sensor_->controls()) : ControlList(sensor_->controls());
  if (!delayedControls_->push(queued)) {
   fail("Delayed control queue rejected"); return;
  }
  tryComplete(sequence);
 }
 /* Receiver SOF is not first-row sensor exposure or BOOTTIME. SensorTimestamp
  * stays absent. AE/AWB policy remains disabled until metering is calibrated. */
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
 auto admission = admittedImages_.find(buffer);
 if (admission == admittedImages_.end() || admission->second != sequence) {
  cancelImage(buffer); fail("Output admission/frame identity mismatch"); return;
 }
 admittedImages_.erase(admission);
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
 if (it == frames_.end() || !it->second.image || !it->second.stats || !it->second.luma ||
     (delayedControls_ && !it->second.appliedControls))
  return;
 FrameBuffer *image = it->second.image;
 StatsIdentity stats = *it->second.stats;
 auto applied = it->second.appliedControls;
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
 if (applied) {
  applied->metadata(request->_d()->metadata());
  LOG(CAMSSX1E, Debug) << "CAMSS_X1E_APPLIED_CONTROL request=" << request->sequence()
   << " frame=" << sequence << " fll=" << applied->fll << " exposure=" << applied->exposure
   << " again=" << applied->analogue << " dgain=" << applied->digital;
 }
 auto *handler = static_cast<PipelineHandlerCamssX1E *>(pipe());
 handler->completeBuffer(request, image);
 handler->completeRequest(request);
}

REGISTER_PIPELINE_HANDLER(PipelineHandlerCamssX1E, "camss-x1e")
} /* namespace libcamera */
