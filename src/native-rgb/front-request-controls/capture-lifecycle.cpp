/* SPDX-License-Identifier: GPL-2.0-only */
/* Hardware qualification only: real public libcamera API, no pixel processing. */
#include <algorithm>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <iostream>
#include <filesystem>
#include <fstream>
#include <thread>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <vector>
#include <libcamera/camera.h>
#include <libcamera/camera_manager.h>
#include <libcamera/control_ids.h>
#include <libcamera/formats.h>
#include <libcamera/framebuffer_allocator.h>
#include <libcamera/request.h>

using namespace libcamera;

class Lifecycle
{
public:
 explicit Lifecycle(std::shared_ptr<Camera> camera) : camera_(std::move(camera))
 {
  camera_->requestCompleted.connect(this, &Lifecycle::complete);
 }
 ~Lifecycle()
 {
  std::cerr << "LC_STAGE destructor_begin" << std::endl;
  if (running_)
   camera_->stop();
  camera_->requestCompleted.disconnect(this);
  requests_.clear();
  allocator_.reset();
  if (acquired_)
   camera_->release();
  std::cerr << "LC_STAGE destructor_end" << std::endl;
 }
 void acquireAndConfigure()
 {
  check(camera_->acquire() == 0, "acquire");
  acquired_ = true;
  configuration_ = camera_->generateConfiguration({ StreamRole::Viewfinder });
  check(configuration_ && configuration_->size() == 1, "configuration");
  auto &cfg = configuration_->at(0);
  check(cfg.pixelFormat == formats::NV12 && cfg.size == Size(2560,1440) &&
        cfg.bufferCount == 4 && cfg.stride == 2560 && cfg.frameSize == 5529600,
        "qualified configuration");
  check(camera_->configure(configuration_.get()) == 0, "configure");
  stream_ = cfg.stream();
  allocator_ = std::make_unique<FrameBufferAllocator>(camera_);
  check(allocator_->allocate(stream_) == 4, "allocate four application buffers");
 }
 void release()
 {
  requests_.clear();
  allocator_.reset();
  configuration_.reset();
  std::cerr << "LC_STAGE release_begin" << std::endl;
  check(camera_->release() == 0, "release");
  std::cerr << "LC_STAGE release_end" << std::endl;
  acquired_ = false;
 }
 void capture(unsigned int round, unsigned int limit)
 {
  requests_.clear();
  completed_ = queued_ = 0;
  limit_ = limit;
  failure_.clear();
  frames_.clear();
  const auto &buffers = allocator_->buffers(stream_);
  for (unsigned int i=0; i<std::min<unsigned int>(limit, buffers.size()); ++i) {
   auto request = camera_->createRequest(i);
   check(request && request->addBuffer(stream_, buffers[i].get()) == 0,
         "create real application request");
   requests_.push_back(std::move(request));
  }
  ControlList initial(controls::controls);
  if (!round) {
   initial.set(controls::ExposureTime, int32_t(18756));
   initial.set(controls::AnalogueGain, 2.0f);
   initial.set(controls::DigitalGain, 2.0f);
  }
  expectedExposure_ = round ? 9378 : 18756;
  expectedGain_ = round ? 1.0f : 2.0f;
  check(camera_->start(&initial) == 0, "start controls/default reset");
  running_ = true;
  /* Hold the same mutex as completion so admission count cannot race callback. */
  {
   std::unique_lock lock(mutex_);
   for (const auto &request : requests_) {
    check(camera_->queueRequest(request.get()) == 0, "initial request admission");
    queued_++;
   }
   bool done = ready_.wait_for(lock, std::chrono::seconds(15),
                              [&] { return completed_ == limit_ || !failure_.empty(); });
   if (!done)
    failure_ = "finite capture timeout";
  }
  std::cerr << "LC_STAGE round=" << round << " stop_begin" << std::endl;
  check(camera_->stop() == 0, "stop");
  std::cerr << "LC_STAGE round=" << round << " stop_end" << std::endl;
  running_ = false;
  checkSensorStandby();
  std::unique_lock lock(mutex_);
  check(failure_.empty(), failure_);
  check(completed_ == limit && queued_ == limit, "exact finite application count");
  std::cout << "LIFECYCLE_ROUND {\"round\":" << round << ",\"frames\":" << completed_
            << ",\"same_camera\":true,\"sequences\":[";
  for (size_t i=0; i<frames_.size(); ++i)
   std::cout << (i ? "," : "") << frames_[i].first;
  std::cout << "],\"timestamps_ns\":[";
  for (size_t i=0; i<frames_.size(); ++i)
   std::cout << (i ? "," : "") << frames_[i].second;
  std::cout << "],\"clean_stop\":true,\"all_sensors_suspended\":true}" << std::endl;
 }
private:
 static void checkSensorStandby()
 {
  std::vector<std::filesystem::path> sensors;
  for (const auto &device : std::filesystem::directory_iterator("/sys/bus/i2c/devices")) {
   std::ifstream compatible(device.path() / "of_node/compatible");
   std::string name;
   std::getline(compatible, name, '\0');
   if (name == "sony,imx681" || name == "ovti,ov13858" ||
       name == "microsoft,sp11-vd55g0")
    sensors.push_back(device.path());
  }
  check(sensors.size() == 3, "three board sensors");
  auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(3);
  do {
   bool idle = true;
   for (const auto &sensor : sensors) {
    std::ifstream status(sensor / "power/runtime_status");
    std::string state;
    status >> state;
    idle = idle && state == "suspended";
   }
   if (idle)
    return;
   std::this_thread::sleep_for(std::chrono::milliseconds(20));
  } while (std::chrono::steady_clock::now() < deadline);
  throw std::runtime_error("sensors not suspended after stream stop");
 }
 static void check(bool value, const std::string &message)
 {
  if (!value)
   throw std::runtime_error(message);
 }
 void complete(Request *request)
 {
  std::unique_lock lock(mutex_);
  if (request->status() == Request::RequestCancelled)
   return;
  FrameBuffer *buffer = request->findBuffer(stream_);
  auto timestamp = request->metadata().get(controls::SensorTimestamp);
  if (!buffer || request->status() != Request::RequestComplete ||
      buffer->metadata().status != FrameMetadata::FrameSuccess ||
      timestamp || !buffer->metadata().timestamp ||
      buffer->metadata().sequence < 4 ||
      (!frames_.empty() && buffer->metadata().sequence <= frames_.back().first) ||
      request->metadata().get(controls::ExposureTime) != expectedExposure_ ||
      request->metadata().get(controls::AnalogueGain) != expectedGain_ ||
      request->metadata().get(controls::DigitalGain) != expectedGain_ ||
      request->metadata().get(controls::AeEnable) != false ||
      buffer->metadata().planes().size() != 2 ||
      buffer->metadata().planes()[0].bytesused != 3686400 ||
      buffer->metadata().planes()[1].bytesused != 1843200 ||
      completed_ >= limit_ ||
      (!frames_.empty() && buffer->metadata().timestamp <= frames_.back().second)) {
   failure_ = "request, plane, timestamp or finite sequence association";
   ready_.notify_one();
   return;
  }
  frames_.emplace_back(buffer->metadata().sequence, buffer->metadata().timestamp);
  completed_++;
  if (queued_ < limit_) {
   request->reuse(Request::ReuseBuffers);
   if (camera_->queueRequest(request)) {
    failure_ = "reused request admission";
    ready_.notify_one();
    return;
   }
   queued_++;
  }
  if (completed_ == limit_)
   ready_.notify_one();
 }
 std::shared_ptr<Camera> camera_;
 std::unique_ptr<CameraConfiguration> configuration_;
 std::unique_ptr<FrameBufferAllocator> allocator_;
 Stream *stream_ = nullptr;
 std::vector<std::unique_ptr<Request>> requests_;
 std::mutex mutex_;
 std::condition_variable ready_;
 int32_t expectedExposure_ = 0;
 float expectedGain_ = 0;
 unsigned int completed_ = 0, queued_ = 0, limit_ = 0;
 bool acquired_ = false, running_ = false;
 std::string failure_;
 std::vector<std::pair<uint32_t,uint64_t>> frames_;
};

int main(int argc, char **argv)
{
 if (argc == 2 && std::string(argv[1]) == "--help") {
  std::cout << "SP11 public-libcamera lifecycle qualification:1,24,reacquire24 frames\n";
  return 0;
 }
 try {
  CameraManager manager;
  if (manager.start())
   throw std::runtime_error("camera manager");
  auto camera = manager.get("sp11-front-imx681");
  if (!camera || manager.cameras().size() != 1)
   throw std::runtime_error("qualified single front camera");
  {
   Lifecycle capture(camera);
   capture.acquireAndConfigure();
   capture.capture(0,1);
   capture.capture(1,24); // Same object, configuration and application DMA buffers.
   capture.release();
   capture.acquireAndConfigure();
   capture.capture(2,24); // Same manager/camera object, closed/reopened devices.
   capture.release();
  }
  /* Return the application Camera reference before manager cleanup/deferred
   * Camera/IPA deletion. CameraManager::stop documents this lifetime rule. */
  std::cerr << "LC_STAGE camera_reset_begin" << std::endl;
  camera.reset();
  std::cerr << "LC_STAGE camera_reset_end manager_stop_begin" << std::endl;
  manager.stop();
  std::cerr << "LC_STAGE manager_stop_end" << std::endl;
  std::cout << "PASS_LIBCAMERA_REQUEST_CONTROLS_LIFECYCLE_1_24_24" << std::endl;
  return 0;
 } catch (const std::exception &error) {
  std::cerr << "LIFECYCLE_FAILED " << error.what() << std::endl;
  return 1;
 }
}
