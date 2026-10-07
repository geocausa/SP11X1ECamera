/* SPDX-License-Identifier: GPL-2.0-only */
#include <iostream>
#include "camss-x1e-controls.h"
#include "test.h"
using namespace libcamera;
class CamssX1EControlsTest : public Test {
protected:
 int run() override {
  CamssX1EManual baseline, out, unchanged;
  ControlList request(controls::controls);
  request.set(controls::ExposureTime, int32_t(18756));
  request.set(controls::AnalogueGain, 2.0f);
  request.set(controls::DigitalGain, 2.0f);
  if (camssX1EManualRequest(request, baseline, &out) || out.exposure != 2000 || out.analogue != 512 || out.digital != 512) return TestFail;
  ControlList metadata(controls::controls); out.metadata(metadata);
  if (metadata.get(controls::SensorTimestamp) || metadata.get(controls::ExposureTime) != 18756 ||
      metadata.get(controls::AnalogueGain) != 2.0f || metadata.get(controls::DigitalGain) != 2.0f ||
      metadata.get(controls::AeEnable) != false || metadata.get(controls::ExposureTimeMode) != controls::ExposureTimeModeManual) return TestFail;
  request.set(controls::DigitalGain, std::numeric_limits<float>::quiet_NaN());
  out = unchanged;
  if (camssX1EManualRequest(request, baseline, &out) != -ERANGE || !(out == unchanged)) return TestFail;
  request.clear(); request.set(controls::AeEnable, true);
  if (camssX1EManualRequest(request, baseline, &out) != -EOPNOTSUPP) return TestFail;
  request.clear(); request.set(controls::ExposureTimeMode, controls::ExposureTimeModeAuto);
  if (camssX1EManualRequest(request, baseline, &out) != -EOPNOTSUPP) return TestFail;
  request.clear(); request.set(controls::ExposureTime, int32_t(66619));
  const std::array<int64_t, 2> slow{66657,66657};
  request.set(controls::FrameDurationLimits, slow);
  if (camssX1EManualRequest(request, baseline, &out) || out.fll != 7108 || out.exposure != 7104) return TestFail;
  const std::array<int64_t, 2> fast{33329,33329}; request.set(controls::FrameDurationLimits, fast);
  if (camssX1EManualRequest(request, out, &out) || out.fll != 3554 || out.exposure != 3550) return TestFail;
  request.clear(); request.set(controls::FrameDurationLimits, std::array<int64_t,2>{33330,33330});
  if (camssX1EManualRequest(request, baseline, &out) != -ERANGE) return TestFail;
  request.clear(); request.set(controls::FrameDurationLimits.id(), ControlValue(Span<const int64_t>(slow.data(),1)));
  if (camssX1EManualRequest(request, baseline, &out) != -EINVAL) return TestFail;
  request.clear(); request.set(controls::ExposureTime.id(), ControlValue(1.0f));
  if (camssX1EManualRequest(request, baseline, &out) != -EINVAL) return TestFail;
  request.clear(); request.set(controls::Brightness, 1.0f);
  if (camssX1EManualRequest(request, baseline, &out) != -EOPNOTSUPP) return TestFail;
  request.clear();
  CamssX1EControlSchedule schedule;
  for (int i=0;i<4;i++) { if (schedule.prepare(request,&out)) return TestFail; schedule.admitted(out,false); }
  request.set(controls::AnalogueGain,2.0f);
  if (schedule.prepare(request,&out) || out.analogue !=512) return TestFail;
  schedule.admitted(out,true);
  std::optional<CamssX1EManual> next;
  if (schedule.frameStart(0,&next) || next || schedule.frameStart(1,&next) || !next || next->analogue !=512) return TestFail;
  if (schedule.frameStart(1,&next) != -ESTALE) return TestFail;
  if (schedule.prepare(request,&out)) return TestFail; // target5 before SOF2 is still schedulable
  if (schedule.frameStart(2,&next) || next) return TestFail;
  if (schedule.prepare(request,&out) != -ETIME) return TestFail; // target5 has now been pushed
  request.clear(); if (schedule.prepare(request,&out) || out.analogue !=512) return TestFail;
  schedule.reset();
  if (schedule.nextImage() !=0 || schedule.prepare(request,&out) || !(out == baseline) || schedule.frameStart(0,&next) || next) return TestFail;
  schedule.reset(CamssX1EManual{3554,2000,512,512});
  if (schedule.prepare(request,&out) || out.exposure !=2000 || out.analogue !=512) return TestFail;
  std::cout << "PASS conversion, ranges, clipping, immutable errors, exact request horizon, discontinuity, restart defaults/start controls\n";
  return TestPass;
 }
};
TEST_REGISTER(CamssX1EControlsTest)
