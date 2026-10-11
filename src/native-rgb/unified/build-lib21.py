#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""libcamera tree 21: one library with both SP11 pipelines.

front: camss-x1e pipeline + IPA from tree 20 (robust queue, AE/AWB/tone)
rear:  camss-x1e-rear pipeline + IPA from the rear daily tree 20 (native AE)
The two handlers live in separate directories; only the build lists, the IPA
mojom list and the libipa sensor helper list are shared and merged here.
Usage: build-lib21.py [--build]
"""
import shutil, subprocess, sys
from pathlib import Path

P = Path("/home/geoca/Documents/SP11-PROJECT")
FRONT = P / "06-camera/reference/libcamera-front-robust-20"
REAR = P / "06-camera/reference/libcamera-rear-daily-20"
OUT = P / "06-camera/reference/libcamera-unified-21"
BUILD = P / "02-kernel/libcamera-unified-21"


def rep(path, a, b):
    t = path.read_text()
    assert t.count(a) == 1, (path, a)
    path.write_text(t.replace(a, b))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(FRONT, OUT, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    for rel in ("include/libcamera/ipa/camss_x1e_rear.mojom",
                "test/ipa/libipa/camss-x1e-rear-ipa-test.cpp"):
        shutil.copy2(REAR / rel, OUT / rel)
    for rel in ("src/ipa/camss-x1e-rear", "src/libcamera/pipeline/camss-x1e-rear"):
        shutil.copytree(REAR / rel, OUT / rel)
    rep(OUT / "include/libcamera/ipa/meson.build", "    'camss-x1e': 'camss_x1e.mojom',\n",
        "    'camss-x1e': 'camss_x1e.mojom',\n    'camss-x1e-rear': 'camss_x1e_rear.mojom',\n")
    rep(OUT / "meson.build", "    'camss-x1e': ['aarch64'],\n",
        "    'camss-x1e': ['aarch64'],\n    'camss-x1e-rear': ['aarch64'],\n")
    rep(OUT / "meson_options.txt", "choices : ['camss-x1e', 'ipu3',", "choices : ['camss-x1e', 'camss-x1e-rear', 'ipu3',")
    rep(OUT / "meson_options.txt", "            'camss-x1e',\n", "            'camss-x1e',\n            'camss-x1e-rear',\n")
    rep(OUT / "test/ipa/libipa/meson.build",
        "    {'name': 'camss-x1e-helpers', 'sources': ['camss-x1e-helpers-test.cpp']},\n",
        "    {'name': 'camss-x1e-helpers', 'sources': ['camss-x1e-helpers-test.cpp']},\n"
        "    {'name': 'camss-x1e-rear-ipa', 'sources': ['camss-x1e-rear-ipa-test.cpp']},\n")
    # Both cameras share VFE1: the video node advertises whichever geometry was
    # configured last. The rear handler re-applies its exact 4K route and formats
    # in configure() and validates them there, so registration only needs NV12.
    rep(OUT / "src/libcamera/pipeline/camss-x1e-rear/camss-x1e-rear.cpp",
        " bool exact = it != supported.end() && it->second.size() == 1 &&\n"
        "              it->second[0].min == kOutput && it->second[0].max == kOutput;\n"
        " if (!exact || !video_->caps().isVideoCapture()) {\n",
        " if (it == supported.end() || !video_->caps().isVideoCapture()) {\n")
    # The statistics node is shared too (front QXS1, rear QXR1): each handler
    # selects its layout with S_FMT instead of expecting it as the default.
    rear = OUT / "src/libcamera/pipeline/camss-x1e-rear/camss-x1e-rear.cpp"
    rep(rear, " V4L2DeviceFormat meta{};\n ret=statistics_->getFormat(&meta);\n",
        " V4L2DeviceFormat meta{};\n meta.fourcc=V4L2PixelFormat(NATIVE_REAR_STATS_MAGIC);meta.planesCount=1;\n"
        " meta.planes[0].size=NATIVE_REAR_STATS_BYTES;\n ret=statistics_->setFormat(&meta);\n")
    front = OUT / "src/libcamera/pipeline/camss-x1e/camss-x1e.cpp"
    rep(front, " V4L2DeviceFormat metadata;\n ret = statistics_->getFormat(&metadata);\n",
        " V4L2DeviceFormat metadata;\n metadata.fourcc = V4L2PixelFormat(NATIVE_FRONT_STATS_MAGIC);\n"
        " metadata.planesCount = 1;\n metadata.planes[0].size = NATIVE_FRONT_STATS_BYTES;\n"
        " ret = statistics_->setFormat(&metadata);\n")
    rep(front, "int CamssX1ECameraData::configure()\n{\n if (running_)\n  return -EBUSY;\n int ret = media_->disableLinks();\n if (ret)\n  return ret;\n",
        "int CamssX1ECameraData::configure()\n{\n if (running_)\n  return -EBUSY;\n int ret = media_->disableLinks();\n if (ret)\n  return ret;\n"
        " {\n  V4L2DeviceFormat metadata;\n  metadata.fourcc = V4L2PixelFormat(NATIVE_FRONT_STATS_MAGIC);\n"
        "  metadata.planesCount = 1;\n  metadata.planes[0].size = NATIVE_FRONT_STATS_BYTES;\n"
        "  ret = statistics_->setFormat(&metadata);\n"
        "  if (ret || metadata.fourcc != V4L2PixelFormat(NATIVE_FRONT_STATS_MAGIC))\n   return ret ? ret : -EINVAL;\n }\n")
    # Diagnostics: say which rear statistics stage failed (admission, AEC grid
    # decode -1000+err, AE controller -2000+err).
    ipa = OUT / "src/ipa/camss-x1e-rear/camss-x1e-rear.cpp"
    rep(ipa, "    ret=RearAec::decodeNormal(plane.data()+NATIVE_REAR_STATS_HEADER_BYTES,RearAec::kCapacity,&raw);\n",
        "    ret=RearAec::decodeNormal(plane.data()+NATIVE_REAR_STATS_HEADER_BYTES,RearAec::kCapacity,&raw);\n"
        "    if(ret)ret=-1000+ret;\n")
    rep(ipa, "     stream_=stream;ret=controller_.observe(seq,meter,&proposal);\n",
        "     stream_=stream;ret=controller_.observe(seq,meter,&proposal);\n     if(ret)ret=-2000+ret;\n")
    rep(rear, '  fail("Rear IPA rejected statistics envelope");return;\n',
        '  LOG(CAMSSX1ERear,Error)<<"Rear statistics rejected ret="<<ret<<" sequence="<<sequence\n'
        '   <<" known="<<(it!=frames_.end())<<" stream="<<stream<<" expected="<<streamId_;\n'
        '  fail("Rear IPA rejected statistics envelope");return;\n')
    # Bright scenes: the AEC grid does not count pixels above its saturation
    # threshold (measured: up to ~15 of 4096 cells short in daylight; cell means
    # reach ~125k). Count the missing samples at saturation instead of rejecting
    # the whole frame, which stopped the rear stream in daylight.
    aec = OUT / "src/ipa/camss-x1e-rear/rear-aec-statistics.h"
    rep(aec, "constexpr uint64_t kSamples=2205,kSumMask=0x3ffffffffULL;\n",
        "constexpr uint64_t kSamples=2205,kSumMask=0x3ffffffffULL,kSaturated=131071;\n")
    rep(aec, "  if((value>>48)!=kSamples||(value&0x0000fffc00000000ULL))return -EPROTO;\n"
        "  total[channel]+=value&kSumMask;\n",
        "  const uint64_t counted=value>>48;\n"
        "  if(counted>kSamples||(value&0x0000fffc00000000ULL))return -EPROTO;\n"
        "  total[channel]+=(value&kSumMask)+(kSamples-counted)*kSaturated;\n")
    # Rear AE target: the engineering 12000 left daylight scenes about one stop
    # darker than Windows. Default 18000, overridable with SP11_REAR_AE_TARGET.
    rep(rear, "ret=ipa_->start(aeEnabled_,seedLines_,seedGain_,12000.0);",
        "ret=ipa_->start(aeEnabled_,seedLines_,seedGain_,[]{const char *v=std::getenv(\"SP11_REAR_AE_TARGET\");"
        "double t=v?std::atof(v):18000.0;return t>1000.0&&t<100000.0?t:18000.0;}());")
    # Applications expect automatic exposure unless they ask otherwise.
    rep(rear, " bool aeEnabled_=false;\n", " bool aeEnabled_=true;\n")
    rep(rear, "manual.emplace(&controls::AeEnable,ControlInfo{false,true,false});",
        "manual.emplace(&controls::AeEnable,ControlInfo{false,true,true});")
    print("WROTE", OUT)
    if "--build" in sys.argv:
        if BUILD.exists():
            shutil.rmtree(BUILD)
        subprocess.run(["meson", "setup", str(BUILD), str(OUT), "--buildtype=release", "--werror",
                        "-Dpipelines=camss-x1e,camss-x1e-rear", "-Dipas=camss-x1e,camss-x1e-rear",
                        "-Dcam=enabled", "-Dqcam=disabled", "-Dgstreamer=disabled", "-Dv4l2=disabled",
                        "-Ddocumentation=disabled", "-Dlc-compliance=disabled", "-Dtracing=disabled",
                        "-Dpycamera=disabled", "-Dandroid=disabled", "-Dtest=false"], check=True)
        if not (BUILD / "source").exists():
            (BUILD / "source").symlink_to(OUT)
        subprocess.run(["ninja", "-C", str(BUILD)], check=True)
        print("BUILT", BUILD)


if __name__ == "__main__":
    main()
