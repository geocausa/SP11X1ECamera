#!/usr/bin/env bash
# E004io: compile scratch NV12 mapped-DMA-span guard, never install or run.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
STAGE="$REPO/experiments/E004-front-ir-vd55g0/e004io-nv12-sg-dma-span"
SOURCE="$REPO/src/front-imx681/kernel/camss"
KERNEL_SOURCE="/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src"
KERNEL_BUILD="/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826"
"$REPO/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$(uname -r)" == "7.1.5-sp11-render-parity-v4+" ]]
[[ "$(cat "$KERNEL_BUILD/include/config/kernel.release")" == "$(uname -r)" ]]
exec 9>/tmp/sp11-e004im-build.lock
flock -x 9
SCRATCH="$(mktemp -d /tmp/sp11-camera-e004io.XXXXXX)"
trap 'rm -rf "$SCRATCH"' EXIT
mkdir "$SCRATCH/camss"
cp -a "$SOURCE"/. "$SCRATCH/camss/"
python3 "$STAGE/make_dma_span.py" "$SOURCE" "$SCRATCH/camss" > "$SCRATCH/MANIFEST.json"
python3 "$STAGE/test_dma_span.py" --inspect "$SCRATCH/camss" > "$SCRATCH/AUDIT.json"
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$SCRATCH/camss" \
 W=1 KCFLAGS="-ffile-prefix-map=$SCRATCH=/usr/src/sp11-e004io" \
 -j4 modules > "$SCRATCH/build.log" 2>&1 || {
   tail -80 "$SCRATCH/build.log" >&2
   exit 1
 }
[[ -s "$SCRATCH/camss/qcom-camss.ko" ]]
nm "$SCRATCH/camss/qcom-camss.ko" | grep -F 'vfe680_x1e_linear_nv12_full_dryrun_build' >/dev/null
nm "$SCRATCH/camss/qcom-camss.ko" | grep -F 'vfe680_x1e_linear_nv12_buffer_plan' >/dev/null
echo E004IO_GOLDEN_KERNEL_ARM64_BUILD=PASS
echo E004IO_DMA_CONTIGUITY=ONE_MAPPED_DMA_SEGMENT_AT_LEAST_5529600_BYTES
echo E004IO_ALT_NV12_STREAM=EOPNOTSUPP_BEFORE_PIPELINE_PM
echo E004IO_MODULE_INSTALLED=NO CAMERA_ACCESS=NO GOLDEN_UNCHANGED=YES
printf 'E004IO_UNINSTALLED_MODULE_SHA256='
sha256sum "$SCRATCH/camss/qcom-camss.ko" | awk '{print $1}'
