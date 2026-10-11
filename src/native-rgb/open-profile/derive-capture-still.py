#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Generate capture-front-still.cpp from capture-front-ae.cpp: same two phases
(manual, then automatic), but keeps SP11_KEEP_PER_PHASE consecutive full frames
from the middle of each phase (temporal noise / module ablation against a static
chart) and lets SP11_MANUAL_LINES / SP11_MANUAL_AGAIN override the manual phase.
Build: derive-capture-still.py --build <libcamera build dir>
Env SP11_HOLD_AT/SP11_HOLD_MS simulate an application that stops returning buffers.
"""
import subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
src = (HERE.parent / "front-ae/capture-front-ae.cpp").read_text()


def rep(a, b):
    global src
    assert src.count(a) == 1, a[:60]
    src = src.replace(a, b)


rep(" * SP11 front (imx681) validation capture against a displayed pattern loop.\n",
    " * SP11 front (imx681) still capture against a static displayed chart.\n"
    " * Keeps SP11_KEEP_PER_PHASE consecutive full frames from the middle of each phase.\n")
rep("const Phase kPhases[] = {", "Phase kPhases[] = {")
rep("constexpr unsigned kPhaseCount = sizeof(kPhases) / sizeof(kPhases[0]);",
    "constexpr unsigned kPhaseCount = sizeof(kPhases) / sizeof(kPhases[0]);\nunsigned gKeep = 1;")
rep("\t\tif (keep_.size() < 2 && (completed_ == perPhase_ / 2 || completed_ == perPhase_ + perPhase_ / 2)) {",
    "\t\tif (keep_.size() < kPhaseCount * gKeep && completed_ % perPhase_ >= perPhase_ / 2 &&\n"
    "\t\t    completed_ % perPhase_ < perPhase_ / 2 + gKeep) {")
rep("\t\tneed(perPhase >= 60 && perPhase <= 3000, \"frames per phase range\");\n",
    "\t\tneed(perPhase >= 60 && perPhase <= 3000, \"frames per phase range\");\n"
    "\t\tif (const char *k = std::getenv(\"SP11_KEEP_PER_PHASE\"))\n"
    "\t\t\tgKeep = unsigned(std::strtoul(k, nullptr, 10));\n"
    "\t\tneed(gKeep >= 1 && gKeep <= 12, \"keep per phase range\");\n"
    "\t\tif (const char *l = std::getenv(\"SP11_MANUAL_LINES\"))\n"
    "\t\t\tkPhases[0].lines = int32_t(std::strtol(l, nullptr, 10));\n"
    "\t\tif (const char *a = std::getenv(\"SP11_MANUAL_AGAIN\"))\n"
    "\t\t\tkPhases[0].again = std::strtof(a, nullptr);\n"
    "\t\tneed(kPhases[0].lines >= 8 && kPhases[0].lines <= 3550 && kPhases[0].again >= 1.0f &&\n"
    "\t\t     kPhases[0].again <= 16.0f, \"manual phase range\");\n")
rep('"SP11 front AE/tone validation capture (env SP11_PATTERN_DIR, SP11_PATTERN_FRAMES_PER_PHASE)',
    '"SP11 front still capture (env SP11_PATTERN_DIR, SP11_PATTERN_FRAMES_PER_PHASE, SP11_KEEP_PER_PHASE,'
    ' SP11_MANUAL_LINES, SP11_MANUAL_AGAIN)')
# Consumer-stall simulation: SP11_HOLD_AT (completed frame) and SP11_HOLD_MS hold
# every request completing in that window and requeue them together afterwards
# from a helper thread, like an application that stops returning buffers.
rep("#include <vector>\n", "#include <thread>\n#include <vector>\n")
rep("unsigned gKeep = 1;", "unsigned gKeep = 1, gHoldAt = 0, gHoldMs = 0;")
rep("\t~Capture()\n\t{\n", "\t~Capture()\n\t{\n\t\tif (holdThread_.joinable())\n\t\t\tholdThread_.join();\n")
rep("\t\tneed(!camera_->stop(), \"stop\");\n",
    "\t\tif (holdThread_.joinable())\n\t\t\tholdThread_.join();\n\t\tneed(!camera_->stop(), \"stop\");\n")
rep("\t\tif (camera_->queueRequest(request)) {\n",
    "\t\tif (holding(request))\n\t\t\treturn;\n\t\tif (camera_->queueRequest(request)) {\n")
rep("\tvoid writeOutputs()\n",
    "\t/* Called with mutex_ held. */\n"
    "\tbool holding(Request *request)\n\t{\n"
    "\t\tif (!gHoldMs)\n\t\t\treturn false;\n"
    "\t\tconst auto now = std::chrono::steady_clock::now();\n"
    "\t\tif (completed_ == gHoldAt && !holdThread_.joinable()) {\n"
    "\t\t\tholdUntil_ = now + std::chrono::milliseconds(gHoldMs);\n"
    "\t\t\tholdThread_ = std::thread([this] { releaseHeld(); });\n\t\t}\n"
    "\t\tif (now < holdUntil_) {\n\t\t\theld_.push_back(request);\n\t\t\treturn true;\n\t\t}\n"
    "\t\treturn false;\n\t}\n"
    "\tvoid releaseHeld()\n\t{\n"
    "\t\tstd::this_thread::sleep_until(holdUntil_);\n"
    "\t\tstd::unique_lock lock(mutex_);\n"
    "\t\tfor (Request *request : held_)\n"
    "\t\t\tif (!stopping_ && !camera_->queueRequest(request))\n\t\t\t\theldReleased_++;\n"
    "\t\theld_.clear();\n\t}\n"
    "\tvoid writeOutputs()\n")
rep("\tunsigned savedFrames_ = 0, mismatches_ = 0;\n",
    "\tunsigned savedFrames_ = 0, mismatches_ = 0, heldReleased_ = 0;\n"
    "\tstd::vector<Request *> held_;\n\tstd::chrono::steady_clock::time_point holdUntil_{};\n\tstd::thread holdThread_;\n")
rep("<< \",\\\"metadata_mismatches\\\":\" << mismatches_", "<< \",\\\"metadata_mismatches\\\":\" << mismatches_ << \",\\\"held_released\\\":\" << heldReleased_")
rep("\t\tif (const char *l = std::getenv(\"SP11_MANUAL_LINES\"))\n",
    "\t\tif (const char *h = std::getenv(\"SP11_HOLD_AT\"))\n\t\t\tgHoldAt = unsigned(std::strtoul(h, nullptr, 10));\n"
    "\t\tif (const char *h = std::getenv(\"SP11_HOLD_MS\"))\n\t\t\tgHoldMs = unsigned(std::strtoul(h, nullptr, 10));\n"
    "\t\tneed(gHoldMs <= 10000, \"hold range\");\n"
    "\t\tif (const char *l = std::getenv(\"SP11_MANUAL_LINES\"))\n")
out = HERE / "capture-front-still.cpp"
out.write_text(src)
print("WROTE", out)
if len(sys.argv) == 3 and sys.argv[1] == "--build":
    b = Path(sys.argv[2])
    subprocess.run(["g++", "-std=c++20", "-O2", "-Wall", "-Wextra", "-Werror", str(out), "-o", str(b / "capture-front-still"),
                    "-I" + str(b / "include"), "-I" + str(b / "source/include"), "-L" + str(b / "src/libcamera"),
                    "-L" + str(b / "src/libcamera/base"), "-lcamera", "-lcamera-base"], check=True)
    print("BUILT", b / "capture-front-still")
