/* SPDX-License-Identifier: GPL-2.0-only */
#pragma once
#include "camss-x1e-admission.h"
#include <algorithm>
#include <array>
#include <cerrno>
#include <cmath>
#include <cstdint>
#include <limits>
#include <map>
#include <optional>
#include <libcamera/control_ids.h>
#include <libcamera/controls.h>
#include <linux/videodev2.h>

namespace libcamera {
/* Sensor timing model: 6752 array clocks/line, PIXEL_RATE=720 MHz.
 * Integer microseconds are rounded; no claim about first-row timestamps.
 * Keep the development FLL interval bounded to the measured 3554..7108 lines.
 */
struct CamssX1EManual {
 int32_t fll = 3554, exposure = 1000, analogue = 0, digital = 256;
 bool operator==(const CamssX1EManual &b) const
 { return fll == b.fll && exposure == b.exposure && analogue == b.analogue && digital == b.digital; }
 static int64_t duration(int32_t lines) { return (int64_t(lines) * 422 + 22) / 45; }
 ControlList sensorControls(const ControlInfoMap &info) const
 {
  ControlList out(info);
  out.set(V4L2_CID_VBLANK, fll - 2160);
  out.set(V4L2_CID_EXPOSURE, exposure);
  out.set(V4L2_CID_ANALOGUE_GAIN, analogue);
  out.set(V4L2_CID_DIGITAL_GAIN, digital);
  return out;
 }
 static std::optional<CamssX1EManual> fromSensor(const ControlList &values)
 {
  for (uint32_t id : { V4L2_CID_VBLANK, V4L2_CID_EXPOSURE, V4L2_CID_ANALOGUE_GAIN, V4L2_CID_DIGITAL_GAIN })
   if (!values.contains(id)) return {};
  CamssX1EManual out;
  out.fll = values.get(V4L2_CID_VBLANK).get<int32_t>() + 2160;
  out.exposure = values.get(V4L2_CID_EXPOSURE).get<int32_t>();
  out.analogue = values.get(V4L2_CID_ANALOGUE_GAIN).get<int32_t>();
  out.digital = values.get(V4L2_CID_DIGITAL_GAIN).get<int32_t>();
  if (out.fll < 3554 || out.fll > 7108 || out.exposure < 4 || out.exposure > out.fll - 4 ||
      out.exposure % 2 || out.analogue < 0 || out.analogue > 960 || out.digital < 256 || out.digital > 3840)
   return {};
  return out;
 }
 void metadata(ControlList &out) const
 {
  out.set(controls::AeEnable, false);
  out.set(controls::AeState, controls::AeStateIdle);
  out.set(controls::ExposureTimeMode, controls::ExposureTimeModeManual);
  out.set(controls::AnalogueGainMode, controls::AnalogueGainModeManual);
  out.set(controls::ExposureTime, int32_t(duration(exposure)));
  out.set(controls::AnalogueGain, 1024.0f / (1024 - analogue));
  out.set(controls::DigitalGain, digital / 256.0f);
  out.set(controls::FrameDuration, duration(fll));
  const std::array<int64_t, 2> limits{ duration(fll), duration(fll) };
  out.set(controls::FrameDurationLimits, limits);
 }
};

/* Validate the complete request before changing persistent state. */
inline int camssX1EManualRequest(const ControlList &request, const CamssX1EManual &current,
                               CamssX1EManual *output)
{
 for (const auto &[id, value] : request) {
  auto descriptor = controls::controls.find(id);
  if (descriptor == controls::controls.end() || value.type() != descriptor->second->type() ||
      (id == controls::FrameDurationLimits.id() ? !value.isArray() || value.numElements() != 2 : value.isArray())) return -EINVAL;
  if (id != controls::AeEnable.id() && id != controls::ExposureTimeMode.id() &&
      id != controls::AnalogueGainMode.id() && id != controls::ExposureTime.id() &&
      id != controls::AnalogueGain.id() && id != controls::DigitalGain.id() &&
      id != controls::FrameDurationLimits.id()) return -EOPNOTSUPP;
 }
 if (request.get(controls::AeEnable).value_or(false) ||
     request.get(controls::ExposureTimeMode).value_or(controls::ExposureTimeModeManual) != controls::ExposureTimeModeManual ||
     request.get(controls::AnalogueGainMode).value_or(controls::AnalogueGainModeManual) != controls::AnalogueGainModeManual)
  return -EOPNOTSUPP;
 CamssX1EManual out = current;
 if (auto limits = request.get(controls::FrameDurationLimits)) {
  int64_t low = (*limits)[0], high = (*limits)[1];
  if (!low && !high) out.fll = 3554;
  else {
   if (low < 0 || high <= 0 || low > high || low > CamssX1EManual::duration(7108) ||
       high < CamssX1EManual::duration(3554)) return -ERANGE;
   /* Round to the nearest representable duration, accepting its advertised
    * rounded-microsecond limits without accidentally excluding that line. */
   out.fll = std::clamp<int64_t>((low * 45 + 211) / 422, 3554, 7108);
   if (CamssX1EManual::duration(out.fll) < low) out.fll++;
   if (out.fll > 7108 || CamssX1EManual::duration(out.fll) > high) return -ERANGE;
  }
 }
 if (auto exposure = request.get(controls::ExposureTime)) {
  if (*exposure < CamssX1EManual::duration(4) || *exposure > CamssX1EManual::duration(7104)) return -ERANGE;
  out.exposure = std::max<int32_t>(4, ((*exposure * int64_t(45) + 422) / 844) * 2);
 }
 out.exposure = std::min(out.exposure, (out.fll - 4) & ~1);
 if (auto gain = request.get(controls::AnalogueGain)) {
  if (!std::isfinite(*gain) || *gain < 1.0f || *gain > 16.0f) return -ERANGE;
  out.analogue = std::lround(1024.0 - 1024.0 / *gain);
 }
 if (auto gain = request.get(controls::DigitalGain)) {
  if (!std::isfinite(*gain) || *gain < 1.0f || *gain > 15.0f) return -ERANGE;
  out.digital = std::lround(*gain * 256.0);
 }
 *output = out;
 return 0;
}

/* Admission is ordered exactly like VIDIOC_QBUF, including internal outputs.
 * DelayedControls reset seeds index0, written at SOF0. push after SOF N is
 * index N+1, written at SOF N+1 and effective at N+3. Never amend that slot
 * after it has been pushed. Late controlled requests fail instead of acquiring
 * a misleading request/frame association. Empty requests inherit sensor state.
 */
class CamssX1EControlSchedule {
public:
 void reset(const CamssX1EManual &initial = {}) { nextImage_ = nextSof_ = 0; desired_ = initial; changes_.clear(); }
 uint32_t nextImage() const { return nextImage_; }
 int prepare(const ControlList &request, CamssX1EManual *values) const
 {
  if (nextImage_ == std::numeric_limits<uint32_t>::max()) return -EOVERFLOW;
  int ret = camssX1EManualRequest(request, desired_, values);
  if (ret) return ret;
  if (!request.empty() && uint64_t(nextImage_) < uint64_t(nextSof_) + 3) return -ETIME;
  return 0;
 }
 void admitted(const CamssX1EManual &values, bool changed)
 {
  if (changed) { changes_.emplace(nextImage_, values); desired_ = values; }
  nextImage_++;
 }
 int frameStart(uint32_t sequence, std::optional<CamssX1EManual> *next)
 {
  if (sequence != nextSof_ || sequence > std::numeric_limits<uint32_t>::max() - 3) return -ESTALE;
  nextSof_++;
  auto it = changes_.find(sequence + 3);
  *next = it == changes_.end() ? std::optional<CamssX1EManual>{} : it->second;
  if (it != changes_.end()) changes_.erase(it);
  return 0;
 }
private:
 uint32_t nextImage_ = 0, nextSof_ = 0;
 CamssX1EManual desired_;
 std::map<uint32_t, CamssX1EManual> changes_;
};
} /* namespace libcamera */
