/* SPDX-License-Identifier: GPL-2.0-only */
/* Real public libcamera requests; no pixel mapping, reading or file output. */
#include <chrono>
#include <condition_variable>
#include <iostream>
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
class Capture
{
public:
 explicit Capture(std::shared_ptr<Camera> camera) : camera_(std::move(camera))
 { camera_->requestCompleted.connect(this, &Capture::complete); }
 ~Capture()
 {
  if (running_) camera_->stop();
  camera_->requestCompleted.disconnect(this);
  requests_.clear();
  allocator_.reset();
  if (acquired_) camera_->release();
 }
 void run()
 {
  need(!camera_->acquire(), "acquire"); acquired_ = true;
  configuration_ = camera_->generateConfiguration({StreamRole::Viewfinder});
  need(configuration_ && configuration_->size() == 1, "configuration");
  auto &cfg = configuration_->at(0);
  need(cfg.pixelFormat == formats::NV12 && cfg.size == Size(3840,2160) &&
       cfg.bufferCount == 4 && cfg.stride == 3840 && cfg.frameSize == 12441600,
       "exact 4K NV12 configuration");
  need(!camera_->configure(configuration_.get()), "configure");
  stream_ = cfg.stream();
  allocator_ = std::make_unique<FrameBufferAllocator>(camera_);
  need(allocator_->allocate(stream_) == 4, "four exported application DMA buffers");
  for (unsigned int i = 0; i < 4; i++) {
   auto request = camera_->createRequest(i);
   need(request && !request->addBuffer(stream_, allocator_->buffers(stream_)[i].get()),
        "application request binding");
   requests_.push_back(std::move(request));
  }
  started_ = std::chrono::steady_clock::now();
  need(!camera_->start(), "start"); running_ = true;
  {
   std::unique_lock lock(mutex_);
   for (auto &request : requests_) need(!camera_->queueRequest(request.get()), "queue request");
   bool ready = ready_.wait_for(lock, std::chrono::seconds(15),
                               [&]{return completed_ >= 80 || !failure_.empty();});
   if (!ready) failure_ = "request completion timeout";
  }
  need(!camera_->stop(), "stop"); running_ = false;
  need(failure_.empty(), failure_);
  need(completed_ >= 80, "80 complete reused application requests");
  requests_.clear();
  need(!allocator_->free(stream_), "application buffer release");
  allocator_.reset();
  need(!camera_->release(), "release"); acquired_ = false;
  double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started_).count();
  std::cout << "{\"status\":\"PASS_LIBCAMERA_REAR_CONTINUOUS_REQUEST_REUSE\","
            << "\"completed_frames\":" << completed_
            << ",\"width\":3840,\"height\":2160,\"stride\":3840,"
               "\"image_bytes\":12441600,\"logical_planes\":2,\"pixel_bytes_read\":0,"
               "\"SensorTimestamp_present\":false,\"stop_and_release\":true,"
               "\"application_buffers\":4,\"reused_requests\":true,"
            << "\"elapsed_seconds\":" << elapsed
            << ",\"completion_rate_fps\":" << completed_ / elapsed << "}" << std::endl;
 }
private:
 static void need(bool ok, const std::string &what)
 { if (!ok) throw std::runtime_error(what); }
 void complete(Request *request)
 {
  std::unique_lock lock(mutex_);
  if (request->status() == Request::RequestCancelled || stopping_) return;
  auto *buffer = request->findBuffer(stream_);
  if (!buffer || request->status() != Request::RequestComplete ||
      buffer->metadata().status != FrameMetadata::FrameSuccess ||
      buffer->metadata().sequence != completed_ ||
      buffer->metadata().planes().size() != 2 ||
      buffer->metadata().planes()[0].bytesused != 8294400 ||
      buffer->metadata().planes()[1].bytesused != 4147200 ||
      !buffer->metadata().timestamp || buffer->metadata().timestamp <= timestamp_ ||
      request->metadata().get(controls::SensorTimestamp)) {
   failure_ = "request, consumed sequence, planes or timestamp mismatch";
   ready_.notify_one(); return;
  }
  timestamp_ = buffer->metadata().timestamp;
  completed_++;
  if (completed_ >= 80) {
   stopping_ = true; ready_.notify_one();
  } else {
   request->reuse(Request::ReuseBuffers);
   if (camera_->queueRequest(request)) {
    failure_ = "request reuse queue failed"; ready_.notify_one();
   }
  }
 }
 std::shared_ptr<Camera> camera_;
 std::unique_ptr<CameraConfiguration> configuration_;
 std::unique_ptr<FrameBufferAllocator> allocator_;
 Stream *stream_ = nullptr;
 std::vector<std::unique_ptr<Request>> requests_;
 std::mutex mutex_;
 std::condition_variable ready_;
 bool acquired_ = false, running_ = false, stopping_ = false;
 std::chrono::steady_clock::time_point started_;
 unsigned int completed_ = 0;
 uint64_t timestamp_ = 0;
 std::string failure_;
};
int main(int argc, char **argv)
{
 if (argc == 2 && std::string(argv[1]) == "--help") {
  std::cout << "SP11 real public-libcamera rear continuous reused-request qualification; no pixels read\n";
  return 0;
 }
 try {
  CameraManager manager;
  if (manager.start()) throw std::runtime_error("camera manager");
  auto camera = manager.get("sp11-rear-ov13858-qualification");
  if (!camera || manager.cameras().size() != 1)
   throw std::runtime_error("exactly one qualified rear camera");
  { Capture capture(camera); capture.run(); }
  manager.stop();
  return 0;
 } catch (const std::exception &error) {
  std::cerr << "REAR_LIBCAMERA_FAILED " << error.what() << std::endl;
  return 1;
 }
}
