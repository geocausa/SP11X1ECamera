#!/usr/bin/env bash
# E004im — compile both separate NV12 components together, NEVER install/run.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
STAGE="$ROOT/experiments/E004-front-ir-vd55g0/e004im-combined-nv12-kernel-scratch"
SOURCE="$ROOT/src/front-imx681/kernel/camss"
KERNEL_SOURCE="/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src"
KERNEL_BUILD="/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826"
"$ROOT/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$(uname -r)" == '7.1.5-sp11-render-parity-v4+' ]]
[[ "$(cat "$KERNEL_BUILD/include/config/kernel.release")" == "$(uname -r)" ]]
[[ -f "$KERNEL_SOURCE/Makefile" && -f "$KERNEL_BUILD/Module.symvers" ]]
exec 9>/tmp/sp11-e004im-build.lock
flock -x 9
SCRATCH="$(mktemp -d /tmp/sp11-camera-e004im.XXXXXX)"
trap 'rm -rf "$SCRATCH"' EXIT
mkdir "$SCRATCH/camss"
cp -a "$SOURCE"/. "$SCRATCH/camss/"
python3 "$STAGE/make_combined.py" "$SOURCE" "$SCRATCH/camss" > "$SCRATCH/MANIFEST.json"
python3 "$STAGE/test_combined.py" --inspect "$SCRATCH/camss"
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$SCRATCH/camss" W=1 \
 KCFLAGS="-ffile-prefix-map=$SCRATCH=/usr/src/sp11-e004im" \
 -j4 modules > "$SCRATCH/build.log" 2>&1 || {
    tail -80 "$SCRATCH/build.log" >&2
    exit 1
 }
[[ -s "$SCRATCH/camss/qcom-camss.ko" ]]
nm "$SCRATCH/camss/qcom-camss.ko" | grep -F 'vfe680_x1e_linear_nv12_buffer_plan' >/dev/null
nm "$SCRATCH/camss/qcom-camss.ko" | grep -F 'vfe680_x1e_linear_nv12_stream_authorize' >/dev/null
echo E004IM_COMBINED_KERNEL_BUILD=PASS
echo E004IM_QC10C_DEFAULT=UNCHANGED
echo E004IM_NV12_STREAM=BLOCKED_BEFORE_PIPELINE_POWER
echo E004IM_SIDECAR_STREAM_AUTHORIZATION=EOPNOTSUPP
echo E004IM_MODULE_INSTALLED=NO CAMERA_ACCESS=NO
printf 'E004IM_UNINSTALLED_MODULE_SHA256='
sha256sum "$SCRATCH/camss/qcom-camss.ko" | awk '{print $1}'
