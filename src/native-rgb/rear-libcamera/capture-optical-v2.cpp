/* SPDX-License-Identifier: GPL-2.0-only */
/* Real public libcamera Requests with3 finite SAME-SP11 private snapshots. */
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <vector>
#include "rear-completion-cadence.h"
#include "rear-private-optical-v2.h"
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
  colorSpace_ = cfg.colorSpace ? cfg.colorSpace->toString() : "unspecified";
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
   bool ready = ready_.wait_for(lock, std::chrono::seconds(20),
                               [&]{return completed_ >= 400 || !failure_.empty();});
   if (!ready) failure_ = "request completion timeout";
  }
  auto stoppingAt = std::chrono::steady_clock::now();
  need(!camera_->stop(), "stop"); running_ = false;
  need(failure_.empty(), failure_);
  need(completed_ >= 400, "400 complete reused application requests");
  requests_.clear();
  need(!allocator_->free(stream_), "application buffer release");
  allocator_.reset();
  need(!camera_->release(), "release"); acquired_ = false;
  privateFrames_.saveAfterRelease();
  double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started_).count();
  double callbackSpan = std::chrono::duration<double>(lastCallback_ - firstCallback_).count();
  double beforeFirst = std::chrono::duration<double>(firstCallback_ - started_).count();
  double afterLast = std::chrono::duration<double>(std::chrono::steady_clock::now() - lastCallback_).count();
  double stopRelease = std::chrono::duration<double>(std::chrono::steady_clock::now() - stoppingAt).count();
  need(completed_ == 400 && callbackSpan > 0 && timestamp_ > firstTimestamp_ && minGap_ > 0, "cadence interval admission");
  std::cout << "{\"status\":\"PASS_LIBCAMERA_REAR_CONTINUOUS_REQUEST_REUSE\","
            << "\"completed_frames\":" << completed_
            << ",\"width\":3840,\"height\":2160,\"stride\":3840,"
               "\"image_bytes\":12441600,\"logical_planes\":2,\"pixel_bytes_read\":37324800,\"private_nv12_frames_saved\":3,\"optical_diagnostic_copy\":true,"
               "\"SensorTimestamp_present\":false,\"stop_and_release\":true,"
               "\"application_buffers\":4,\"reused_requests\":true,"
            << "\"elapsed_seconds\":" << elapsed
            << ",\"completion_rate_fps\":" << completed_ / elapsed
            << ",\"callback_intervals\":" << completed_-1
            << ",\"callback_span_seconds\":" << callbackSpan
            << ",\"callback_interval_rate_fps\":" << (completed_-1)/callbackSpan
            << ",\"completion_timestamp_span_ns\":" << timestamp_-firstTimestamp_
            << ",\"completion_gap_min_ns\":" << minGap_
            << ",\"completion_gap_max_ns\":" << maxGap_
            << ",\"prefix_buffers\":80"
            << ",\"prefix_completion_timestamp_span_ns\":" << cadence_.prefixLast-cadence_.first
            << ",\"prefix_completion_gap_min_ns\":" << cadence_.prefixMin
            << ",\"prefix_completion_gap_max_ns\":" << cadence_.prefixMax
            << ",\"long_gap_threshold_ns\":50000000"
            << ",\"long_gap_count\":" << cadence_.longGaps
            << ",\"long_gap_count_after_first80\":" << cadence_.lateLongGaps
            << ",\"first_long_gap_sequence\":" << cadence_.firstLongSequence
            << ",\"completion_gap_max_sequence\":" << cadence_.maximumSequence
            << ",\"start_to_first_callback_seconds\":" << beforeFirst
            << ",\"last_callback_to_release_seconds\":" << afterLast
            << ",\"stop_release_seconds\":" << stopRelease
            << ",\"color_space\":\"" << colorSpace_ << "\""
            << ",\"timestamp_kind\":\"driver_completion_not_sensor_SOF\"}" << std::endl;
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
  try {
   const auto &planes=buffer->planes();
   need(planes.size()==2,"optical exported plane count");
   privateFrames_.capture({planes[0].fd.get(),planes[1].fd.get(),
    planes[0].offset,planes[1].offset,planes[0].length,planes[1].length},completed_);
  } catch(const std::exception &error) {
   failure_=error.what();ready_.notify_one();return;
  }
  const auto now = std::chrono::steady_clock::now();
  if (!completed_) { firstCallback_ = now; firstTimestamp_ = buffer->metadata().timestamp; }
  else {
   const uint64_t gap = buffer->metadata().timestamp - timestamp_;
   if (!minGap_ || gap < minGap_) minGap_ = gap;
   if (gap > maxGap_) maxGap_ = gap;
  }
  cadence_.observe(buffer->metadata().timestamp, completed_);
  lastCallback_ = now;
  timestamp_ = buffer->metadata().timestamp;
  completed_++;
  if (completed_ >= 400) {
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
 std::chrono::steady_clock::time_point started_, firstCallback_, lastCallback_;
 uint64_t firstTimestamp_ = 0, minGap_ = 0, maxGap_ = 0;
 RearCompletionCadence cadence_;
 RearOptical::PrivateFrames privateFrames_;
 std::string colorSpace_;
 unsigned int completed_ = 0;
 uint64_t timestamp_ = 0;
 std::string failure_;
};
int main(int argc, char **argv)
{
 if (argc == 2 && std::string(argv[1]) == "--help") {
  std::cout << "SP11 private optical snapshots; pixels remain SAME SP11; normal Request reuse\n";
  return 0;
 }
 /* OPTICAL_IDENTITY_PREFLIGHT_BEGIN */
 if (argc == 2 && std::string(argv[1]) == "--identity-check") {
  bool ok=true;
  for (unsigned s=1;s<=3;s++)
   ok=ok && RearOptical::privateDirectoryAllowed("/var/lib/sp11-camera-native-rear-generation-20261007-52/private-optical/session-"+std::to_string(s));
  ok=ok && !RearOptical::privateDirectoryAllowed("/var/lib/sp11-camera-native-rear-generation-20261007-49/private-optical/session-1");
  if (!ok) return 1;
  std::cout << "{\"status\":\"PASS_PRIVATE_OPTICAL_COMPILE_BOUND_IDENTITY\",\"candidate_identity\":52,\"hardware_access\":false}\n";
  return 0;
 }
 /* OPTICAL_IDENTITY_PREFLIGHT_END */
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
