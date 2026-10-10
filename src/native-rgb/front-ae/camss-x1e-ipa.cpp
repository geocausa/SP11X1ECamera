/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * SP11 front (imx681) IPA: hardware-statistics metering, automatic exposure
 * and independently measured tone curves.
 *
 * Metering: by default the equal-weight raw Gr/Gb mean of the 32x32 BE grid
 * is held at ae_target. With ae_output_target set, exposure is instead chosen
 * so that the mean displayed green of the 1024 BE regions (each region's green
 * mapped through the programmed green tone LUT) reaches the target, so a
 * bright window or display in the scene no longer darkens everything else.
 * Optionally the displayed target rises from ae_output_target in bright
 * scenes to ae_output_target_dark in dim ones (scene level = meter luma at
 * full-frame exposure and unity gain, interpolated in log between
 * ae_lux_bright and ae_lux_dark), as measured for the Windows reference.
 * A highlight guard (ae_highlight_percentile/ae_highlight_target) lowers
 * exposure when a large bright area (above that region percentile) would be
 * displayed brighter than the guard level; small bright areas may clip.
 * Automatic exposure scales the exposure/gain product of the frame the
 * statistics came from (its applied sensor controls are supplied by the
 * pipeline), so each estimate is self-consistent despite the sensor's
 * two-frame control delay.
 * White balance (awb_ref_rg/awb_ref_bg set): the frame red/green and
 * blue/green statistic ratios are compared with those of the calibration
 * scene, and the red and blue tone LUTs are rescaled by the smoothed ratio
 * (grey world anchored to the measured reference), so the calibrated look is
 * kept under the calibration light and neutrals follow other lights.
 * Exposure is used up to the 30 fps frame time, then analogue gain, then
 * (ae_max_exposure_low) a longer frame time down to the measured 15 fps
 * limit, then a
 * bounded digital gain. Red/blue means are reported for white-balance work.
 */
#include <algorithm>
#include <array>
#include <cerrno>
#include <cmath>
#include <cstdint>
#include <map>
#include <memory>
#include <vector>

#include <libcamera/ipa/camss_x1e_ipa_interface.h>
#include <libcamera/ipa/ipa_module_info.h>

#include <libcamera/base/file.h>
#include "libcamera/internal/yaml_parser.h"
#include "libcamera/internal/mapped_framebuffer.h"
extern "C" {
#include "libipa/native-front-isp-params.h"
}
#include "libipa/camss_x1e_helpers.h"
#include "libipa/front-aec-decoder.h"

namespace libcamera {

namespace {
constexpr int32_t kMinExposure = 4;
constexpr int32_t kMaxExposure = 3550; /* 3554-line frame at 30 fps, minus margin. */
constexpr int32_t kMaxAnalogueCode = 960; /* 16x */
double analogueGain(int32_t code) { return 1024.0 / (1024 - code); }
}

class IPACamssX1E final : public ipa::camss_x1e::IPACamssX1EInterface
{
public:
	int init(const IPASettings &settings) override
	{
		if (running_ || !buffers_.empty() || settings.sensorModel != "imx681")
			return -EINVAL;
		std::vector<uint8_t> candidate(NF_ISP_HEADER_BYTES);
		int ret = native_front_isp_encode(nullptr, 0, candidate.data(), candidate.size());
		if (!settings.configurationFile.empty()) {
			File file(settings.configurationFile);
			if (!file.open(File::OpenModeFlag::ReadOnly))
				return file.error();
			auto data = YamlParser::parse(file);
			if (!data || !data->isDictionary() ||
			    (*data)["version"].get<uint32_t>(0) != 1 ||
			    (*data)["sensor"].get<std::string>("") != "imx681" ||
			    (*data)["layout"].get<std::string>("") != "rgb257-u10")
				return -EINVAL;
			std::array<uint16_t, NF_GAMMA_POINT_COUNT> points{};
			size_t at = 0;
			for (const char *key : { "gamma_r", "gamma_g", "gamma_b" }) {
				auto values = (*data)[key].getList<uint16_t>();
				if (!values || values->size() != NF_GAMMA_POINTS)
					return -EINVAL;
				for (uint16_t value : *values)
					points[at++] = value;
			}
			baseLut_ = points;
			if (data->contains("awb_ref_rg")) {
				awbRefRg_ = (*data)["awb_ref_rg"].get<double>(0.0);
				awbRefBg_ = (*data)["awb_ref_bg"].get<double>(0.0);
				awbSpeed_ = (*data)["awb_speed"].get<double>(0.03);
				awbStrength_ = (*data)["awb_strength"].get<double>(1.0);
				awbBlack_ = (*data)["awb_black"].get<double>(835.0);
				awbMinLevel_ = (*data)["awb_min_level"].get<double>(300.0);
				if (!(awbRefRg_ > 0.0 && awbRefBg_ > 0.0) || !(awbSpeed_ > 0.0 && awbSpeed_ <= 1.0) ||
				    !(awbStrength_ >= 0.0 && awbStrength_ <= 1.0) || !(awbBlack_ >= 0.0) || !(awbMinLevel_ > 0.0))
					return -EINVAL;
				awbEnabled_ = true;
			}
			greenLut_.assign(points.begin() + NF_GAMMA_POINTS,
					 points.begin() + 2 * NF_GAMMA_POINTS);
			if (data->contains("ae_output_target")) {
				outputTarget_ = (*data)["ae_output_target"].get<double>(0.0);
				meterBlack_ = (*data)["ae_meter_black"].get<double>(-1.0);
				meterScale_ = (*data)["ae_meter_scale"].get<double>(0.0);
				if (!(outputTarget_ > 0.0 && outputTarget_ < 1023.0) ||
				    !(meterBlack_ >= 0.0) || !(meterScale_ > 0.0))
					return -EINVAL;
				outputTargetDark_ = outputTarget_;
				if (data->contains("ae_highlight_target")) {
					highlightTarget_ = (*data)["ae_highlight_target"].get<double>(0.0);
					highlightPercentile_ = (*data)["ae_highlight_percentile"].get<double>(0.0);
					if (!(highlightTarget_ > 0.0 && highlightTarget_ < 1023.0) ||
					    !(highlightPercentile_ > 0.5 && highlightPercentile_ < 1.0))
						return -EINVAL;
				}
				if (data->contains("ae_output_target_dark")) {
					outputTargetDark_ = (*data)["ae_output_target_dark"].get<double>(0.0);
					luxBright_ = (*data)["ae_lux_bright"].get<double>(0.0);
					luxDark_ = (*data)["ae_lux_dark"].get<double>(0.0);
					if (!(outputTargetDark_ > 0.0 && outputTargetDark_ < 1023.0) ||
					    !(luxDark_ > 0.0) || !(luxBright_ > luxDark_))
						return -EINVAL;
				}
			}
			if (data->contains("ae_target")) {
				aeTarget_ = (*data)["ae_target"].get<double>(0.0);
				if (!(aeTarget_ > 0.0 && aeTarget_ < 1e6))
					return -EINVAL;
			}
			if (data->contains("ae_speed")) {
				aeSpeed_ = (*data)["ae_speed"].get<double>(0.0);
				if (!(aeSpeed_ > 0.0 && aeSpeed_ <= 1.0))
					return -EINVAL;
			}
			if (data->contains("ae_max_exposure_low")) {
				maxExposureLow_ = (*data)["ae_max_exposure_low"].get<int32_t>(0);
				if (maxExposureLow_ < kMaxExposure || maxExposureLow_ > 7104)
					return -EINVAL;
				maxExposureLow_ &= ~1;
			}
			if (data->contains("ae_max_digital")) {
				aeMaxDigital_ = (*data)["ae_max_digital"].get<double>(0.0);
				if (!(aeMaxDigital_ >= 1.0 && aeMaxDigital_ <= 8.0))
					return -EINVAL;
			}
			candidate.resize(NF_ISP_MAX_BYTES);
			ret = native_front_isp_encode(points.data(), points.size(),
						      candidate.data(), candidate.size());
		}
		if (ret)
			return ret;
		ispTemplate_ = std::move(candidate);
		initialized_ = true;
		return 0;
	}

	int mapBuffers(const std::vector<IPABuffer> &buffers) override
	{
		if (!initialized_ || running_ || !buffers_.empty() || buffers.size() != 8)
			return -EINVAL;
		std::map<uint32_t, std::unique_ptr<MappedFrameBuffer>> pending;
		for (const IPABuffer &buffer : buffers) {
			if (!buffer.id || pending.count(buffer.id) || buffer.planes.size() != 1 ||
			    buffer.planes[0].length < NATIVE_FRONT_STATS_BYTES)
				return -EINVAL;
			FrameBuffer fb(buffer.planes);
			auto map = std::make_unique<MappedFrameBuffer>(&fb, MappedFrameBuffer::MapFlag::Read);
			if (!map->isValid() || map->planes().size() != 1 ||
			    map->planes()[0].size() < NATIVE_FRONT_STATS_BYTES)
				return -EINVAL;
			pending.emplace(buffer.id, std::move(map));
		}
		buffers_ = std::move(pending);
		return 0;
	}

	void unmapBuffers(const std::vector<uint32_t> &ids) override
	{
		if (running_)
			return;
		for (uint32_t id : ids)
			buffers_.erase(id);
	}

	int start() override
	{
		if (!initialized_ || running_ || buffers_.size() != 8)
			return -EINVAL;
		stream_ = 0;
		nextSequence_ = 0;
		nextParameter_ = 5;
		logGain_ = { 0.0, 0.0 };
		running_ = true;
		return 0;
	}
	void stop() override { running_ = false; }

	int computeParameters(uint64_t request, std::vector<uint8_t> *packet,
			      std::vector<uint8_t> *ispPacket) override
	{
		if (!packet || !ispPacket || packet == ispPacket || !running_ ||
		    request != nextParameter_ || request > 0xffffffffULL)
			return -EINVAL;
		const std::array<uint16_t, 4> demux{};
		const std::array<uint32_t, 4> pdpc{};
		const std::array<uint16_t, 2> wb{};
		native_front_params parameters;
		int ret = ipa::camssX1EFrontParameters(request, 0, demux, pdpc, wb, &parameters);
		if (ret)
			return ret;
		const auto *bytes = reinterpret_cast<const uint8_t *>(&parameters);
		packet->assign(bytes, bytes + sizeof(parameters));
		if (awbEnabled_)
			refreshLut();
		*ispPacket = ispTemplate_;
		nextParameter_++;
		return 0;
	}

	void computeParametersAsync(uint64_t epoch, uint64_t request) override
	{
		std::vector<uint8_t> packet, ispPacket;
		int ret = computeParameters(request, &packet, &ispPacket);
		parametersComputed.emit(epoch, request, ret, packet, ispPacket);
	}

	void processStatistics(uint32_t bufferId, uint64_t stream, uint32_t sequence,
			       uint64_t timestamp, int32_t exposure, int32_t analogue,
			       int32_t digital) override
	{
		float luma = 0.0f, red = 0.0f, blue = 0.0f;
		int32_t aeExposure = -1, aeAnalogue = -1, aeDigital = -1;
		int ret = -EINVAL;
		auto it = buffers_.find(bufferId);
		if (running_ && it != buffers_.end() && stream &&
		    sequence == nextSequence_ && (!stream_ || stream == stream_)) {
			const auto &plane = it->second->planes()[0];
			Span<const uint8_t> stats(plane.data(), NATIVE_FRONT_STATS_BYTES);
			ret = ipa::camssX1EFrameLuma(stats, stream, sequence, timestamp, &luma);
			FrontAec::Meter meter{};
			const uint8_t *grid = plane.data() + NATIVE_FRONT_STATS_HEADER_BYTES;
			if (!ret)
				ret = FrontAec::decodeNormal(grid, NATIVE_FRONT_STATS_AEC_BYTES, &meter);
			if (!ret && outputTarget_ > 0.0)
				regionGreen(grid);
			if (!ret) {
				stream_ = stream;
				nextSequence_++;
				red = float(meter.r);
				blue = float(meter.b);
				if (awbEnabled_)
					updateAwb(meter, luma);
				if (exposure >= kMinExposure && analogue >= 0 &&
				    analogue <= kMaxAnalogueCode && digital >= 256)
					autoExposure(luma, exposure, analogue, digital,
						     &aeExposure, &aeAnalogue, &aeDigital);
			}
		}
		statisticsProcessed.emit(bufferId, stream, sequence, timestamp, ret, luma,
					 red, blue, aeExposure, aeAnalogue, aeDigital);
	}

private:
	void autoExposure(float luma, int32_t exposure, int32_t analogue, int32_t digital,
			  int32_t *e, int32_t *a, int32_t *d) const
	{
		const double current = exposure * analogueGain(analogue) * digital / 256.0;
		double ratio = outputTarget_ > 0.0 ? guarded(outputRatio(sceneTarget(luma, current)))
							   : aeTarget_ / std::max<double>(luma, 1.0);
		ratio = std::clamp(ratio, 1.0 / 16, 16.0);
		if (std::fabs(std::log(ratio)) < std::log(1.04)) {
			*e = exposure; *a = analogue; *d = digital;
			return;
		}
		double desired = current * std::pow(ratio, aeSpeed_);
		const double maxGain = analogueGain(kMaxAnalogueCode);
		const double maximum = maxExposureLow_ * maxGain * aeMaxDigital_;
		desired = std::clamp(desired, double(kMinExposure), maximum);
		if (desired <= kMaxExposure) {
			*e = std::max(kMinExposure, int32_t(desired) & ~1);
			*a = 0;
			*d = 256;
			return;
		}
		if (desired <= kMaxExposure * maxGain) {
			*e = kMaxExposure;
			*a = std::clamp<int32_t>(std::lround(1024.0 - 1024.0 * kMaxExposure / desired), 0, kMaxAnalogueCode);
			*d = 256;
			return;
		}
		*a = kMaxAnalogueCode;
		if (desired <= maxExposureLow_ * maxGain) {
			*e = std::clamp<int32_t>(int32_t(desired / maxGain) & ~1, kMaxExposure, maxExposureLow_);
			*d = 256;
			return;
		}
		*e = maxExposureLow_;
		const double dg = std::clamp(desired / (maxExposureLow_ * maxGain), 1.0, aeMaxDigital_);
		*d = std::clamp<int32_t>(std::lround(dg * 256.0), 256, std::lround(aeMaxDigital_ * 256.0));
	}

	/* Smoothed log gains for red and blue relative to the calibrated LUTs. */
	void updateAwb(const FrontAec::Meter &m, double luma)
	{
		const double g = luma - awbBlack_;
		if (g < awbMinLevel_)
			return;
		const double rg = std::max(m.r - awbBlack_, 1.0) / g;
		const double bg = std::max(m.b - awbBlack_, 1.0) / g;
		const double lim = std::log(2.0);
		const double tr = std::clamp(std::log(awbRefRg_ / rg) * awbStrength_, -lim, lim);
		const double tb = std::clamp(std::log(awbRefBg_ / bg) * awbStrength_, -lim, lim);
		logGain_[0] += awbSpeed_ * (tr - logGain_[0]);
		logGain_[1] += awbSpeed_ * (tb - logGain_[1]);
	}

	static double sample(const uint16_t *lut, double x)
	{
		const double p = std::clamp(x, 0.0, 1023.0) * (NF_GAMMA_POINTS - 1) / 1023.0;
		const size_t i = std::min<size_t>(size_t(p), NF_GAMMA_POINTS - 2);
		const double f = p - i;
		return lut[i] * (1.0 - f) + lut[i + 1] * f;
	}

	/* Re-encode the red and blue LUTs as base(gain * x) when the gains moved.
	 * A gain below 1 ramps the top quarter to full scale so clipped
	 * highlights stay neutral. */
	void refreshLut()
	{
		const std::array<double, 2> gains = { std::exp(logGain_[0]), std::exp(logGain_[1]) };
		if (std::fabs(std::log(gains[0] / appliedGain_[0])) < 0.004 &&
		    std::fabs(std::log(gains[1] / appliedGain_[1])) < 0.004)
			return;
		std::array<uint16_t, NF_GAMMA_POINT_COUNT> points = baseLut_;
		const size_t channels[2] = { 0, 2 };
		for (size_t k = 0; k < 2; k++) {
			const uint16_t *base = baseLut_.data() + channels[k] * NF_GAMMA_POINTS;
			uint16_t *dst = points.data() + channels[k] * NF_GAMMA_POINTS;
			const double top = sample(base, 1023.0 * gains[k]);
			int prev = 0;
			for (size_t i = 0; i < NF_GAMMA_POINTS; i++) {
				const double x = i * 1023.0 / (NF_GAMMA_POINTS - 1);
				double y = sample(base, x * gains[k]);
				if (gains[k] < 1.0) {
					const double r = std::clamp((x - 768.0) / 255.0, 0.0, 1.0);
					y += (1023.0 - top) * r * r;
				}
				const int lo = i ? prev : 0, hi = i ? std::min(1023, prev + 500) : 500;
				const int v = std::clamp<int>(int(std::lround(y)), lo, hi);
				dst[i] = uint16_t(v);
				prev = v;
			}
		}
		std::vector<uint8_t> candidate(NF_ISP_MAX_BYTES);
		if (native_front_isp_encode(points.data(), points.size(), candidate.data(), candidate.size()))
			return;
		ispTemplate_ = std::move(candidate);
		appliedGain_ = gains;
	}

	/* Per-region green means (BE sum/count, meter units) as tone-LUT input. */
	void regionGreen(const uint8_t *grid)
	{
		for (size_t region = 0; region < FrontAec::kRegions; region++) {
			const uint8_t *p = grid + region * FrontAec::kStride;
			const double gr = double(FrontAec::le64(p + 8) & FrontAec::kSumMask);
			const double gb = double(FrontAec::le64(p + 16) & FrontAec::kSumMask);
			const double mean = (gr + gb) / (2.0 * FrontAec::kSamples);
			green_[region] = std::max(0.0, (mean - meterBlack_) / meterScale_);
		}
	}

	double displayedMean(double scale) const
	{
		double sum = 0.0;
		for (double g : green_) {
			const double x = std::min(g * scale, 1023.0) * (NF_GAMMA_POINTS - 1) / 1023.0;
			const size_t i = std::min<size_t>(size_t(x), NF_GAMMA_POINTS - 2);
			const double f = x - i;
			sum += greenLut_[i] * (1.0 - f) + greenLut_[i + 1] * f;
		}
		return sum / green_.size();
	}

	/* Exposure ratio that brings the mean displayed green to the target. */
	double sceneTarget(double luma, double current) const
	{
		if (!(luxBright_ > luxDark_))
			return outputTarget_;
		const double lux = std::max(luma - meterBlack_, 1.0) * kMaxExposure / std::max(current, 1.0);
		const double f = std::clamp(std::log(lux / luxDark_) / std::log(luxBright_ / luxDark_), 0.0, 1.0);
		return outputTargetDark_ + (outputTarget_ - outputTargetDark_) * f;
	}

	/* Limit a ratio so the region at the highlight percentile stays at or
	 * below the highlight target on the displayed green scale. */
	double guarded(double ratio) const
	{
		if (!(highlightTarget_ > 0.0))
			return ratio;
		std::array<double, FrontAec::kRegions> sorted = green_;
		const size_t k = std::min<size_t>(size_t(highlightPercentile_ * sorted.size()), sorted.size() - 1);
		std::nth_element(sorted.begin(), sorted.begin() + k, sorted.end());
		const double g = sorted[k];
		if (!(g > 0.0))
			return ratio;
		/* LUT input that displays the highlight target. */
		size_t i = 1;
		while (i < NF_GAMMA_POINTS - 1 && greenLut_[i] < highlightTarget_)
			i++;
		const double a = greenLut_[i - 1], b = greenLut_[i];
		const double f = b > a ? std::clamp((highlightTarget_ - a) / (b - a), 0.0, 1.0) : 0.0;
		const double x = (i - 1 + f) * 1023.0 / (NF_GAMMA_POINTS - 1);
		return std::min(ratio, x / g);
	}

	double outputRatio(double target) const
	{
		double lo = 1.0 / 16, hi = 16.0;
		if (displayedMean(lo) >= target)
			return lo;
		if (displayedMean(hi) <= target)
			return hi;
		for (int i = 0; i < 30; i++) {
			const double mid = std::sqrt(lo * hi);
			(displayedMean(mid) < target ? lo : hi) = mid;
		}
		return std::sqrt(lo * hi);
	}

	std::vector<uint8_t> ispTemplate_;
	std::vector<double> greenLut_;
	std::array<uint16_t, NF_GAMMA_POINT_COUNT> baseLut_{};
	bool awbEnabled_ = false;
	double awbRefRg_ = 0.0, awbRefBg_ = 0.0, awbSpeed_ = 0.03, awbStrength_ = 1.0;
	double awbBlack_ = 835.0, awbMinLevel_ = 300.0;
	std::array<double, 2> logGain_{};
	std::array<double, 2> appliedGain_{ 1.0, 1.0 };
	std::array<double, FrontAec::kRegions> green_{};
	double outputTarget_ = 0.0;
	double meterBlack_ = 0.0;
	double meterScale_ = 1.0;
	double outputTargetDark_ = 0.0;
	double highlightTarget_ = 0.0;
	double highlightPercentile_ = 0.0;
	double luxBright_ = 0.0;
	double luxDark_ = 0.0;
	bool initialized_ = false;
	bool running_ = false;
	uint64_t stream_ = 0;
	uint64_t nextParameter_ = 5;
	uint32_t nextSequence_ = 0;
	double aeTarget_ = 45000.0;
	double aeSpeed_ = 0.6;
	double aeMaxDigital_ = 4.0;
	int32_t maxExposureLow_ = kMaxExposure;
	std::map<uint32_t, std::unique_ptr<MappedFrameBuffer>> buffers_;
};

extern "C" {
extern const IPAModuleInfo ipaModuleInfo = {
	IPA_MODULE_API_VERSION, 0, "camss-x1e", "camss-x1e",
};
IPAInterface *ipaCreate() { return new IPACamssX1E(); }
}
} /* namespace libcamera */
