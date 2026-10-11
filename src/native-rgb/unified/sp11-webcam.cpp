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
 * neutral offset, a cored unsharp mask and a motion-adaptive temporal filter,
 * plus edge-preserving luma/chroma noise reduction and a local tone mapper.
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
#include <cstddef>
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
#include <sys/socket.h>
#include <sys/un.h>
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
	float uGain = 1.0f, vGain = 1.0f; /* per-axis chroma gain on top of chromaGain */
	float sharpen = 0.0f, sharpenCore = 2.0f;
	float tnrStrength = 0.0f, tnrThreshold = 12.0f;
	float lumaNr = 0.0f;     /* half-scale sigma filter threshold, codes; 0 = off */
	float lumaCore = 0.0f;   /* full-scale detail coring, codes */
	float chromaNr = 0.0f;   /* quarter-scale luma-guided chroma filter edge threshold; 0 = off */
	float ltm = 0.0f;        /* local tone mapping strength; 0 = off */
	float ltmPivot = 110.0f; /* local level left unchanged */
	float ltmMaxGain = 2.5f, ltmMinGain = 0.85f;
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
			} else if (key == "u_gain") {
				s >> uGain;
			} else if (key == "v_gain") {
				s >> vGain;
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
			} else if (key == "luma_nr") {
				s >> lumaNr;
			} else if (key == "luma_core") {
				s >> lumaCore;
			} else if (key == "chroma_nr") {
				s >> chromaNr;
			} else if (key == "ltm") {
				s >> ltm;
			} else if (key == "ltm_pivot") {
				s >> ltmPivot;
			} else if (key == "ltm_max_gain") {
				s >> ltmMaxGain;
			} else if (key == "ltm_min_gain") {
				s >> ltmMinGain;
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
		uGain = std::clamp(uGain, 0.5f, 2.0f);
		vGain = std::clamp(vGain, 0.5f, 2.0f);
		sharpen = std::clamp(sharpen, 0.0f, 4.0f);
		tnrStrength = std::clamp(tnrStrength, 0.0f, 0.9f);
		tnrThreshold = std::clamp(tnrThreshold, 1.0f, 64.0f);
		lumaNr = std::clamp(lumaNr, 0.0f, 32.0f);
		lumaCore = std::clamp(lumaCore, 0.0f, 16.0f);
		chromaNr = std::clamp(chromaNr, 0.0f, 128.0f);
		ltm = std::clamp(ltm, 0.0f, 1.0f);
		ltmPivot = std::clamp(ltmPivot, 16.0f, 240.0f);
		ltmMaxGain = std::clamp(ltmMaxGain, 1.0f, 4.0f);
		ltmMinGain = std::clamp(ltmMinGain, 0.25f, 1.0f);
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
		y2_.assign(size_t(OW) * OH, 0);
		yh_.assign(size_t(HW) * HH, 0);
		yhs_.assign(size_t(HW) * HH, 0);
		for (auto *q : { &qu_, &qv_, &qum_, &qvm_, &qus_, &qvs_ })
			q->assign(size_t(QW) * HH, 128);
		u2_.assign(size_t(OW / 2) * OH, 128);
		v2_.assign(size_t(OW / 2) * OH, 128);
		grid_.assign(size_t(GW) * GH, 0.0f);
		gain_.assign(size_t(GW) * GH, 256);
		for (int d = 0; d < 256; d++) {
			const float T = std::max(look.chromaNr, 1.0f);
			cw_[d] = int(std::lround(16.0f * std::max(0.0f, 1.0f - float(d) / T)));
		}
		for (int n = 1; n < 26; n++)
			rec_[n] = 65536 / n;
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
			cu_[c] = uint8_t(std::clamp(int(std::lround(128 + look.chromaGain * look.uGain * (c - 128) + look.uOffset)), 0, 255));
			cv_[c] = uint8_t(std::clamp(int(std::lround(128 + look.chromaGain * look.vGain * (c - 128) + look.vOffset)), 0, 255));
		}
	}

	void run(const uint8_t *y, const uint8_t *uv, uint8_t *out)
	{
		const bool temporal = primed_ && look_.tnrStrength > 0.0f;
		bands([&](unsigned r0, unsigned r1) { pass1(y, uv, r0, r1, temporal); });
		primed_ = true;
		Yp_ = y_.data();
		Up_ = u_.data();
		Vp_ = v_.data();
		if (look_.lumaNr > 0.0f || look_.chromaNr > 0.0f) {
			bandsN(HH, [&](unsigned r0, unsigned r1) { down(r0, r1); });
			bandsN(HH, [&](unsigned r0, unsigned r1) { lowFilter(r0, r1); });
			if (look_.chromaNr > 0.0f)
				bandsN(HH, [&](unsigned r0, unsigned r1) { chromaGuided(r0, r1); });
			bands([&](unsigned r0, unsigned r1) { rebuild(r0, r1); });
			if (look_.lumaNr > 0.0f)
				Yp_ = y2_.data();
			if (look_.chromaNr > 0.0f) {
				Up_ = u2_.data();
				Vp_ = v2_.data();
			}
		}
		if (look_.ltm > 0.0f)
			localTone();
		bands([&](unsigned r0, unsigned r1) { pass2(out, r0, r1); });
	}

private:
	template<typename F>
	void bandsN(unsigned rows, F fn)
	{
		constexpr unsigned N = 4;
		std::thread t[N - 1];
		for (unsigned b = 1; b < N; b++)
			t[b - 1] = std::thread(fn, rows * b / N, rows * (b + 1) / N);
		fn(0, rows / N);
		for (auto &th : t)
			th.join();
	}
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


	static inline void sort2(int &a, int &b)
	{
		if (a > b)
			std::swap(a, b);
	}
	static inline int median9(int p[9])
	{
		sort2(p[1], p[2]); sort2(p[4], p[5]); sort2(p[7], p[8]);
		sort2(p[0], p[1]); sort2(p[3], p[4]); sort2(p[6], p[7]);
		sort2(p[1], p[2]); sort2(p[4], p[5]); sort2(p[7], p[8]);
		sort2(p[0], p[3]); sort2(p[5], p[8]); sort2(p[4], p[7]);
		sort2(p[3], p[6]); sort2(p[1], p[4]); sort2(p[2], p[5]);
		sort2(p[4], p[7]); sort2(p[4], p[2]); sort2(p[6], p[4]);
		sort2(p[4], p[2]);
		return p[4];
	}
	/*
	 * Two-scale noise reduction. Half scale (960x540): luma 2x2 means, then a
	 * 5x5 sigma filter (mean of neighbours within +-lumaNr) removes the blotchy
	 * low-frequency noise while keeping edges. Chroma goes to quarter scale
	 * (480x540 per plane), a 3x3 median removes colour speckles and a 5x5
	 * luma-guided mean smooths what is left without bleeding across edges.
	 * Full scale: luma = filtered half scale + cored fine detail; chroma is the
	 * filtered quarter scale, interpolated back.
	 */
	void down(unsigned r0, unsigned r1)
	{
		for (unsigned r = r0; r < r1; r++) {
			const uint8_t *a = &y_[size_t(2 * r) * OW], *b = a + OW;
			uint8_t *o = &yh_[size_t(r) * HW];
			for (unsigned x = 0; x < HW; x++)
				o[x] = uint8_t((a[2 * x] + a[2 * x + 1] + b[2 * x] + b[2 * x + 1] + 2) >> 2);
			const uint8_t *ua = &u_[size_t(2 * r) * CW], *ub = ua + CW;
			const uint8_t *va = &v_[size_t(2 * r) * CW], *vb = va + CW;
			uint8_t *ou = &qu_[size_t(r) * QW], *ov = &qv_[size_t(r) * QW];
			for (unsigned x = 0; x < QW; x++) {
				ou[x] = uint8_t((ua[2 * x] + ua[2 * x + 1] + ub[2 * x] + ub[2 * x + 1] + 2) >> 2);
				ov[x] = uint8_t((va[2 * x] + va[2 * x + 1] + vb[2 * x] + vb[2 * x + 1] + 2) >> 2);
			}
		}
	}
	void lowFilter(unsigned r0, unsigned r1)
	{
		const int T = std::max(1, int(look_.lumaNr));
		for (unsigned r = r0; r < r1; r++) {
			int rows[5];
			for (int k = 0; k < 5; k++)
				rows[k] = std::clamp(int(r) + k - 2, 0, int(HH) - 1);
			uint8_t *o = &yhs_[size_t(r) * HW];
			for (int x = 0; x < int(HW); x++) {
				const int c = yh_[size_t(r) * HW + x];
				int s = 0, n = 0;
				for (int ky = 0; ky < 5; ky++) {
					const uint8_t *q = &yh_[size_t(rows[ky]) * HW];
					for (int kx = -2; kx <= 2; kx++) {
						const int v = q[std::clamp(x + kx, 0, int(HW) - 1)];
						if (std::abs(v - c) <= T) {
							s += v;
							n++;
						}
					}
				}
				o[x] = uint8_t((s * rec_[n] + 32768) >> 16);
			}
			if (look_.chromaNr <= 0.0f)
				continue;
			const size_t ra = size_t(r ? r - 1 : r) * QW, rm = size_t(r) * QW,
				     rb = size_t(r + 1 < HH ? r + 1 : r) * QW;
			for (unsigned pl = 0; pl < 2; pl++) {
				const uint8_t *sp = pl ? qv_.data() : qu_.data();
				uint8_t *om = pl ? &qvm_[rm] : &qum_[rm];
				for (unsigned x = 0; x < QW; x++) {
					const unsigned xl = x ? x - 1 : x, xr = x + 1 < QW ? x + 1 : x;
					int pp[9] = { sp[ra + xl], sp[ra + x], sp[ra + xr], sp[rm + xl], sp[rm + x],
						      sp[rm + xr], sp[rb + xl], sp[rb + x], sp[rb + xr] };
					om[x] = uint8_t(median9(pp));
				}
			}
		}
	}
	void chromaGuided(unsigned r0, unsigned r1)
	{
		for (unsigned r = r0; r < r1; r++) {
			int rows[5];
			for (int k = 0; k < 5; k++)
				rows[k] = std::clamp(int(r) + k - 2, 0, int(HH) - 1);
			for (int x = 0; x < int(QW); x++) {
				const int yc = yh_[size_t(r) * HW + 2 * x];
				int su = 0, sv = 0, sw = 0;
				for (int ky = 0; ky < 5; ky++) {
					const size_t cr = size_t(rows[ky]) * QW, yr = size_t(rows[ky]) * HW;
					for (int kx = -2; kx <= 2; kx++) {
						const int xx = std::clamp(x + kx, 0, int(QW) - 1);
						const int w = cw_[std::abs(int(yh_[yr + 2 * xx]) - yc)];
						su += w * qum_[cr + xx];
						sv += w * qvm_[cr + xx];
						sw += w;
					}
				}
				const size_t o = size_t(r) * QW + x;
				qus_[o] = sw ? uint8_t((su + sw / 2) / sw) : qum_[o];
				qvs_[o] = sw ? uint8_t((sv + sw / 2) / sw) : qvm_[o];
			}
		}
	}
	/* 2x bilinear interpolation weights: output i -> source i0/i1, weights /4. */
	static inline void up2(int i, int n, int &i0, int &i1, int &w0, int &w1)
	{
		const int k = i >> 1;
		if (i & 1) {
			i0 = k; i1 = k + 1; w0 = 3; w1 = 1;
		} else {
			i0 = k - 1; i1 = k; w0 = 1; w1 = 3;
		}
		i0 = std::clamp(i0, 0, n - 1);
		i1 = std::clamp(i1, 0, n - 1);
	}
	void rebuild(unsigned r0, unsigned r1)
	{
		const int core = int(look_.lumaCore);
		const bool luma = look_.lumaNr > 0.0f, chroma = look_.chromaNr > 0.0f;
		for (unsigned r = r0; r < r1; r++) {
			int a0, a1, b0, b1;
			up2(int(r), int(HH), a0, a1, b0, b1);
			if (luma) {
				const uint8_t *m = &y_[size_t(r) * OW];
				const uint8_t *h0 = &yh_[size_t(a0) * HW], *h1 = &yh_[size_t(a1) * HW];
				const uint8_t *s0 = &yhs_[size_t(a0) * HW], *s1 = &yhs_[size_t(a1) * HW];
				uint8_t *o = &y2_[size_t(r) * OW];
				for (int x = 0; x < int(OW); x++) {
					int c0, c1, d0, d1;
					up2(x, int(HW), c0, c1, d0, d1);
					const int low = (b0 * (d0 * h0[c0] + d1 * h0[c1]) + b1 * (d0 * h1[c0] + d1 * h1[c1]) + 8) >> 4;
					const int lows = (b0 * (d0 * s0[c0] + d1 * s0[c1]) + b1 * (d0 * s1[c0] + d1 * s1[c1]) + 8) >> 4;
					int det = m[x] - low;
					det = det > core ? det - core : det < -core ? det + core : 0;
					o[x] = uint8_t(std::clamp(lows + det, 0, 255));
				}
			}
			if (chroma) {
				const uint8_t *u0 = &qus_[size_t(a0) * QW], *u1 = &qus_[size_t(a1) * QW];
				const uint8_t *v0 = &qvs_[size_t(a0) * QW], *v1 = &qvs_[size_t(a1) * QW];
				uint8_t *ou = &u2_[size_t(r) * CW], *ov = &v2_[size_t(r) * CW];
				for (int x = 0; x < int(CW); x++) {
					int c0, c1, d0, d1;
					up2(x, int(QW), c0, c1, d0, d1);
					ou[x] = uint8_t((b0 * (d0 * u0[c0] + d1 * u0[c1]) + b1 * (d0 * u1[c0] + d1 * u1[c1]) + 8) >> 4);
					ov[x] = uint8_t((b0 * (d0 * v0[c0] + d1 * v0[c1]) + b1 * (d0 * v1[c0] + d1 * v1[c1]) + 8) >> 4);
				}
			}
		}
	}
	/*
	 * Local tone mapping: the local level (8x8 block means, blurred over about
	 * 1/10 of the frame) sets a gain pivoting at ltmPivot: darker areas are
	 * lifted, brighter ones compressed, so a bright window and a dim room both
	 * keep detail. Gains are interpolated per pixel in pass2.
	 */
	void localTone()
	{
		const uint8_t *Y = Yp_;
		for (unsigned gy = 0; gy < GH; gy++)
			for (unsigned gx = 0; gx < GW; gx++) {
				unsigned s = 0;
				for (unsigned r = gy * 8; r < gy * 8 + 8; r += 2) {
					const uint8_t *q = Y + size_t(r) * OW + gx * 8;
					s += q[0] + q[2] + q[4] + q[6];
				}
				grid_[gy * GW + gx] = s / 16.0f;
			}
		/* separable box blur, radius 6 cells, twice */
		std::vector<float> tmp(grid_.size());
		for (int pass = 0; pass < 2; pass++) {
			for (unsigned gy = 0; gy < GH; gy++)
				for (int gx = 0; gx < int(GW); gx++) {
					float s = 0;
					for (int k = -6; k <= 6; k++)
						s += grid_[gy * GW + std::clamp(gx + k, 0, int(GW) - 1)];
					tmp[gy * GW + gx] = s / 13.0f;
				}
			for (int gy = 0; gy < int(GH); gy++)
				for (unsigned gx = 0; gx < GW; gx++) {
					float s = 0;
					for (int k = -6; k <= 6; k++)
						s += tmp[std::clamp(gy + k, 0, int(GH) - 1) * GW + gx];
					grid_[gy * GW + gx] = s / 13.0f;
				}
		}
		const float piv = look_.ltmPivot + 8.0f;
		for (size_t i = 0; i < grid_.size(); i++) {
			const float g = std::pow((grid_[i] + 8.0f) / piv, -look_.ltm);
			gain_[i] = int(std::lround(256.0f * std::clamp(g, look_.ltmMinGain, look_.ltmMaxGain)));
		}
	}
	int gainAt(unsigned x, unsigned r) const
	{
		const float fx = std::clamp((float(x) - 3.5f) / 8.0f, 0.0f, float(GW - 1));
		const float fy = std::clamp((float(r) - 3.5f) / 8.0f, 0.0f, float(GH - 1));
		const unsigned x0 = std::min(unsigned(fx), GW - 2), y0 = std::min(unsigned(fy), GH - 2);
		const float ax = fx - x0, ay = fy - y0;
		const int *g = &gain_[y0 * GW + x0];
		return int((g[0] * (1 - ax) + g[1] * ax) * (1 - ay) + (g[GW] * (1 - ax) + g[GW + 1] * ax) * ay);
	}

	void pass2(uint8_t *out, unsigned r0, unsigned r1) const
	{
		const bool sharpen = look_.sharpen > 0.0f;
		for (unsigned r = r0; r < r1; r++) {
			const uint8_t *m = &Yp_[size_t(r) * OW];
			const uint8_t *a = r ? m - OW : m, *b = r + 1 < OH ? m + OW : m;
			const uint8_t *u = &Up_[size_t(r) * (OW / 2)], *v = &Vp_[size_t(r) * (OW / 2)];
			uint8_t *o = out + size_t(r) * OW * 2;
			const bool tone = look_.ltm > 0.0f;
			for (unsigned x = 0; x < OW; x++) {
				int val = m[x];
				if (sharpen && x > 0 && x + 1 < OW) {
					const int sum = a[x - 1] + a[x] + a[x + 1] + m[x - 1] + m[x] + m[x + 1] +
							b[x - 1] + b[x] + b[x + 1];
					const int blur = (sum * 7282 + 32768) >> 16; /* /9 */
					val = std::clamp(val + sharp_[val - blur + 255], 0, 255);
				}
				if (tone) {
					const int g = gainAt(x, r);
					/* lift fades out towards white so whites stay white */
					if (g > 256)
						val += (((val * (g - 256)) >> 8) * (255 - val)) / 255;
					else
						val = (val * g + 128) >> 8;
				}
				o[2 * x] = uint8_t(val);
			}
			for (unsigned x = 0; x < OW / 2; x++) {
				int cu = u[x], cv = v[x];
				if (tone) {
					/* keep saturation roughly with the luma gain */
					const int g = gainAt(2 * x, r);
					const int gc = int(std::sqrt(float(g) * 256.0f));
					cu = std::clamp(128 + (((cu - 128) * gc) >> 8), 0, 255);
					cv = std::clamp(128 + (((cv - 128) * gc) >> 8), 0, 255);
				}
				o[4 * x + 1] = uint8_t(cu);
				o[4 * x + 3] = uint8_t(cv);
			}
		}
	}

	static constexpr unsigned GW = OW / 8, GH = OH / 8;
	static constexpr unsigned CW = OW / 2, HW = OW / 2, HH = OH / 2, QW = OW / 4;
	unsigned ys_ = 0;
	Axis yx_, yy_, cx_, cy_;
	std::vector<uint8_t> y2_, u2_, v2_, yh_, yhs_, qu_, qv_, qum_, qvm_, qus_, qvs_;
	const uint8_t *Yp_ = nullptr, *Up_ = nullptr, *Vp_ = nullptr;
	std::vector<float> grid_;
	std::vector<int> gain_;
	int cw_[256] = {}, rec_[26] = {};
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
			if (++wait_ < kSettleFrames - 1)
				break;
			acc_ += m;
			if (wait_ < kSettleFrames)
				break;
			wait_ = 0;
			scores_.push_back({ pos_, acc_ / 2.0 });
			acc_ = 0.0;
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
	/*
	 * Focus measure: 4x4 block means over the centre half of the native frame,
	 * summed absolute differences between neighbouring blocks (both axes),
	 * normalised by the mean level. Block means suppress sensor noise, which
	 * otherwise dominates pixel-level gradients at 4K and hides the peak.
	 */
	static double metric(const uint8_t *y, unsigned w, unsigned h, unsigned stride, double *mean)
	{
		const unsigned x0 = w / 4, nb = (w / 2) / 4, y0 = h / 4, nr = (h / 2) / 4;
		std::vector<uint32_t> cur(nb), prev(nb);
		uint64_t g = 0, s = 0;
		for (unsigned j = 0; j < nr; j++) {
			std::fill(cur.begin(), cur.end(), 0u);
			for (unsigned k = 0; k < 4; k++) {
				const uint8_t *row = y + size_t(y0 + 4 * j + k) * stride + x0;
				for (unsigned i = 0; i < nb; i++)
					cur[i] += row[4 * i] + row[4 * i + 1] + row[4 * i + 2] + row[4 * i + 3];
			}
			for (unsigned i = 0; i < nb; i++) {
				s += cur[i];
				if (i)
					g += unsigned(std::abs(int(cur[i]) - int(cur[i - 1])));
				if (j)
					g += unsigned(std::abs(int(cur[i]) - int(prev[i])));
			}
			std::swap(cur, prev);
		}
		*mean = nb && nr ? double(s) / (16.0 * nb * nr) : 0.0;
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
		acc_ = 0.0;
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
	double ref_ = 0, refMean_ = 0, lastMetric_ = 0, lastMean_ = 0, acc_ = 0;
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

/* systemd readiness (Type=notify): the loopback is configured as a webcam. */
void notifyReady()
{
	const char *path = std::getenv("NOTIFY_SOCKET");
	if (!path || (path[0] != '/' && path[0] != '@'))
		return;
	sockaddr_un sa{};
	sa.sun_family = AF_UNIX;
	const size_t len = std::min(strlen(path), sizeof(sa.sun_path) - 1);
	memcpy(sa.sun_path, path, len);
	if (sa.sun_path[0] == '@')
		sa.sun_path[0] = 0;
	int s = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
	if (s < 0)
		return;
	const char msg[] = "READY=1";
	sendto(s, msg, sizeof(msg) - 1, 0, reinterpret_cast<sockaddr *>(&sa),
	       socklen_t(offsetof(sockaddr_un, sun_path) + len));
	close(s);
}

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
	notifyReady();
	/* both bridges enumerate the same media device; one may start later */
	if (const char *d = std::getenv("SP11_WEBCAM_LOOKUP_DELAY"))
		std::this_thread::sleep_for(std::chrono::milliseconds(int(1000 * std::clamp(std::atof(d), 0.0, 30.0))));
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
