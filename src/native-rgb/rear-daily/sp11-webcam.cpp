/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * sp11-webcam: on-demand bridge from the SP11 rear camera (libcamera,
 * camss-x1e-rear pipeline, 4K NV12, native AE) to a v4l2loopback device that
 * ordinary applications use as a webcam (1920x1080 YUYV, 30 fps).
 *
 * The camera runs only while some other process has the loopback device open;
 * it is stopped and released a few seconds after the last reader closes it.
 */
#include <algorithm>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <condition_variable>
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
#include <mutex>
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
constexpr unsigned SW = 3840, SH = 2160, OW = 1920, OH = 1080;
constexpr size_t OUT_BYTES = size_t(OW) * OH * 2;
std::atomic<bool> gQuit{ false };

void logmsg(const std::string &m) { std::cerr << "sp11-webcam: " << m << std::endl; }

void dmaSync(int fd, bool start)
{
	dma_buf_sync s{};
	s.flags = (start ? DMA_BUF_SYNC_START : DMA_BUF_SYNC_END) | DMA_BUF_SYNC_READ;
	while (ioctl(fd, DMA_BUF_IOCTL_SYNC, &s) < 0 && errno == EINTR) {
	}
}

/* 4K NV12 -> 1080p YUYV: 2x2 luma box filter; one NV12 chroma sample per
 * output pixel, averaged over horizontal pairs for 4:2:2. */
void convert(const uint8_t *y, const uint8_t *uv, uint8_t *out)
{
	for (unsigned r = 0; r < OH; r++) {
		const uint8_t *y0 = y + size_t(2 * r) * SW, *y1 = y0 + SW;
		const uint8_t *c = uv + size_t(r) * SW;
		uint8_t *o = out + size_t(r) * OW * 2;
		for (unsigned x = 0; x < OW; x += 2) {
			const unsigned a = 2 * x;
			o[0] = uint8_t((y0[a] + y0[a + 1] + y1[a] + y1[a + 1] + 2) >> 2);
			o[2] = uint8_t((y0[a + 2] + y0[a + 3] + y1[a + 2] + y1[a + 3] + 2) >> 2);
			o[1] = uint8_t((c[2 * x] + c[2 * x + 2] + 1) >> 1);
			o[3] = uint8_t((c[2 * x + 1] + c[2 * x + 3] + 1) >> 1);
			o += 4;
		}
	}
}

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
		if (cam_->acquire())
			return false;
		acquired_ = true;
		cfg_ = cam_->generateConfiguration({ StreamRole::Viewfinder });
		if (!cfg_ || cfg_->size() != 1 || cam_->configure(cfg_.get())) {
			stop();
			return false;
		}
		stream_ = cfg_->at(0).stream();
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
			const uint8_t *yb = map(pl[0].fd.get()), *cb = map(pl[1].fd.get());
			if (yb && cb) {
				dmaSync(pl[0].fd.get(), true);
				if (pl[1].fd.get() != pl[0].fd.get())
					dmaSync(pl[1].fd.get(), true);
				convert(yb + pl[0].offset, cb + pl[1].offset, frame_.data());
				if (pl[1].fd.get() != pl[0].fd.get())
					dmaSync(pl[1].fd.get(), false);
				dmaSync(pl[0].fd.get(), false);
				if (write(out_, frame_.data(), frame_.size()) != ssize_t(frame_.size()) && errno != EAGAIN)
					logmsg(std::string("loopback write: ") + strerror(errno));
				frames_++;
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
	std::unique_ptr<CameraConfiguration> cfg_;
	std::unique_ptr<FrameBufferAllocator> alloc_;
	Stream *stream_ = nullptr;
	std::vector<std::unique_ptr<Request>> reqs_;
	std::map<int, std::pair<void *, size_t>> maps_;
	bool acquired_ = false;
	std::atomic<bool> running_{ false }, stopping_{ false }, failed_{ false };
	unsigned long frames_ = 0;
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
}

int main()
{
	const char *d = getenv("SP11_WEBCAM_DEVICE");
	const std::string dev = d ? d : "/dev/video50";
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
	auto cam = cm.get("sp11-rear-ov13858-qualification");
	if (!cam) {
		logmsg("rear camera not found");
		return 1;
	}
	logmsg("ready on " + dev + " (1920x1080 YUYV, camera off until opened)");
	{
		Bridge br(cam, out);
		auto lastSeen = std::chrono::steady_clock::now();
		while (!gQuit) {
			int n = readers(dev);
			auto now = std::chrono::steady_clock::now();
			if (n > 0)
				lastSeen = now;
			if (n > 0 && !br.running()) {
				logmsg("reader detected; starting camera");
				if (!br.start())
					logmsg("camera start failed");
			} else if (br.running() && (br.failed() || now - lastSeen > std::chrono::seconds(4))) {
				logmsg(br.failed() ? "capture failure; stopping" : "no readers; stopping camera");
				br.stop();
			}
			std::this_thread::sleep_for(std::chrono::milliseconds(500));
		}
		br.stop();
	}
	cam.reset();
	cm.stop();
	close(out);
	return 0;
}
