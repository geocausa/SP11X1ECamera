#!/usr/bin/env bash
# E004in -- build uninstalled SP11 CAMSS module with read-only FULL write-master proposal.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
EXPERIMENT="$REPO/experiments/E004-front-ir-vd55g0/e004in-linear-full-wm-dryrun"
SOURCE="$REPO/src/front-imx681/kernel/camss"
KERNEL_SOURCE="/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src"
KERNEL_BUILD="/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826"
"$REPO/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$(uname -r)" == "7.1.5-sp11-render-parity-v4+" ]]
[[ "$(cat "$KERNEL_BUILD/include/config/kernel.release")" == "$(uname -r)" ]]
exec 9>/tmp/sp11-e004im-build.lock
flock -x 9
SCRATCH="$(mktemp -d /tmp/sp11-camera-e004in.XXXXXX)"
trap 'rm -rf "$SCRATCH"' EXIT
mkdir "$SCRATCH/camss"
cp -a "$SOURCE"/. "$SCRATCH/camss/"
python3 "$EXPERIMENT/make_full_dryrun.py" "$SOURCE" "$SCRATCH/camss" > "$SCRATCH/MANIFEST.json"
python3 "$EXPERIMENT/test_full_dryrun.py" --inspect "$SCRATCH/camss" > "$SCRATCH/AUDIT.json"
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$SCRATCH/camss" \
 W=1 KCFLAGS="-ffile-prefix-map=$SCRATCH=/usr/src/sp11-e004in" \
 -j4 modules > "$SCRATCH/build.log" 2>&1 || {
   tail -75 "$SCRATCH/build.log" >&2
   exit 1
 }
[[ -s "$SCRATCH/camss/qcom-camss.ko" ]]
nm "$SCRATCH/camss/qcom-camss.ko" |
 grep -F 'vfe680_x1e_linear_nv12_full_dryrun_build' >/dev/null
nm "$SCRATCH/camss/qcom-camss.ko" |
 grep -F 'vfe680_x1e_linear_nv12_full_dryrun_authorize' >/dev/null
printf 'E004IN_KERNEL_ARM64_BUILD=PASS\n'
printf 'E004IN_FULL_CLIENTS=0,1 PROPOSED_PACKER=3\n'
printf 'E004IN_ALT_NV12_STREAM=EOPNOTSUPP_BEFORE_POWER\n'
printf 'E004IN_FULL_MMIO_WRITES=0 COMPRESSED_MODE_RESET_PROVEN=NO\n'
printf 'E004IN_MODULE_INSTALLED=NO CAMERA_ACCESS=NO GOLDEN_UNCHANGED=YES\n'
printf 'E004IN_UNINSTALLED_MODULE_SHA256='
sha256sum "$SCRATCH/camss/qcom-camss.ko" | awk '{print $1}'
