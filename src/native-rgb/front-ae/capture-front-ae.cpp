/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * SP11 front (imx681) validation capture against a displayed pattern loop.
 *
 * Phase 0 uses fixed manual controls (tone/colour check against the Windows
 * fixed-exposure reference); phase 1 enables pipeline automatic exposure
 * (AE check against the Windows automatic reference). Per-frame applied
 * exposure, gains and AeState are written to meta.csv. Every 2560x1440 NV12 frame is reduced to a
 * 16x9 grid of Y/U/V means, stored with the driver completion time and
 * CLOCK_REALTIME so frames can be aligned with the SP7 player log. Two full
 * frames are kept for ROI inspection. All output stays in SP11_PATTERN_DIR.
 */
#include <algorithm>
#include <cerrno>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <iostream>
#include <linux/dma-buf.h>
#include <map>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <vector>
#include <libcamera/camera.h>
#include <libcamera/camera_manager.h>
#include <libcamera/control_ids.h>
#include <libcamera/formats.h>
#include <libcamera/framebuffer_allocator.h>
#include <libcamera/request.h>
using namespace libcamera;

namespace {
constexpr unsigned W = 2560, H = 1440, GX = 16, GY = 9, CW = W / GX, CH = H / GY;
constexpr size_t YBytes = size_t(W) * H, UVBytes = YBytes / 2;
/* imx681 timing used by the camss-x1e pipeline: 422/45 us per line. */
int32_t exposureUs(int32_t lines) { return int32_t((int64_t(lines) * 422 + 22) / 45); }
struct Phase { int32_t lines; float again, dgain; bool automatic; };
const Phase kPhases[] = { { 3546, 16.0f, 1.0f, false }, { 0, 0.0f, 0.0f, true } };
constexpr unsigned kPhaseCount = sizeof(kPhases) / sizeof(kPhases[0]);
struct Record {
	uint32_t sequence, phase;
	uint64_t completion_ns, realtime_ns;
	float y[GX * GY], u[GX * GY], v[GX * GY];
};
uint64_t realtimeNs()
{
	timespec ts{};
	clock_gettime(CLOCK_REALTIME, &ts);
	return uint64_t(ts.tv_sec) * 1000000000ull + ts.tv_nsec;
}
void dmaSync(int fd, bool start)
{
	dma_buf_sync s{};
	s.flags = (start ? DMA_BUF_SYNC_START : DMA_BUF_SYNC_END) | DMA_BUF_SYNC_READ;
	while (ioctl(fd, DMA_BUF_IOCTL_SYNC, &s) < 0)
		if (errno != EINTR)
			throw std::runtime_error("dma-buf sync");
}
void need(bool ok, const std::string &what)
{
	if (!ok)
		throw std::runtime_error(what);
}
void setPhase(ControlList &c, const Phase &p)
{
	if (p.automatic) {
		c.set(controls::AeEnable, true);
		return;
	}
	c.set(controls::AeEnable, false);
	c.set(controls::ExposureTime, exposureUs(p.lines));
	c.set(controls::AnalogueGain, p.again);
	c.set(controls::DigitalGain, p.dgain);
}
struct Meta { uint32_t sequence; int32_t exposure_us; float again, dgain; int32_t ae_state, ae_enable; };
}

class Capture
{
public:
	Capture(std::shared_ptr<Camera> camera, std::string dir, unsigned perPhase)
		: camera_(std::move(camera)), dir_(std::move(dir)), perPhase_(perPhase)
	{
		total_ = perPhase_ * kPhaseCount;
		records_.reserve(total_);
		camera_->requestCompleted.connect(this, &Capture::complete);
	}
	~Capture()
	{
		if (running_)
			camera_->stop();
		camera_->requestCompleted.disconnect(this);
		requests_.clear();
		for (auto &m : maps_)
			munmap(m.second.first, m.second.second);
		allocator_.reset();
		if (acquired_)
			camera_->release();
	}
	void run()
	{
		need(!camera_->acquire(), "acquire");
		acquired_ = true;
		config_ = camera_->generateConfiguration({ StreamRole::Viewfinder });
		need(config_ && config_->size() == 1, "configuration");
		auto &cfg = config_->at(0);
		need(cfg.pixelFormat == formats::NV12 && cfg.size == Size(W, H) && cfg.stride == W,
		     "2560x1440 NV12 configuration");
		need(!camera_->configure(config_.get()), "configure");
		stream_ = cfg.stream();
		allocator_ = std::make_unique<FrameBufferAllocator>(camera_);
		const int n = allocator_->allocate(stream_);
		need(n >= 4, "four buffers");
		for (int i = 0; i < n; i++) {
			auto request = camera_->createRequest(i);
			need(request && !request->addBuffer(stream_, allocator_->buffers(stream_)[i].get()),
			     "request binding");
			requests_.push_back(std::move(request));
		}
		ControlList start(camera_->controls());
		setPhase(start, kPhases[0]);
		started_ = std::chrono::steady_clock::now();
		startRealtime_ = realtimeNs();
		need(!camera_->start(&start), "start");
		running_ = true;
		{
			std::unique_lock lock(mutex_);
			for (auto &request : requests_)
				need(!camera_->queueRequest(request.get()), "queue");
			bool done = cv_.wait_for(lock, std::chrono::seconds(total_ / 20 + 40),
						 [&] { return completed_ >= total_ || !failure_.empty(); });
			if (!done)
				failure_ = "completion timeout";
			stopping_ = true;
		}
		need(!camera_->stop(), "stop");
		running_ = false;
		double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started_).count();
		requests_.clear();
		for (auto &m : maps_)
			munmap(m.second.first, m.second.second);
		maps_.clear();
		need(!allocator_->free(stream_), "buffer release");
		allocator_.reset();
		need(!camera_->release(), "release");
		acquired_ = false;
		writeOutputs();
		std::cout << "{\"status\":\"" << (failure_.empty() ? "PASS_FRONT_AE_CAPTURE" : "PARTIAL_FRONT_AE_CAPTURE")
			  << "\",\"error\":\"" << failure_ << "\",\"completed_frames\":" << completed_
			  << ",\"requested_frames\":" << total_ << ",\"frames_per_phase\":" << perPhase_
			  << ",\"elapsed_seconds\":" << elapsed << ",\"fps\":" << completed_ / elapsed
			  << ",\"start_realtime_ns\":" << startRealtime_ << ",\"phases\":[";
		for (unsigned i = 0; i < kPhaseCount; i++)
			std::cout << (i ? "," : "") << "{\"lines\":" << kPhases[i].lines << ",\"exposure_us\":"
				  << exposureUs(kPhases[i].lines) << ",\"again\":" << kPhases[i].again
				  << ",\"dgain\":" << kPhases[i].dgain << ",\"automatic\":" << kPhases[i].automatic << "}";
		std::cout << "],\"grid\":[" << GX << "," << GY << "],\"record_bytes\":" << sizeof(Record)
			  << ",\"full_frames_saved\":" << savedFrames_ << ",\"metadata_mismatches\":" << mismatches_
			  << "}" << std::endl;
		need(completed_ >= total_ / 2, failure_.empty() ? "too few frames" : failure_);
	}

private:
	const uint8_t *mapPlane(int fd, size_t end)
	{
		auto it = maps_.find(fd);
		if (it == maps_.end()) {
			/* Planes share one dma-buf: map the whole buffer once. */
			off_t size = lseek(fd, 0, SEEK_END);
			need(size > 0 && size_t(size) >= end, "dma-buf size");
			void *p = mmap(nullptr, size_t(size), PROT_READ, MAP_SHARED, fd, 0);
			need(p != MAP_FAILED, "mmap");
			it = maps_.emplace(fd, std::make_pair(p, size_t(size))).first;
		}
		need(it->second.second >= end, "mapping extent");
		return static_cast<const uint8_t *>(it->second.first);
	}
	void reduce(const FrameBuffer *buffer, Record &r)
	{
		const auto &planes = buffer->planes();
		need(planes.size() == 2, "plane count");
		const int yfd = planes[0].fd.get(), cfd = planes[1].fd.get();
		const uint8_t *ybase = mapPlane(yfd, planes[0].offset + planes[0].length) + planes[0].offset;
		const uint8_t *cbase = mapPlane(cfd, planes[1].offset + planes[1].length) + planes[1].offset;
		dmaSync(yfd, true);
		if (cfd != yfd)
			dmaSync(cfd, true);
		for (unsigned gy = 0; gy < GY; gy++)
			for (unsigned gx = 0; gx < GX; gx++) {
				uint64_t sy = 0, su = 0, sv = 0, n = 0, m = 0;
				for (unsigned y = gy * CH + 1; y < (gy + 1) * CH; y += 3)
					for (unsigned x = gx * CW + 1; x < (gx + 1) * CW; x += 3) {
						sy += ybase[size_t(y) * W + x];
						n++;
					}
				for (unsigned y = gy * CH / 2; y < (gy + 1) * CH / 2; y += 2)
					for (unsigned x = gx * CW / 2; x < (gx + 1) * CW / 2; x += 2) {
						const uint8_t *c = cbase + size_t(y) * W + 2 * x;
						su += c[0];
						sv += c[1];
						m++;
					}
				r.y[gy * GX + gx] = float(double(sy) / n);
				r.u[gy * GX + gx] = float(double(su) / m);
				r.v[gy * GX + gx] = float(double(sv) / m);
			}
		if (keep_.size() < 2 && (completed_ == perPhase_ / 2 || completed_ == perPhase_ + perPhase_ / 2)) {
			keep_.emplace_back(YBytes + UVBytes);
			std::memcpy(keep_.back().data(), ybase, YBytes);
			std::memcpy(keep_.back().data() + YBytes, cbase, UVBytes);
			keepSeq_.push_back(completed_);
		}
		if (cfd != yfd)
			dmaSync(cfd, false);
		dmaSync(yfd, false);
	}
	void complete(Request *request)
	{
		std::unique_lock lock(mutex_);
		if (request->status() == Request::RequestCancelled || stopping_)
			return;
		const uint64_t now = realtimeNs();
		auto *buffer = request->findBuffer(stream_);
		if (!buffer || request->status() != Request::RequestComplete ||
		    buffer->metadata().status != FrameMetadata::FrameSuccess) {
			failure_ = "request or buffer failure at frame " + std::to_string(completed_);
			cv_.notify_one();
			return;
		}
		try {
			Record r{};
			r.sequence = buffer->metadata().sequence;
			r.phase = std::min(completed_ / perPhase_, kPhaseCount - 1);
			const auto &md = request->metadata();
			Meta m{ r.sequence, md.get(controls::ExposureTime).value_or(-1),
				md.get(controls::AnalogueGain).value_or(-1.0f),
				md.get(controls::DigitalGain).value_or(-1.0f),
				md.get(controls::AeState).value_or(-1),
				int32_t(md.get(controls::AeEnable).value_or(false)) };
			meta_.push_back(m);
			/* Phase 0 frames whose applied controls are not the manual values
			 * yet (transition) are marked invalid. */
			if (r.phase == 0 && (std::fabs(m.again - kPhases[0].again) > 0.05f * kPhases[0].again ||
					     m.exposure_us != exposureUs(kPhases[0].lines))) {
				mismatches_++;
				r.phase = 0xffffffffu;
			}
			r.completion_ns = buffer->metadata().timestamp;
			r.realtime_ns = now;
			reduce(buffer, r);
			records_.push_back(r);
		} catch (const std::exception &e) {
			failure_ = e.what();
			cv_.notify_one();
			return;
		}
		completed_++;
		if (completed_ >= total_) {
			stopping_ = true;
			cv_.notify_one();
			return;
		}
		request->reuse(Request::ReuseBuffers);
		if (completed_ % perPhase_ == 0)
			setPhase(request->controls(), kPhases[completed_ / perPhase_]);
		if (camera_->queueRequest(request)) {
			failure_ = "requeue failed";
			cv_.notify_one();
		}
	}
	void writeOutputs()
	{
		std::string path = dir_ + "/records.bin";
		FILE *f = std::fopen(path.c_str(), "wbx");
		need(f, "records file");
		need(std::fwrite(records_.data(), sizeof(Record), records_.size(), f) == records_.size(), "records write");
		need(!std::fclose(f), "records close");
		std::string mpath = dir_ + "/meta.csv";
		FILE *mf = std::fopen(mpath.c_str(), "wx");
		need(mf, "meta file");
		std::fprintf(mf, "sequence,exposure_us,again,dgain,ae_state,ae_enable\n");
		for (const Meta &m : meta_)
			std::fprintf(mf, "%u,%d,%.4f,%.4f,%d,%d\n", m.sequence, m.exposure_us, m.again, m.dgain,
				     m.ae_state, m.ae_enable);
		need(!std::fclose(mf), "meta close");
		for (size_t i = 0; i < keep_.size(); i++) {
			std::string name = dir_ + "/frame-" + std::to_string(keepSeq_[i]) + ".nv12";
			FILE *g = std::fopen(name.c_str(), "wbx");
			need(g, "frame file");
			need(std::fwrite(keep_[i].data(), 1, keep_[i].size(), g) == keep_[i].size(), "frame write");
			need(!std::fclose(g), "frame close");
			savedFrames_++;
		}
	}
	std::shared_ptr<Camera> camera_;
	std::string dir_;
	unsigned perPhase_, total_ = 0;
	std::unique_ptr<CameraConfiguration> config_;
	std::unique_ptr<FrameBufferAllocator> allocator_;
	Stream *stream_ = nullptr;
	std::vector<std::unique_ptr<Request>> requests_;
	std::map<int, std::pair<void *, size_t>> maps_;
	std::vector<Record> records_;
	std::vector<Meta> meta_;
	std::vector<std::vector<uint8_t>> keep_;
	std::vector<unsigned> keepSeq_;
	unsigned savedFrames_ = 0, mismatches_ = 0;
	std::mutex mutex_;
	std::condition_variable cv_;
	bool acquired_ = false, running_ = false, stopping_ = false;
	std::chrono::steady_clock::time_point started_;
	uint64_t startRealtime_ = 0;
	unsigned completed_ = 0;
	std::string failure_;
};

int main(int argc, char **argv)
{
	if (argc == 2 && std::string(argv[1]) == "--help") {
		std::cout << "SP11 front AE/tone validation capture (env SP11_PATTERN_DIR, SP11_PATTERN_FRAMES_PER_PHASE)\n";
		return 0;
	}
	try {
		const char *dir = std::getenv("SP11_PATTERN_DIR");
		need(dir && *dir, "SP11_PATTERN_DIR");
		const char *pp = std::getenv("SP11_PATTERN_FRAMES_PER_PHASE");
		unsigned perPhase = pp ? unsigned(std::strtoul(pp, nullptr, 10)) : 1800;
		need(perPhase >= 60 && perPhase <= 3000, "frames per phase range");
		CameraManager manager;
		need(!manager.start(), "camera manager");
		auto camera = manager.get("sp11-front-imx681");
		need(camera && manager.cameras().size() == 1, "one front camera");
		{
			Capture capture(camera, dir, perPhase);
			capture.run();
		}
		camera.reset();
		manager.stop();
		return 0;
	} catch (const std::exception &e) {
		std::cerr << "FRONT_AE_FAILED " << e.what() << std::endl;
		return 1;
	}
}
