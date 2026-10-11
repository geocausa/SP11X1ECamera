/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * sp11-webcam: on-demand bridge from one SP11 camera (libcamera, native
 * camss-x1e front or camss-x1e-rear pipeline, NV12) to a v4l2loopback device
 * that ordinary applications use as a webcam (1920x1080 YUYV, 30 fps).
 *
 * Usage: sp11-webcam <libcamera camera id> <loopback device>
 * One instance per camera. The camera runs only while another process holds the
 * loopback device open and is released a few seconds after the last reader
 * closes it. Both cameras share one media device, so only one can stream at a
 * time; a start that finds the other camera busy is retried.
 */
#include <algorithm>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <iostream>
#include <linux/dma-buf.h>
#include <linux/videodev2.h>
#include <map>
#include <memory>
#include <string>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <thread>
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
constexpr unsigned OW = 1920, OH = 1080;
constexpr size_t OUT_BYTES = size_t(OW) * OH * 2;
std::atomic<bool> gQuit{ false };
std::string gTag = "sp11-webcam";

void logmsg(const std::string &m) { std::cerr << gTag << ": " << m << std::endl; }

void dmaSync(int fd, bool start)
{
	dma_buf_sync s{};
	s.flags = (start ? DMA_BUF_SYNC_START : DMA_BUF_SYNC_END) | DMA_BUF_SYNC_READ;
	while (ioctl(fd, DMA_BUF_IOCTL_SYNC, &s) < 0 && errno == EINTR) {
	}
}

/* Bilinear resampling tables: output index -> source index and 8-bit weight. */
struct Axis {
	std::vector<unsigned> i0;
	std::vector<unsigned> w1; /* weight of i0 + 1, 0..256 */
	void build(unsigned src, unsigned dst)
	{
		i0.resize(dst);
		w1.resize(dst);
		for (unsigned o = 0; o < dst; o++) {
			double s = (o + 0.5) * src / dst - 0.5;
			s = std::clamp(s, 0.0, double(src - 1));
			unsigned a = std::min(unsigned(s), src - 2);
			i0[o] = a;
			w1[o] = unsigned((s - a) * 256.0 + 0.5);
		}
	}
};

class Converter
{
public:
	void setup(unsigned w, unsigned h, unsigned ystride, unsigned cstride)
	{
		ys_ = ystride;
		cs_ = cstride;
		yx_.build(w, OW);
		yy_.build(h, OH);
		cx_.build(w / 2, OW / 2);
		cy_.build(h / 2, OH);
	}
	/* NV12 -> YUYV 4:2:2 at OW x OH. */
	void run(const uint8_t *y, const uint8_t *uv, uint8_t *out) const
	{
		for (unsigned r = 0; r < OH; r++) {
			const uint8_t *y0 = y + size_t(yy_.i0[r]) * ys_, *y1 = y0 + ys_;
			const unsigned wy = yy_.w1[r];
			const uint8_t *c0 = uv + size_t(cy_.i0[r]) * cs_, *c1 = c0 + cs_;
			const unsigned wc = cy_.w1[r];
			uint8_t *o = out + size_t(r) * OW * 2;
			for (unsigned x = 0; x < OW; x++) {
				const unsigned a = yx_.i0[x], wx = yx_.w1[x];
				const unsigned t = y0[a] * (256 - wx) + y0[a + 1] * wx;
				const unsigned b = y1[a] * (256 - wx) + y1[a + 1] * wx;
				o[2 * x] = uint8_t((t * (256 - wy) + b * wy + 32768) >> 16);
			}
			for (unsigned x = 0; x < OW / 2; x++) {
				const unsigned a = 2 * cx_.i0[x], wx = cx_.w1[x];
				for (unsigned k = 0; k < 2; k++) {
					const unsigned t = c0[a + k] * (256 - wx) + c0[a + 2 + k] * wx;
					const unsigned b = c1[a + k] * (256 - wx) + c1[a + 2 + k] * wx;
					o[4 * x + 1 + 2 * k] = uint8_t((t * (256 - wc) + b * wc + 32768) >> 16);
				}
			}
		}
	}

private:
	unsigned ys_ = 0, cs_ = 0;
	Axis yx_, yy_, cx_, cy_;
};

/* Count other processes holding the loopback device open. */
int readers(const std::string &dev)
{
	int n = 0;
	const pid_t self = getpid();
	DIR *proc = opendir("/proc");
	if (!proc)
		return 0;
	while (dirent *e = readdir(proc)) {
		char *end;
		long pid = strtol(e->d_name, &end, 10);
		if (*end || pid <= 0 || pid == self)
			continue;
		std::string fdd = std::string("/proc/") + e->d_name + "/fd";
		DIR *fds = opendir(fdd.c_str());
		if (!fds)
			continue;
		while (dirent *f = readdir(fds)) {
			char buf[256];
			std::string p = fdd + "/" + f->d_name;
			ssize_t l = readlink(p.c_str(), buf, sizeof(buf) - 1);
			if (l > 0) {
				buf[l] = 0;
				if (dev == buf) {
					n++;
					break;
				}
			}
		}
		closedir(fds);
	}
	closedir(proc);
	return n;
}

class Bridge
{
public:
	Bridge(std::shared_ptr<Camera> cam, int out) : cam_(std::move(cam)), out_(out), frame_(OUT_BYTES)
	{
		cam_->requestCompleted.connect(this, &Bridge::complete);
	}
	~Bridge() { stop(); cam_->requestCompleted.disconnect(this); }
	bool running() const { return running_; }
	bool start()
	{
		failed_ = false;
		if (cam_->acquire())
			return false;
		acquired_ = true;
		cfg_ = cam_->generateConfiguration({ StreamRole::Viewfinder });
		if (!cfg_ || cfg_->size() != 1 || cfg_->validate() == CameraConfiguration::Invalid ||
		    cam_->configure(cfg_.get())) {
			stop();
			return false;
		}
		const StreamConfiguration &sc = cfg_->at(0);
		if (sc.pixelFormat != formats::NV12 || sc.size.width < OW || sc.size.height < OH) {
			logmsg("unexpected stream " + sc.toString());
			stop();
			return false;
		}
		conv_.setup(sc.size.width, sc.size.height, sc.stride, sc.stride);
		stream_ = sc.stream();
		alloc_ = std::make_unique<FrameBufferAllocator>(cam_);
		if (alloc_->allocate(stream_) <= 0) {
			stop();
			return false;
		}
		for (auto &b : alloc_->buffers(stream_)) {
			auto r = cam_->createRequest();
			if (!r || r->addBuffer(stream_, b.get())) {
				stop();
				return false;
			}
			reqs_.push_back(std::move(r));
		}
		ControlList c(cam_->controls());
		if (cam_->controls().count(&controls::AeEnable))
			c.set(controls::AeEnable, true);
		if (cam_->start(&c)) {
			stop();
			return false;
		}
		running_ = true;
		for (auto &r : reqs_)
			cam_->queueRequest(r.get());
		frames_ = 0;
		started_ = std::chrono::steady_clock::now();
		lastFrame_ = started_.time_since_epoch().count();
		logmsg("streaming " + sc.toString());
		return true;
	}
	void stop()
	{
		if (running_) {
			stopping_ = true;
			cam_->stop();
			running_ = false;
			stopping_ = false;
			double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - started_).count();
			logmsg("stopped after " + std::to_string(frames_) + " frames, " + std::to_string(s > 0 ? frames_ / s : 0) + " fps");
		}
		reqs_.clear();
		for (auto &m : maps_)
			munmap(m.second.first, m.second.second);
		maps_.clear();
		if (alloc_ && stream_)
			alloc_->free(stream_);
		alloc_.reset();
		stream_ = nullptr;
		cfg_.reset();
		if (acquired_)
			cam_->release();
		acquired_ = false;
	}
	bool failed() const { return failed_; }
	/* Seconds since the last delivered frame (or since start). */
	double idle() const
	{
		const std::chrono::steady_clock::duration d(
			std::chrono::steady_clock::now().time_since_epoch().count() - lastFrame_.load());
		return std::chrono::duration<double>(d).count();
	}

private:
	const uint8_t *map(int fd)
	{
		auto it = maps_.find(fd);
		if (it == maps_.end()) {
			off_t sz = lseek(fd, 0, SEEK_END);
			void *p = sz > 0 ? mmap(nullptr, size_t(sz), PROT_READ, MAP_SHARED, fd, 0) : MAP_FAILED;
			if (p == MAP_FAILED)
				return nullptr;
			it = maps_.emplace(fd, std::make_pair(p, size_t(sz))).first;
		}
		return static_cast<const uint8_t *>(it->second.first);
	}
	void complete(Request *r)
	{
		if (r->status() == Request::RequestCancelled || stopping_)
			return;
		FrameBuffer *b = r->findBuffer(stream_);
		if (b && r->status() == Request::RequestComplete && b->metadata().status == FrameMetadata::FrameSuccess) {
			const auto &pl = b->planes();
			const int f0 = pl[0].fd.get(), f1 = pl.size() > 1 ? pl[1].fd.get() : f0;
			const uint8_t *yb = map(f0), *cb = map(f1);
			if (yb && cb && pl.size() > 1) {
				dmaSync(f0, true);
				if (f1 != f0)
					dmaSync(f1, true);
				conv_.run(yb + pl[0].offset, cb + pl[1].offset, frame_.data());
				if (f1 != f0)
					dmaSync(f1, false);
				dmaSync(f0, false);
				if (write(out_, frame_.data(), frame_.size()) != ssize_t(frame_.size()) && errno != EAGAIN)
					logmsg(std::string("loopback write: ") + strerror(errno));
				frames_++;
				lastFrame_ = std::chrono::steady_clock::now().time_since_epoch().count();
			}
		} else if (r->status() != Request::RequestCancelled) {
			failed_ = true;
		}
		r->reuse(Request::ReuseBuffers);
		if (running_ && !stopping_)
			cam_->queueRequest(r);
	}
	std::shared_ptr<Camera> cam_;
	int out_;
	std::vector<uint8_t> frame_;
	Converter conv_;
	std::unique_ptr<CameraConfiguration> cfg_;
	std::unique_ptr<FrameBufferAllocator> alloc_;
	Stream *stream_ = nullptr;
	std::vector<std::unique_ptr<Request>> reqs_;
	std::map<int, std::pair<void *, size_t>> maps_;
	bool acquired_ = false;
	std::atomic<bool> running_{ false }, stopping_{ false }, failed_{ false };
	unsigned long frames_ = 0;
	std::atomic<std::chrono::steady_clock::rep> lastFrame_{ 0 };
	std::chrono::steady_clock::time_point started_;
};

int openLoopback(const std::string &dev)
{
	int fd = open(dev.c_str(), O_RDWR | O_NONBLOCK);
	if (fd < 0)
		return -1;
	v4l2_format f{};
	f.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
	f.fmt.pix.width = OW;
	f.fmt.pix.height = OH;
	f.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
	f.fmt.pix.field = V4L2_FIELD_NONE;
	f.fmt.pix.bytesperline = OW * 2;
	f.fmt.pix.sizeimage = OUT_BYTES;
	f.fmt.pix.colorspace = V4L2_COLORSPACE_SMPTE170M;
	f.fmt.pix.quantization = V4L2_QUANTIZATION_FULL_RANGE;
	if (ioctl(fd, VIDIOC_S_FMT, &f) < 0) {
		close(fd);
		return -1;
	}
	v4l2_streamparm p{};
	p.type = V4L2_BUF_TYPE_VIDEO_OUTPUT;
	p.parm.output.timeperframe.numerator = 1;
	p.parm.output.timeperframe.denominator = 30;
	ioctl(fd, VIDIOC_S_PARM, &p);
	std::vector<uint8_t> black(OUT_BYTES);
	for (size_t i = 0; i < OUT_BYTES; i += 2) {
		black[i] = 0;
		black[i + 1] = 128;
	}
	if (write(fd, black.data(), black.size()) < 0)
		logmsg(std::string("initial frame: ") + strerror(errno));
	return fd;
}
} /* namespace */

int main(int argc, char **argv)
{
	if (argc != 3) {
		std::cerr << "usage: sp11-webcam <camera id> <loopback device>" << std::endl;
		return 2;
	}
	const std::string id = argv[1], dev = argv[2];
	gTag = "sp11-webcam[" + id + "]";
	signal(SIGTERM, [](int) { gQuit = true; });
	signal(SIGINT, [](int) { gQuit = true; });
	int out = openLoopback(dev);
	if (out < 0) {
		logmsg("cannot open/configure " + dev);
		return 1;
	}
	CameraManager cm;
	if (cm.start()) {
		logmsg("camera manager failed");
		return 1;
	}
	auto cam = cm.get(id);
	if (!cam) {
		logmsg("camera not found");
		return 1;
	}
	logmsg("ready on " + dev + " (1920x1080 YUYV, camera off until opened)");
	{
		Bridge br(cam, out);
		auto lastSeen = std::chrono::steady_clock::now();
		auto nextTry = lastSeen;
		unsigned failures = 0;
		while (!gQuit) {
			int n = readers(dev);
			auto now = std::chrono::steady_clock::now();
			if (n > 0)
				lastSeen = now;
			if (n > 0 && !br.running() && now >= nextTry) {
				logmsg("reader detected; starting camera");
				if (br.start()) {
					failures = 0;
				} else {
					failures++;
					logmsg("camera start failed (busy or error); retrying");
					nextTry = now + std::chrono::seconds(std::min(failures, 5u));
				}
			} else if (br.running() && (br.failed() || br.idle() > 3.0 ||
						      now - lastSeen > std::chrono::seconds(4))) {
				/* A stalled stream (no frame for 3 s) is restarted like a failure. */
				logmsg(br.failed() ? "capture failure; restarting" :
				       br.idle() > 3.0 ? "stream stalled; restarting" : "no readers; stopping camera");
				br.stop();
				nextTry = now + std::chrono::seconds(1);
			}
			std::this_thread::sleep_for(std::chrono::milliseconds(300));
		}
		br.stop();
	}
	cam.reset();
	cm.stop();
	close(out);
	return 0;
}
