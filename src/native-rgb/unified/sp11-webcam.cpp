/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * sp11-webcam: on-demand bridge from one SP11 camera (libcamera, native
 * camss-x1e front or camss-x1e-rear pipeline, NV12) to a v4l2loopback device
 * that ordinary applications use as a webcam (1920x1080 YUYV, 30 fps).
 *
 * Usage: sp11-webcam <libcamera camera id> <loopback device> [look file]
 * One instance per camera. The camera runs only while another process holds the
 * loopback device open and is released a few seconds after the last reader
 * closes it. Both cameras share one media device, so only one can stream at a
 * time; a start that finds the other camera busy is retried.
 *
 * The optional look file (fit-look.py, measured against a same-scene Windows
 * capture) sets the output rendering: a luma tone table, chroma gain and
 * neutral offset, a cored unsharp mask and a motion-adaptive temporal filter.
 * With "af 1" (rear camera) the bridge also drives the lens: see Focus.
 */
#include <algorithm>
#include <atomic>
#include <cerrno>
#include <chrono>
#include <cmath>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <linux/dma-buf.h>
#include <linux/i2c-dev.h>
#include <linux/videodev2.h>
#include <map>
#include <memory>
#include <mutex>
#include <sstream>
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

/* Output rendering. Defaults are the identity. */
struct Look {
	uint8_t lut[256];
	float chromaGain = 1.0f, uOffset = 0.0f, vOffset = 0.0f;
	float sharpen = 0.0f, sharpenCore = 2.0f;
	float tnrStrength = 0.0f, tnrThreshold = 12.0f;
	bool af = false;
	int afMin = 380, afMax = 900, afStart = 520;
	Look()
	{
		for (unsigned i = 0; i < 256; i++)
			lut[i] = uint8_t(i);
	}
	bool load(const std::string &path)
	{
		std::ifstream in(path);
		if (!in)
			return false;
		std::string line;
		while (std::getline(in, line)) {
			std::istringstream s(line);
			std::string key;
			if (!(s >> key) || key[0] == '#')
				continue;
			if (key == "lut") {
				for (unsigned i = 0; i < 256; i++) {
					int v;
					if (!(s >> v))
						return false;
					lut[i] = uint8_t(std::clamp(v, 0, 255));
				}
			} else if (key == "chroma_gain") {
				s >> chromaGain;
			} else if (key == "u_offset") {
				s >> uOffset;
			} else if (key == "v_offset") {
				s >> vOffset;
			} else if (key == "sharpen") {
				s >> sharpen;
			} else if (key == "sharpen_core") {
				s >> sharpenCore;
			} else if (key == "tnr_strength") {
				s >> tnrStrength;
			} else if (key == "tnr_threshold") {
				s >> tnrThreshold;
			} else if (key == "af") {
				int v = 0;
				s >> v;
				af = v != 0;
			} else if (key == "af_min") {
				s >> afMin;
			} else if (key == "af_max") {
				s >> afMax;
			} else if (key == "af_start") {
				s >> afStart;
			}
		}
		chromaGain = std::clamp(chromaGain, 0.0f, 3.0f);
		sharpen = std::clamp(sharpen, 0.0f, 4.0f);
		tnrStrength = std::clamp(tnrStrength, 0.0f, 0.9f);
		tnrThreshold = std::clamp(tnrThreshold, 1.0f, 64.0f);
		afMin = std::clamp(afMin, 0, 1023);
		afMax = std::clamp(afMax, afMin, 1023);
		afStart = std::clamp(afStart, afMin, afMax);
		return true;
	}
};

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

/*
 * NV12 (any size) -> rendered YUYV 4:2:2 at OW x OH. Rows are processed in
 * parallel bands; the temporal filter keeps its state per output sample.
 */
class Renderer
{
public:
	void setup(unsigned w, unsigned h, unsigned stride, const Look &look)
	{
		ys_ = stride;
		yx_.build(w, OW);
		yy_.build(h, OH);
		cx_.build(w / 2, OW / 2);
		cy_.build(h / 2, OH);
		look_ = look;
		y_.assign(size_t(OW) * OH, 0);
		u_.assign(size_t(OW / 2) * OH, 128);
		v_.assign(size_t(OW / 2) * OH, 128);
		prevY_.assign(size_t(OW) * OH, 0);
		prevU_.assign(size_t(OW / 2) * OH, 0);
		prevV_.assign(size_t(OW / 2) * OH, 0);
		primed_ = false;
		for (unsigned d = 0; d < 256; d++) {
			float w = look.tnrStrength * std::max(0.0f, 1.0f - float(d) / look.tnrThreshold);
			tnr_[d] = int(std::lround(w * 256.0f));
			/* chroma noise is smaller in code values: half the threshold */
			float wc = look.tnrStrength * std::max(0.0f, 1.0f - float(d) / (0.5f * look.tnrThreshold));
			tnrC_[d] = int(std::lround(wc * 256.0f));
		}
		for (int d = -255; d <= 255; d++) {
			float c = std::max(0.0f, std::fabs(float(d)) - look.sharpenCore);
			sharp_[d + 255] = int(std::lround(look.sharpen * (d < 0 ? -c : c)));
		}
		for (int c = 0; c < 256; c++) {
			cu_[c] = uint8_t(std::clamp(int(std::lround(128 + look.chromaGain * (c - 128) + look.uOffset)), 0, 255));
			cv_[c] = uint8_t(std::clamp(int(std::lround(128 + look.chromaGain * (c - 128) + look.vOffset)), 0, 255));
		}
	}

	void run(const uint8_t *y, const uint8_t *uv, uint8_t *out)
	{
		const bool temporal = primed_ && look_.tnrStrength > 0.0f;
		bands([&](unsigned r0, unsigned r1) { pass1(y, uv, r0, r1, temporal); });
		primed_ = true;
		bands([&](unsigned r0, unsigned r1) { pass2(out, r0, r1); });
	}

private:
	template<typename F>
	void bands(F fn)
	{
		constexpr unsigned N = 4;
		std::thread t[N - 1];
		for (unsigned b = 1; b < N; b++)
			t[b - 1] = std::thread(fn, OH * b / N, OH * (b + 1) / N);
		fn(0, OH / N);
		for (auto &th : t)
			th.join();
	}

	static inline uint8_t filt(int cur, uint16_t &prev, const int *table)
	{
		/* prev is Q8; blend toward it where the change is small */
		int c = cur << 8, p = prev;
		int d = std::abs(c - p) >> 8;
		int w = table[std::min(d, 255)];
		int o = c + (((p - c) * w) >> 8);
		prev = uint16_t(o);
		return uint8_t((o + 128) >> 8);
	}

	void pass1(const uint8_t *y, const uint8_t *uv, unsigned r0, unsigned r1, bool temporal)
	{
		for (unsigned r = r0; r < r1; r++) {
			const uint8_t *y0 = y + size_t(yy_.i0[r]) * ys_, *y1 = y0 + ys_;
			const unsigned wy = yy_.w1[r];
			const uint8_t *c0 = uv + size_t(cy_.i0[r]) * ys_, *c1 = c0 + ys_;
			const unsigned wc = cy_.w1[r];
			uint8_t *oy = &y_[size_t(r) * OW];
			uint16_t *py = &prevY_[size_t(r) * OW];
			for (unsigned x = 0; x < OW; x++) {
				const unsigned a = yx_.i0[x], wx = yx_.w1[x];
				const unsigned t = y0[a] * (256 - wx) + y0[a + 1] * wx;
				const unsigned b = y1[a] * (256 - wx) + y1[a + 1] * wx;
				int v = int((t * (256 - wy) + b * wy + 32768) >> 16);
				if (temporal)
					v = filt(v, py[x], tnr_);
				else
					py[x] = uint16_t(v << 8);
				oy[x] = look_.lut[v];
			}
			uint8_t *ou = &u_[size_t(r) * (OW / 2)], *ov = &v_[size_t(r) * (OW / 2)];
			uint16_t *pu = &prevU_[size_t(r) * (OW / 2)], *pv = &prevV_[size_t(r) * (OW / 2)];
			for (unsigned x = 0; x < OW / 2; x++) {
				const unsigned a = 2 * cx_.i0[x], wx = cx_.w1[x];
				int s[2];
				for (unsigned k = 0; k < 2; k++) {
					const unsigned t = c0[a + k] * (256 - wx) + c0[a + 2 + k] * wx;
					const unsigned b = c1[a + k] * (256 - wx) + c1[a + 2 + k] * wx;
					s[k] = int((t * (256 - wc) + b * wc + 32768) >> 16);
				}
				if (temporal) {
					s[0] = filt(s[0], pu[x], tnrC_);
					s[1] = filt(s[1], pv[x], tnrC_);
				} else {
					pu[x] = uint16_t(s[0] << 8);
					pv[x] = uint16_t(s[1] << 8);
				}
				ou[x] = cu_[s[0]];
				ov[x] = cv_[s[1]];
			}
		}
	}

	void pass2(uint8_t *out, unsigned r0, unsigned r1) const
	{
		const bool sharpen = look_.sharpen > 0.0f;
		for (unsigned r = r0; r < r1; r++) {
			const uint8_t *m = &y_[size_t(r) * OW];
			const uint8_t *a = r ? m - OW : m, *b = r + 1 < OH ? m + OW : m;
			const uint8_t *u = &u_[size_t(r) * (OW / 2)], *v = &v_[size_t(r) * (OW / 2)];
			uint8_t *o = out + size_t(r) * OW * 2;
			for (unsigned x = 0; x < OW; x++) {
				int val = m[x];
				if (sharpen && x > 0 && x + 1 < OW) {
					const int sum = a[x - 1] + a[x] + a[x + 1] + m[x - 1] + m[x] + m[x + 1] +
							b[x - 1] + b[x] + b[x + 1];
					const int blur = (sum * 7282 + 32768) >> 16; /* /9 */
					val = std::clamp(val + sharp_[val - blur + 255], 0, 255);
				}
				o[2 * x] = uint8_t(val);
			}
			for (unsigned x = 0; x < OW / 2; x++) {
				o[4 * x + 1] = u[x];
				o[4 * x + 3] = v[x];
			}
		}
	}

	unsigned ys_ = 0;
	Axis yx_, yy_, cx_, cy_;
	Look look_;
	std::vector<uint8_t> y_, u_, v_;
	std::vector<uint16_t> prevY_, prevU_, prevV_;
	bool primed_ = false;
	int tnr_[256] = {}, tnrC_[256] = {}, sharp_[511] = {};
	uint8_t cu_[256] = {}, cv_[256] = {};
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

/*
 * Rear lens: a DW9800 voice-coil actuator at 0x0c on the rear sensor's CCI bus,
 * powered from the camera VAF rail through the sp11-rear-vaf regulator-output
 * device (only while the rear camera streams; the bus is usable only while the
 * sensor is powered, so the actuator is set up on the first frames).
 * Contrast autofocus on the native frames: normalised horizontal gradient
 * energy of the centre region, a coarse then a fine sweep over the useful code
 * range, then hold. A lasting drop in sharpness or a large brightness change
 * re-runs the sweep once the scene is steady again.
 */
class Focus
{
public:
	void configure(const Look &l)
	{
		enabled_ = l.af;
		min_ = l.afMin;
		max_ = l.afMax;
		best_ = l.afStart;
	}
	void begin()
	{
		active_ = false;
		if (!enabled_)
			return;
		bus_ = findBus();
		if (bus_ < 0 || !power(true)) {
			logmsg("focus: lens supply or rear bus not available; fixed focus");
			return;
		}
		active_ = true;
		ready_ = false;
		n_ = 0;
	}
	void end()
	{
		std::lock_guard<std::mutex> lock(mu_);
		if (fd_ >= 0) {
			/* ease the lens back towards its rest before the supply goes */
			for (int p = pos_; p > min_; p -= 40) {
				move(p);
				usleep(3000);
			}
			move(min_);
			usleep(3000);
			close(fd_);
			fd_ = -1;
		}
		if (active_ || powered_)
			power(false);
		active_ = false;
	}
	/* Once per delivered frame, from the completion thread. */
	void frame(const uint8_t *y, unsigned w, unsigned h, unsigned stride)
	{
		std::lock_guard<std::mutex> lock(mu_);
		if (!active_)
			return;
		n_++;
		double mean;
		const double m = metric(y, w, h, stride, &mean);
		if (!ready_) {
			if (n_ < 4)
				return;
			if (!init()) {
				active_ = false;
				power(false);
				return;
			}
			ready_ = true;
			move(best_);
			wait_ = 0;
			state_ = Settle;
			return;
		}
		switch (state_) {
		case Settle:
			/* auto exposure converges first */
			if (n_ >= 12)
				sweep(min_, max_, 48);
			break;
		case Sweep:
			if (++wait_ < kSettleFrames)
				break;
			wait_ = 0;
			scores_.push_back({ pos_, m });
			if (next_ < plan_.size()) {
				move(plan_[next_++]);
				break;
			}
			done(m);
			break;
		case Hold:
			monitor(m, mean);
			break;
		}
		lastMean_ = mean;
	}

private:
	enum State { Settle, Sweep, Hold };
	static constexpr unsigned kSettleFrames = 3;

	static int findBus()
	{
		DIR *d = opendir("/sys/bus/i2c/devices");
		if (!d)
			return -1;
		int bus = -1;
		while (dirent *e = readdir(d)) {
			std::string n = e->d_name;
			if (n.size() < 6 || n.compare(n.size() - 5, 5, "-0010"))
				continue;
			std::ifstream c("/sys/bus/i2c/devices/" + n + "/of_node/compatible");
			std::string v;
			std::getline(c, v, '\0');
			if (v == "ovti,ov13858")
				bus = std::atoi(n.c_str());
		}
		closedir(d);
		return bus;
	}
	bool power(bool on)
	{
		std::ofstream s("/sys/devices/platform/sp11-rear-vaf/state");
		if (!s)
			return false;
		s << (on ? "enabled" : "disabled");
		s.flush();
		powered_ = on && bool(s);
		return bool(s);
	}
	bool init()
	{
		const std::string p = "/dev/i2c-" + std::to_string(bus_);
		fd_ = open(p.c_str(), O_RDWR);
		if (fd_ < 0 || ioctl(fd_, I2C_SLAVE, 0x0c) < 0) {
			logmsg("focus: cannot open " + p + "; fixed focus");
			return false;
		}
		const uint8_t ctl[2] = { 0x02, 0x00 }; /* active, direct drive */
		if (write(fd_, ctl, 2) != 2) {
			logmsg(std::string("focus: actuator not responding (") + strerror(errno) + "); fixed focus");
			close(fd_);
			fd_ = -1;
			return false;
		}
		return true;
	}
	void move(int p)
	{
		p = std::clamp(p, 0, 1023);
		const uint8_t b[3] = { 0x03, uint8_t(p >> 8), uint8_t(p & 0xff) };
		if (fd_ >= 0 && write(fd_, b, 3) == 3)
			pos_ = p;
	}
	/* Normalised gradient energy of the centre half, every 4th row. */
	static double metric(const uint8_t *y, unsigned w, unsigned h, unsigned stride, double *mean)
	{
		uint64_t g = 0, s = 0, n = 0;
		for (unsigned r = h / 4; r < 3 * h / 4; r += 4) {
			const uint8_t *row = y + size_t(r) * stride;
			for (unsigned x = w / 4; x < 3 * w / 4; x++) {
				g += unsigned(std::abs(int(row[x + 1]) - int(row[x])));
				s += row[x];
			}
			n += w / 2;
		}
		*mean = n ? double(s) / n : 0.0;
		return s ? double(g) / double(s) : 0.0;
	}
	void sweep(int lo, int hi, int step)
	{
		plan_.clear();
		scores_.clear();
		for (int p = std::max(lo, min_); p <= std::min(hi, max_); p += step)
			plan_.push_back(p);
		fine_ = step < 48;
		next_ = 1;
		wait_ = 0;
		move(plan_[0]);
		state_ = Sweep;
	}
	void done(double)
	{
		auto best = std::max_element(scores_.begin(), scores_.end(),
					     [](const auto &a, const auto &b) { return a.second < b.second; });
		auto worst = std::min_element(scores_.begin(), scores_.end(),
					      [](const auto &a, const auto &b) { return a.second < b.second; });
		const bool flat = best->second <= 0 || (best->second - worst->second) / best->second < 0.04;
		if (!fine_) {
			if (flat) {
				/* no contrast to focus on: keep the previous position */
				move(best_);
				hold();
				logmsg("focus: low contrast, holding " + std::to_string(best_));
				return;
			}
			sweep(best->first - 48, best->first + 48, 12);
			return;
		}
		best_ = best->first;
		move(best_);
		hold();
		logmsg("focus: position " + std::to_string(best_) + " contrast " + std::to_string(best->second));
	}
	void hold()
	{
		state_ = Hold;
		ref_ = 0;
		refMean_ = 0;
		refN_ = 0;
		bad_ = 0;
		steady_ = 0;
		lastSweep_ = n_;
	}
	void monitor(double m, double mean)
	{
		if (refN_ < 6) {
			/* reference: average of the first frames at the chosen position */
			if (refN_ >= kSettleFrames) {
				ref_ += m;
				refMean_ += mean;
			}
			if (++refN_ == 6) {
				ref_ /= 6 - kSettleFrames;
				refMean_ /= 6 - kSettleFrames;
			}
			return;
		}
		const bool changed = m < 0.75 * ref_ ||
				     (refMean_ > 1 && std::fabs(mean / refMean_ - 1.0) > 0.3);
		bad_ = changed ? bad_ + 1 : 0;
		if (bad_ < 20) {
			steady_ = 0;
			lastMetric_ = m;
			return;
		}
		/* the scene changed: wait until it is steady, at most one sweep per 3 s */
		steady_ = std::fabs(m - lastMetric_) < 0.06 * std::max(m, 1e-6) ? steady_ + 1 : 0;
		lastMetric_ = m;
		if (steady_ >= 8 && n_ - lastSweep_ > 90)
			sweep(min_, max_, 48);
	}

	std::mutex mu_;
	bool enabled_ = false, active_ = false, ready_ = false, fine_ = false, powered_ = false;
	int bus_ = -1, fd_ = -1, min_ = 380, max_ = 900, best_ = 520, pos_ = 0;
	State state_ = Settle;
	unsigned long n_ = 0, lastSweep_ = 0;
	unsigned wait_ = 0, refN_ = 0, bad_ = 0, steady_ = 0;
	size_t next_ = 0;
	std::vector<int> plan_;
	std::vector<std::pair<int, double>> scores_;
	double ref_ = 0, refMean_ = 0, lastMetric_ = 0, lastMean_ = 0;
};

class Bridge
{
public:
	Bridge(std::shared_ptr<Camera> cam, int out, const Look &look)
		: cam_(std::move(cam)), out_(out), frame_(OUT_BYTES), look_(look)
	{
		focus_.configure(look_);
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
		render_.setup(sc.size.width, sc.size.height, sc.stride, look_);
		width_ = sc.size.width;
		height_ = sc.size.height;
		stride_ = sc.stride;
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
		focus_.begin();
		if (cam_->start(&c)) {
			focus_.end();
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
			focus_.end(); /* while the sensor, and so the lens bus, is powered */
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
				focus_.frame(yb + pl[0].offset, width_, height_, stride_);
				render_.run(yb + pl[0].offset, cb + pl[1].offset, frame_.data());
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
	Look look_;
	Renderer render_;
	Focus focus_;
	unsigned width_ = 0, height_ = 0, stride_ = 0;
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
	if (argc != 3 && argc != 4) {
		std::cerr << "usage: sp11-webcam <camera id> <loopback device> [look file]" << std::endl;
		return 2;
	}
	const std::string id = argv[1], dev = argv[2];
	gTag = "sp11-webcam[" + id + "]";
	signal(SIGTERM, [](int) { gQuit = true; });
	signal(SIGINT, [](int) { gQuit = true; });
	Look look;
	if (argc == 4) {
		if (look.load(argv[3]))
			logmsg(std::string("look ") + argv[3]);
		else
			logmsg(std::string("cannot read look ") + argv[3] + "; using identity rendering");
	}
	int out = openLoopback(dev);
	if (out < 0) {
		logmsg("cannot open/configure " + dev);
		return 1;
	}
	/*
	 * The loopback stays open (and so stays a capture device for PipeWire)
	 * while the camera is looked up. At boot both bridges enumerate the same
	 * media device at once and one may find a node busy: retry instead of
	 * exiting, which would hide the device from applications that already
	 * enumerated it.
	 */
	std::unique_ptr<CameraManager> cm;
	std::shared_ptr<Camera> cam;
	for (unsigned attempt = 0; !gQuit && !cam; attempt++) {
		cm = std::make_unique<CameraManager>();
		if (!cm->start())
			cam = cm->get(id);
		if (cam)
			break;
		cm.reset();
		if (attempt == 60) {
			logmsg("camera not found");
			close(out);
			return 1;
		}
		if (attempt == 0)
			logmsg("camera not available yet; retrying");
		std::this_thread::sleep_for(std::chrono::milliseconds(1000 + 250 * (attempt % 4)));
	}
	if (!cam) {
		close(out);
		return 0;
	}
	logmsg("ready on " + dev + " (1920x1080 YUYV, camera off until opened)");
	{
		Bridge br(cam, out, look);
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
	cm->stop();
	close(out);
	return 0;
}
