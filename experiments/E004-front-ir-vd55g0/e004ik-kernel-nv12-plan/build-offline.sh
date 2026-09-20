#!/usr/bin/env bash
# E004ik: compile only a detached, uninstalled SP11 CAMSS NV12 address planner.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
EXPERIMENT="$REPO/experiments/E004-front-ir-vd55g0/e004ik-kernel-nv12-plan"
SOURCE="$REPO/src/front-imx681/kernel/camss"
KERNEL_SOURCE="/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src"
KERNEL_BUILD="/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826"
GOLDEN_KERNEL='7.1.5-sp11-render-parity-v4+'
BASELINE='5af25a42cd15aa5b4c0721da1929b3e50b7bac43e40bdb0962ba996f189632ec'
"$REPO/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$(uname -r)" == "$GOLDEN_KERNEL" ]]
[[ "$(sha256sum "$SOURCE/camss-vfe-680.c" | awk '{print $1}')" == "$BASELINE" ]]
[[ "$(cat "$KERNEL_BUILD/include/config/kernel.release")" == "$GOLDEN_KERNEL" ]]
[[ -f "$KERNEL_SOURCE/Makefile" && -f "$KERNEL_BUILD/Module.symvers" ]]
[[ -f "$EXPERIMENT/nv12-kernel-sidecar.cfrag" ]]
exec 9>/tmp/sp11-e004ik-kbuild.lock
flock -x 9
SCRATCH="$(mktemp -d /tmp/sp11-camera-e004ik.XXXXXX)"
trap 'rm -rf "$SCRATCH"' EXIT
mkdir "$SCRATCH/camss"
cp -a "$SOURCE"/. "$SCRATCH/camss/"
python3 - "$SCRATCH/camss/camss-vfe-680.c" "$EXPERIMENT/nv12-kernel-sidecar.cfrag" <<'PY'
from pathlib import Path
import sys
destination, section = (Path(p) for p in sys.argv[1:])
data = section.read_text()
assert 'vfe680_x1e_linear_nv12_stream_authorize' in data
assert 'return -EOPNOTSUPP;' in data
assert 'writel(' not in data and 'writel_relaxed(' not in data
with destination.open('a') as out:
    out.write('\n' + data + '\n')
PY
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$SCRATCH/camss" \
    W=1 KCFLAGS="-ffile-prefix-map=$SCRATCH=/usr/src/sp11-e004ik" \
    -j4 modules > "$SCRATCH/build.log" 2>&1 || {
        tail -75 "$SCRATCH/build.log" >&2
        exit 1
    }
[[ -s "$SCRATCH/camss/qcom-camss.ko" ]]
nm "$SCRATCH/camss/qcom-camss.ko" | grep -F 'vfe680_x1e_linear_nv12_buffer_plan' >/dev/null
nm "$SCRATCH/camss/qcom-camss.ko" | grep -F 'vfe680_x1e_linear_nv12_stream_authorize' >/dev/null
printf 'E004IK_OFFLINE_KERNEL_BUILD=PASS\n'
printf 'E004IK_KERNEL_RELEASE=%s\n' "$GOLDEN_KERNEL"
printf 'E004IK_SOURCE_QC10C_SHA256=%s\n' "$BASELINE"
printf 'E004IK_SIDECAR_SHA256='
sha256sum "$EXPERIMENT/nv12-kernel-sidecar.cfrag" | awk '{print $1}'
printf 'E004IK_UNINSTALLED_MODULE_SHA256='
sha256sum "$SCRATCH/camss/qcom-camss.ko" | awk '{print $1}'
printf 'E004IK_STREAM_AUTHORIZATION=EOPNOTSUPP_UNCONDITIONALLY\n'
printf 'E004IK_MODULE_INSTALLED=NO CAMERA_NODE_OPENED=NO\n'
