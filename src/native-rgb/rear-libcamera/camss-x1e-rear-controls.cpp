/* SPDX-License-Identifier: GPL-2.0-only */
/* SP11 rear public-request transport qualification.
 * Continuous hardware ISP with bounded manual exposure/gain qualification.
 * Automatic IPA and per-frame sensor exposure timestamps are not implemented.
 * No CPU image mapping, software ISP, sensor group-hold or fictitious metadata.
 */
#include <array>
#include <chrono>
#include "rear-manual-controls.h"
#include <cerrno>
#include <memory>
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
  if (data->running_ || data->allocated_)
   return -EBUSY;
  int ret = data->video_->importBuffers(data->stream_.configuration().bufferCount);
  if (ret)
   return ret;
  data->allocated_ = true;
  /* The driver requires two queued buffers before hardware start, so empty
   * STREAMON arms the queue; ordinary camera requests supply those buffers.
   */
  ret = data->video_->streamOn();
  if (ret) {
   data->video_->releaseBuffers();
   data->allocated_ = false;
   return ret;
  }
  data->admitted_ = 0;
  data->lastCompleted_ = -1;
  data->running_ = true;
  return 0;
 }
 void stopDevice(Camera *camera) override
 {
  auto *data = cameraData(camera);
  data->running_ = false;
  int ret = data->video_->streamOff();
  if (ret)
   LOG(CAMSSX1ERear, Error) << "Rear STREAMOFF failed: " << ret;
  if (data->allocated_) {
   ret = data->video_->releaseBuffers();
   if (ret)
    LOG(CAMSSX1ERear, Error) << "Rear buffer release failed: " << ret;
   else
    data->allocated_ = false;
  }
 }
 int queueRequestDevice(Camera *camera, Request *request) override
 {
  auto *data = cameraData(camera);
  if (!data->running_)
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
  for (const char *name : { "msm_csiphy1", "msm_csid1", "msm_vfe1_pix" })
   match.add(name);
  auto media = acquireMediaDevice(enumerator, match);
  if (!media)
   return false;
  auto data = std::make_unique<RearData>(this, media);
  if (data->init())
   return false;
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
 if (ret)
  close();
 return ret;
}
void RearData::close()
{
 if (video_)
  video_->close();
 for (auto *device : { sensor_.get(), phy_.get(), csid_.get(), vfe_.get() })
  if (device)
   device->close();
}
int RearData::configure()
{
 if (running_ || allocated_)
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

void RearData::ready(FrameBuffer *buffer)
{
 auto *request = buffer->request();
 if (!request) {
  LOG(CAMSSX1ERear, Error) << "Capture completed without its application request";
  return;
 }
 auto *handler = static_cast<PipelineHandlerCamssX1ERear *>(pipe());
 /* The driver reports completion-time CLOCK_MONOTONIC, not exposure start.
  * Do not fabricate the SensorTimestamp control.
  */
 lastCompleted_ = buffer->metadata().sequence;
 handler->completeBuffer(request, buffer);
 handler->completeRequest(request);
}
REGISTER_PIPELINE_HANDLER(PipelineHandlerCamssX1ERear, "camss-x1e-rear")
} /* namespace libcamera */
