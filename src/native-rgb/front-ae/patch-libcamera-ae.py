#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Derive the front AE libcamera tree (19) from the qualified async tree (18).

Changes: IPA automatic exposure + red/blue metering (new IPA source), mojom
signatures carrying applied controls and AE proposals, pipeline AE mode and
proposal injection through DelayedControls, AE metadata, and request
admission that treats AE-mode-only controls as non-manual.
"""
import shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = Path("/home/geoca/Documents/SP11-PROJECT")
SRC = PROJECT / "06-camera/reference/libcamera-native-front-async-20261010-18"
OUT = PROJECT / "06-camera/reference/libcamera-front-ae-19"


def rep(path, a, b, count=1):
    t = path.read_text()
    assert t.count(a) == count, (path.name, a[:80], t.count(a))
    path.write_text(t.replace(a, b))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT, symlinks=True, ignore=shutil.ignore_patterns(".git"))
    shutil.copyfile(HERE / "camss-x1e-ipa.cpp", OUT / "src/ipa/camss-x1e/camss-x1e.cpp")
    m = OUT / "include/libcamera/ipa/camss_x1e.mojom"
    rep(m, " [async] processStatistics(uint32 bufferId, uint64 stream,\n                           uint32 sequence, uint64 timestamp);",
        " [async] processStatistics(uint32 bufferId, uint64 stream,\n                           uint32 sequence, uint64 timestamp,\n                           int32 exposure, int32 analogue, int32 digital);")
    rep(m, " statisticsProcessed(uint32 bufferId, uint64 stream, uint32 sequence,\n                     uint64 timestamp, int32 ret, float luma);",
        " statisticsProcessed(uint32 bufferId, uint64 stream, uint32 sequence,\n                     uint64 timestamp, int32 ret, float luma,\n                     float red, float blue, int32 aeExposure,\n                     int32 aeAnalogue, int32 aeDigital);")
    for c in (OUT / "src/libcamera/pipeline/camss-x1e/camss-x1e-controls.h",
              OUT / "src/ipa/libipa/camss-x1e-controls.h"):
        if not c.exists():
            continue
        rep(c, " if (request.get(controls::AeEnable).value_or(false) ||\n     request.get(controls::ExposureTimeMode).value_or(controls::ExposureTimeModeManual) != controls::ExposureTimeModeManual ||\n     request.get(controls::AnalogueGainMode).value_or(controls::AnalogueGainModeManual) != controls::AnalogueGainModeManual)\n  return -EOPNOTSUPP;\n",
            " /* AeEnable and the exposure/gain modes select the pipeline AE mode; they\n  * carry no sensor value and are accepted here. */\n")
        rep(c, "/* Validate the complete request before changing persistent state. */",
            "/* Manual sensor values present (AE-mode-only requests are not manual). */\n"
            "inline bool camssX1EHasManual(const ControlList &r)\n{\n"
            " return r.contains(controls::ExposureTime.id()) || r.contains(controls::AnalogueGain.id()) ||\n"
            "        r.contains(controls::DigitalGain.id()) || r.contains(controls::FrameDurationLimits.id());\n}\n\n"
            "/* Requested AE mode, starting from the current mode. Explicit manual values\n"
            " * switch to manual exposure, as in other libcamera pipelines. */\n"
            "inline bool camssX1EAeRequested(const ControlList &r, bool current)\n{\n"
            " if (auto ae = r.get(controls::AeEnable)) current = *ae;\n"
            " if (auto m = r.get(controls::ExposureTimeMode)) current = *m == controls::ExposureTimeModeAuto;\n"
            " if (r.contains(controls::ExposureTime.id()) || r.contains(controls::AnalogueGain.id()) ||\n"
            "     r.contains(controls::DigitalGain.id())) current = false;\n return current;\n}\n\n"
            "/* Validate the complete request before changing persistent state. */")
        rep(c, "  if (!request.empty() && uint64_t(nextImage_) < uint64_t(nextSof_) + 3) return -ETIME;",
            "  if (camssX1EHasManual(request) && uint64_t(nextImage_) < uint64_t(nextSof_) + 3) return -ETIME;")
    p = OUT / "src/libcamera/pipeline/camss-x1e/camss-x1e.cpp"
    rep(p, "  { &controls::AeEnable, ControlInfo(false, false, false) },\n  { &controls::ExposureTimeMode, ControlInfo(controls::ExposureTimeModeManual, controls::ExposureTimeModeManual, controls::ExposureTimeModeManual) },\n  { &controls::AnalogueGainMode, ControlInfo(controls::AnalogueGainModeManual, controls::AnalogueGainModeManual, controls::AnalogueGainModeManual) },",
        "  { &controls::AeEnable, ControlInfo(false, true, true) },\n  { &controls::ExposureTimeMode, ControlInfo(controls::ExposureTimeModeAuto, controls::ExposureTimeModeManual, controls::ExposureTimeModeAuto) },\n  { &controls::AnalogueGainMode, ControlInfo(controls::AnalogueGainModeAuto, controls::AnalogueGainModeManual, controls::AnalogueGainModeAuto) },")
    rep(p, " bool ipaStarted_ = false;\n",
        " bool ipaStarted_ = false;\n bool aeEnabled_ = true;\n bool aeConverged_ = false;\n std::optional<CamssX1EManual> aeProposal_, aePushed_;\n")
    rep(p, " void meteringReady(uint32_t bufferId, uint64_t stream, uint32_t sequence,\n                    uint64_t timestamp, int32_t ret, float luma);",
        " void meteringReady(uint32_t bufferId, uint64_t stream, uint32_t sequence,\n                    uint64_t timestamp, int32_t ret, float luma, float red,\n                    float blue, int32_t aeExposure, int32_t aeAnalogue, int32_t aeDigital);")
    rep(p, " CamssX1EManual initial;\n if (controls) {\n  int ret = camssX1EManualRequest(*controls, initial, &initial);\n  if (ret) return ret;\n }\n",
        " CamssX1EManual initial;\n if (controls) {\n  int ret = camssX1EManualRequest(*controls, initial, &initial);\n  if (ret) return ret;\n }\n"
        " aeEnabled_ = controls ? camssX1EAeRequested(*controls, true) : true;\n"
        " aeConverged_ = false;\n aeProposal_.reset();\n aePushed_.reset();\n")
    rep(p, " Request *request = buffer->request();\n if (!request) return -EINVAL;\n if (controlTimingTrial_",
        " Request *request = buffer->request();\n if (!request) return -EINVAL;\n aeEnabled_ = camssX1EAeRequested(request->controls(), aeEnabled_);\n if (controlTimingTrial_")
    rep(p, "  controlSchedule_.admitted(values, !requested.empty());\n  if (!requested.empty())\n",
        "  controlSchedule_.admitted(values, camssX1EHasManual(requested));\n  if (camssX1EHasManual(requested))\n")
    rep(p, " ipa_->processStatistics(buffer->cookie(), stream, sequence, frame.stats->timestamp);",
        " int32_t appliedExposure = -1, appliedAnalogue = -1, appliedDigital = -1;\n"
        " if (frame.appliedControls) {\n  appliedExposure = frame.appliedControls->exposure;\n"
        "  appliedAnalogue = frame.appliedControls->analogue;\n  appliedDigital = frame.appliedControls->digital;\n }\n"
        " ipa_->processStatistics(buffer->cookie(), stream, sequence, frame.stats->timestamp,\n"
        "                         appliedExposure, appliedAnalogue, appliedDigital);")
    rep(p, "void CamssX1ECameraData::meteringReady(uint32_t bufferId, uint64_t stream,\n                                      uint32_t sequence, uint64_t timestamp,\n                                      int32_t ret, float luma)\n{",
        "void CamssX1ECameraData::meteringReady(uint32_t bufferId, uint64_t stream,\n                                      uint32_t sequence, uint64_t timestamp,\n                                      int32_t ret, float luma, float red, float blue,\n                                      int32_t aeExposure, int32_t aeAnalogue, int32_t aeDigital)\n{")
    rep(p, " frame.luma = luma;\n frame.metadata = nullptr;\n",
        " frame.luma = luma;\n frame.metadata = nullptr;\n"
        " if (aeExposure >= 4) {\n  CamssX1EManual proposal;\n  /* Exposure beyond the 30 fps frame time lengthens the frame (bounded by the\n   * measured 3554..7108-line interval). */\n  proposal.fll = std::clamp<int32_t>(aeExposure + 4, 3554, 7108);\n  proposal.exposure = aeExposure;\n"
        "  proposal.analogue = aeAnalogue;\n  proposal.digital = aeDigital;\n"
        "  aeConverged_ = frame.appliedControls && *frame.appliedControls == proposal;\n  aeProposal_ = proposal;\n }\n"
        " LOG(CAMSSX1E, Debug) << \"CAMSS_X1E_AE frame=\" << sequence << \" luma=\" << luma << \" red=\" << red\n"
        "                     << \" blue=\" << blue << \" exposure=\" << aeExposure << \" again=\" << aeAnalogue\n"
        "                     << \" dgain=\" << aeDigital << \" enabled=\" << aeEnabled_ << \" converged=\" << aeConverged_;\n")
    rep(p, "  if (controlSchedule_.frameStart(sequence, &upcoming)) {\n   fail(\"Request control schedule discontinuity\"); return;\n  }\n",
        "  if (controlSchedule_.frameStart(sequence, &upcoming)) {\n   fail(\"Request control schedule discontinuity\"); return;\n  }\n"
        "  /* AE proposals use the same delayed, read-back-checked write path as\n   * request controls; an explicit request change takes precedence. */\n"
        "  if (!upcoming && aeEnabled_ && aeProposal_ && !(aePushed_ && *aePushed_ == *aeProposal_)) {\n"
        "   upcoming = aeProposal_;\n   aePushed_ = aeProposal_;\n  }\n")
    rep(p, "  applied->metadata(request->_d()->metadata());\n",
        "  applied->metadata(request->_d()->metadata());\n"
        "  ControlList &md = request->_d()->metadata();\n  md.set(controls::AeEnable, aeEnabled_);\n"
        "  md.set(controls::AeState, aeEnabled_ ? (aeConverged_ ? controls::AeStateConverged : controls::AeStateSearching)\n"
        "                                     : controls::AeStateIdle);\n"
        "  md.set(controls::ExposureTimeMode, aeEnabled_ ? controls::ExposureTimeModeAuto : controls::ExposureTimeModeManual);\n"
        "  md.set(controls::AnalogueGainMode, aeEnabled_ ? controls::AnalogueGainModeAuto : controls::AnalogueGainModeManual);\n")
    print("PATCHED", OUT)


if __name__ == "__main__":
    main()
