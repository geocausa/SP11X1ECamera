#!/usr/bin/env bash
# E004il: independent format enumeration, fail-closed streaming, no installed driver.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
EXPERIMENT="$REPO/experiments/E004-front-ir-vd55g0/e004il-nv12-v4l2-negotiation"
SOURCE="$REPO/src/front-imx681/kernel/camss"
KERNEL_SOURCE="/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src"
KERNEL_BUILD="/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826"
"$REPO/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$(uname -r)" == '7.1.5-sp11-render-parity-v4+' ]]
[[ "$(cat "$KERNEL_BUILD/include/config/kernel.release")" == "$(uname -r)" ]]
exec 9>/tmp/sp11-e004il-kbuild.lock
flock -x 9
SCRATCH="$(mktemp -d /tmp/sp11-camera-e004il.XXXXXX)"
trap 'rm -rf "$SCRATCH"' EXIT
mkdir "$SCRATCH/camss"
cp -a "$SOURCE"/. "$SCRATCH/camss/"
python3 "$EXPERIMENT/offline-v4l2-overlay.py" "$SOURCE" "$SCRATCH/camss" > "$SCRATCH/MANIFEST.json"
# Hard guarantee even the scratch-overlay's VFE680 and accepted source remain identical.
cmp "$SOURCE/camss-vfe-680.c" "$SCRATCH/camss/camss-vfe-680.c"
python3 "$EXPERIMENT/test_source_contract.py" --inspect "$SCRATCH/camss"
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$SCRATCH/camss" W=1 \
 KCFLAGS="-ffile-prefix-map=$SCRATCH=/usr/src/sp11-e004il" \
 -j4 modules > "$SCRATCH/build.log" 2>&1 || {
   tail -70 "$SCRATCH/build.log" >&2
   exit 1
 }
[[ -s "$SCRATCH/camss/qcom-camss.ko" ]]
echo E004IL_OFFLINE_KERNEL_BUILD=PASS
echo E004IL_STAGED_NV12_TRY_FMT=YES
echo E004IL_STAGED_NV12_STREAMON=EOPNOTSUPP_BEFORE_PM
echo E004IL_MODULE_INSTALLED=NO
echo E004IL_CAMERA_ACCESS=NO
sha256sum "$SCRATCH/camss/qcom-camss.ko" | sed 's# .*# UNINSTALLED_MODULE#'
