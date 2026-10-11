#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Derive the robust-queue libcamera tree (20) from the front AE tree (19).

Pairs with kernel native_front_queue_robust (build 46), which drops frames into a
scratch buffer when no application buffer is queued. The pipeline then sees
hardware frames without an image or statistics, and images arriving with a later
frame sequence than predicted at admission. Changes:
 - imageReady: an image may arrive later than its admission prediction; the gap
   is the number of frames dropped before it. All outstanding admissions and the
   request-control schedule move by the same gap (the kernel consumes buffers in
   order, so every later buffer shifts equally).
 - frameStart: frame-start records older than 8 frames that never received an
   image or statistics are dropped frames and are retired.
Strict checks stay for images earlier than predicted, duplicates and identity.
Build: patch-libcamera-robust.py && meson setup + ninja (see --build).
"""
import shutil, subprocess, sys
from pathlib import Path

PROJECT = Path("/home/geoca/Documents/SP11-PROJECT")
SRC = PROJECT / "06-camera/reference/libcamera-front-ae-19"
OUT = PROJECT / "06-camera/reference/libcamera-front-robust-20"
BUILD = PROJECT / "02-kernel/libcamera-front-robust-20"


def rep(path, a, b, count=1):
    t = path.read_text()
    assert t.count(a) == count, (path.name, a[:80], t.count(a))
    path.write_text(t.replace(a, b))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT, symlinks=True, ignore=shutil.ignore_patterns(".git"))
    d = OUT / "src/libcamera/pipeline/camss-x1e"
    rep(d / "camss-x1e-controls.h",
        " int frameStart(uint32_t sequence, std::optional<CamssX1EManual> *next)\n",
        " /* Frames dropped by the kernel before an admitted image: every image index\n"
        "  * from 'from' on, and the control changes keyed to them, move by 'gap'. */\n"
        " void dropped(uint32_t from, uint32_t gap)\n"
        " {\n"
        "  std::map<uint32_t, CamssX1EManual> moved;\n"
        "  for (const auto &[index, values] : changes_)\n"
        "   moved.emplace(index >= from ? index + gap : index, values);\n"
        "  changes_ = std::move(moved);\n"
        "  nextImage_ += gap;\n"
        " }\n"
        " int frameStart(uint32_t sequence, std::optional<CamssX1EManual> *next)\n")
    c = d / "camss-x1e.cpp"
    rep(c,
        " auto admission = admittedImages_.find(buffer);\n"
        " if (admission == admittedImages_.end() || admission->second != sequence) {\n"
        "  cancelImage(buffer); fail(\"Output admission/frame identity mismatch\"); return;\n"
        " }\n",
        " auto admission = admittedImages_.find(buffer);\n"
        " if (admission == admittedImages_.end() || sequence < admission->second) {\n"
        "  cancelImage(buffer); fail(\"Output admission/frame identity mismatch\"); return;\n"
        " }\n"
        " if (sequence > admission->second) {\n"
        "  /* The kernel dropped frames because no image was queued in time. */\n"
        "  const uint32_t predicted = admission->second, gap = sequence - predicted;\n"
        "  for (auto &[queued, target] : admittedImages_) {\n"
        "   (void)queued;\n"
        "   if (target >= predicted)\n"
        "    target += gap;\n"
        "  }\n"
        "  controlSchedule_.dropped(predicted, gap);\n"
        "  droppedFrames_ += gap;\n"
        "  LOG(CAMSSX1E, Warning) << \"CAMSS_X1E_DROPPED frames=\" << gap << \" before=\" << sequence\n"
        "                       << \" total=\" << droppedFrames_;\n"
        " }\n")
    rep(c,
        " nextSofSequence_++;\n"
        " LOG(CAMSSX1E, Debug) << \"CAMSS_X1E_SOF frame=\" << sequence;\n",
        " nextSofSequence_++;\n"
        " LOG(CAMSSX1E, Debug) << \"CAMSS_X1E_SOF frame=\" << sequence;\n"
        " /* Frames the kernel dropped never get an image or statistics. */\n"
        " for (auto it = frames_.begin(); it != frames_.end() && it->first + 8 < sequence;) {\n"
        "  if (!it->second.image && !it->second.stats && !it->second.metadata)\n"
        "   it = frames_.erase(it);\n"
        "  else\n"
        "   ++it;\n"
        " }\n")
    rep(c, " std::map<uint32_t, FrameState> frames_;\n",
        " std::map<uint32_t, FrameState> frames_;\n uint64_t droppedFrames_ = 0;\n")
    # Frame-start events lost while the whole pipeline thread was stalled (event
    # queue overflow): resynchronise instead of failing. DelayedControls indexes
    # its ring by the number of frames since reset, so it is reset and indexed
    # relative to the resynchronisation frame.
    rep(d / "camss-x1e-controls.h",
        " int frameStart(uint32_t sequence, std::optional<CamssX1EManual> *next)\n",
        " /* Frame starts were lost: continue at 'sequence'. Changes whose frame has\n"
        "  * passed are applied at the first frame that can still take them. */\n"
        " void resync(uint32_t sequence)\n"
        " {\n"
        "  std::map<uint32_t, CamssX1EManual> moved;\n"
        "  for (const auto &[index, values] : changes_)\n"
        "   moved.insert_or_assign(std::max<uint32_t>(index, sequence + 3), values);\n"
        "  changes_ = std::move(moved);\n"
        "  nextSof_ = sequence;\n"
        " }\n"
        " int frameStart(uint32_t sequence, std::optional<CamssX1EManual> *next)\n")
    rep(c,
        " if (sequence != nextSofSequence_ ||\n"
        "     nextSofSequence_ == std::numeric_limits<uint32_t>::max()) {\n"
        "  fail(\"Native frame-start sequence discontinuity\");\n"
        "  return;\n"
        " }\n",
        " if (sequence < nextSofSequence_ ||\n"
        "     nextSofSequence_ == std::numeric_limits<uint32_t>::max()) {\n"
        "  fail(\"Native frame-start sequence discontinuity\");\n"
        "  return;\n"
        " }\n"
        " if (sequence > nextSofSequence_) {\n"
        "  LOG(CAMSSX1E, Warning) << \"CAMSS_X1E_SOF_RESYNC expected=\" << nextSofSequence_\n"
        "                       << \" frame=\" << sequence;\n"
        "  if (delayedControls_)\n"
        "   delayedControls_->reset();\n"
        "  sofBase_ = sequence;\n"
        "  controlSchedule_.resync(sequence);\n"
        "  expectedWrite_.reset();\n"
        "  aePushed_.reset();\n"
        "  nextSofSequence_ = sequence;\n"
        " }\n")
    rep(c, "  delayedControls_->applyControls(sequence);\n", "  delayedControls_->applyControls(sequence - sofBase_);\n")
    rep(c, "  auto applied = CamssX1EManual::fromSensor(delayedControls_->get(sequence));\n",
        "  auto applied = CamssX1EManual::fromSensor(delayedControls_->get(sequence - sofBase_));\n")
    rep(c, " nextSofSequence_ = 0;\n streamId_ = 0;\n", " nextSofSequence_ = 0;\n sofBase_ = 0;\n streamId_ = 0;\n")
    rep(c, " uint64_t droppedFrames_ = 0;\n", " uint64_t droppedFrames_ = 0;\n uint32_t sofBase_ = 0;\n")
    # Frames whose frame start was lost before a resynchronisation have no
    # applied-control record; they complete without control metadata.
    rep(c, "     (delayedControls_ && !it->second.appliedControls))\n",
        "     (delayedControls_ && !it->second.appliedControls && sequence >= sofBase_))\n")
    # Statistics after dropped frames: the IPA accepts a later sequence, and the
    # kernel's dropped-metadata counter / discontinuity flag is information, not
    # an error (both pipeline and IPA copies of the header check).
    ipa = OUT / "src/ipa/camss-x1e/camss-x1e.cpp"
    # The IPA source of record is front-ae/camss-x1e-ipa.cpp (adds the adaptive shadow lift).
    shutil.copyfile(Path(__file__).resolve().parent.parent / "front-ae/camss-x1e-ipa.cpp", ipa)
    rep(ipa, "\t\t    sequence == nextSequence_ && (!stream_ || stream == stream_)) {\n",
        "\t\t    sequence >= nextSequence_ && (!stream_ || stream == stream_)) {\n")
    rep(ipa, "\t\t\t\tnextSequence_++;\n", "\t\t\t\tnextSequence_ = sequence + 1;\n")
    for h in (OUT / "src/ipa/libipa/native-front-stats.h", d / "native-front-stats.h"):
        rep(h, " if (native_front_stats_u64(p + 32) || native_front_stats_u32(p + 40))\n  return -EPIPE;\n", "")
    print("WROTE", OUT)
    if "--build" in sys.argv:
        if not BUILD.exists():
          subprocess.run(["meson", "setup", str(BUILD), str(OUT), "--buildtype=release", "--werror",
                        "-Dpipelines=camss-x1e", "-Dipas=camss-x1e", "-Dcam=enabled", "-Dqcam=disabled",
                        "-Dgstreamer=disabled", "-Dv4l2=disabled", "-Ddocumentation=disabled",
                        "-Dlc-compliance=disabled", "-Dtracing=disabled", "-Dpycamera=disabled",
                        "-Dandroid=disabled", "-Dtest=false"], check=True)
        if not (BUILD / "source").exists():
            (BUILD / "source").symlink_to(OUT)
        subprocess.run(["ninja", "-C", str(BUILD)], check=True)
        print("BUILT", BUILD)


if __name__ == "__main__":
    main()
