#!/usr/bin/env bash
set -Eeuo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
T=$(mktemp -d /tmp/sp11-rgb-source-tests.XXXXXX)
trap 'rm -rf "$T"' EXIT
cp -a "$HERE" "$T/source"
bash "$T/source/build.sh" "$T/build"
F=(-O3 -std=c11 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off)
for camera in front rear; do
 if "$T/build/$camera-direct-publisher" --source /dev/video0 1; then exit 1; fi
 # Standard release builds must reject the opt-in continuous flag BEFORE
 # accessing any camera; only a distinct new guarded candidate may compile
 # SP11_CAMERA_ALLOW_CONTINUOUS=1 with an exact one-shot boot token.
 set +e
 "$T/build/$camera-direct-publisher" --source /dev/video0 continuous > "$T/default-continuous-$camera.log" 2>&1
 continuous_rc=$?
 set -e
 [[ "$continuous_rc" -eq 2 ]]
 gcc "${F[@]}" "$T/source/tests/test_$camera.c" -Wl,--wrap=fopen,--wrap=geteuid,--wrap=open,--wrap=fstat,--wrap=close,--wrap=mmap,--wrap=munmap,--wrap=poll,--wrap=write,--wrap=ioctl -o "$T/fake"
 "$T/fake"
 # Explicit profiling is exercised ONLY under fake mmap/boot token wrappers.
 gcc "${F[@]}" -DSP11_CAMERA_ALLOW_RAW_PROFILE=1 "$T/source/tests/test_$camera.c" -Wl,--wrap=fopen,--wrap=geteuid,--wrap=open,--wrap=fstat,--wrap=close,--wrap=mmap,--wrap=munmap,--wrap=poll,--wrap=write,--wrap=ioctl -o "$T/profile-fake"
 "$T/profile-fake" > "$T/profile-fake-$camera.log" 2>&1
 grep -Fq "SP11_RGB_RAW10_PROFILE camera=$camera frame=1 blocks=" "$T/profile-fake-$camera.log"
 grep -Fq "E004KQ_FAKE_DEVICE_TESTS=PASS" "$T/profile-fake-$camera.log"
 echo "RGB_${camera^^}_FAKE_MMAP_RAW10_PROFILE=PASS CAMERA_HARDWARE=NONE"
 gcc "${F[@]}" -DSP11_RGB_NV12_VIDEO_RANGE=1 "$T/source/tests/test_$camera.c" -Wl,--wrap=fopen,--wrap=geteuid,--wrap=open,--wrap=fstat,--wrap=close,--wrap=mmap,--wrap=munmap,--wrap=poll,--wrap=write,--wrap=ioctl -o "$T/studio-fake-$camera"
 "$T/studio-fake-$camera" > "$T/studio-fake-$camera.log" 2>&1
 grep -Fq "E004KQ_FAKE_DEVICE_TESTS=PASS" "$T/studio-fake-$camera.log"
 echo "RGB_${camera^^}_FAKE_STUDIO_RANGE_LIFECYCLE=PASS CAMERA_HARDWARE=NONE"
 gcc "${F[@]}" -DSP11_RGB_NV12_BT601_TAG=1 -DSP11_RGB_NV12_VIDEO_RANGE=1 "$T/source/tests/test_$camera.c" -Wl,--wrap=fopen,--wrap=geteuid,--wrap=open,--wrap=fstat,--wrap=close,--wrap=mmap,--wrap=munmap,--wrap=poll,--wrap=write,--wrap=ioctl -o "$T/bt601-fake-$camera"
 "$T/bt601-fake-$camera" > "$T/bt601-fake-$camera.log" 2>&1
 grep -Fq "E004KQ_FAKE_DEVICE_TESTS=PASS" "$T/bt601-fake-$camera.log"
 echo "RGB_${camera^^}_OPTIN_BT601_V4L2_FAKE_LIFECYCLE=PASS CAMERA_HARDWARE=NONE"
 cat > "$T/source/tests/default.c" <<EOF
#define E004KQ_NO_MAIN
#include "../$camera-direct-publisher.c"
#include <assert.h>
int main(void) {
 assert(!token_allowed(""));
 assert(!token_allowed("sp11_camera_e004la_rgb_session=1"));
 assert(!token_allowed("sp11_camera_offline_test=1"));
 return 0;
}
EOF
 gcc "${F[@]}" "$T/source/tests/default.c" -o "$T/default"
 "$T/default"
done
gcc "${F[@]}" "$T/source/iq/tests/test_raw10_unpack.c" -o "$T/raw10-unpack-test"
gcc "${F[@]}" "$T/source/iq/tests/test_raw10_profile.c" -o "$T/raw10-profile-test"
"$T/raw10-profile-test"
gcc "${F[@]}" "$T/source/iq/tests/test_nv12_colorimetry.c" -o "$T/bt601-metadata-offline"
"$T/bt601-metadata-offline"
python3 "$T/source/iq/tests/test_exposure_envelope.py" -q
python3 "$T/source/iq/tests/test_preview_brightness_policy.py" -q
echo "RGB_READ_ONLY_EXPOSURE_ENVELOPE_CAMERA_FREE_TESTS=PASS"
gcc "${F[@]}" "$T/source/iq/tests/test_raw10_temporal_spatial.c" -lm -o "$T/raw10-temporal-test"
"$T/raw10-temporal-test"
gcc "${F[@]}" "$T/source/iq/tests/test_rear_preview_tone.c" -o "$T/rear-tone-offline"
"$T/rear-tone-offline"
gcc "${F[@]}" "$T/source/iq/tests/test_front_preview_tone.c" -o "$T/front-tone-offline"
"$T/front-tone-offline"
gcc -O3 -std=c11 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off "$T/source/iq/tests/test_rear_temporal_preview.c" -lm -o "$T/rear-temporal-offline"
"$T/rear-temporal-offline"

if [[ "$(uname -m)" == aarch64 ]];then
 gcc "${F[@]}" "$T/source/iq/tests/test_rear_temporal_scalar_neon_exact.c" -lm -o "$T/rear-temporal-neon-exact"
 "$T/rear-temporal-neon-exact"
fi
gcc "${F[@]}" "$T/source/iq/tests/test_nv12_range.c" -o "$T/nv12-range-test"
"$T/nv12-range-test"
"$T/raw10-unpack-test"
echo RGB_STANDALONE_SOURCE_TESTS=PASS DEFAULT_CONTINUOUS=DENIED
