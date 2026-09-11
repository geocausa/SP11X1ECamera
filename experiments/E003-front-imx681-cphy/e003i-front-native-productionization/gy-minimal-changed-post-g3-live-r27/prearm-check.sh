#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/gy-minimal-changed-post-g3-live-r27
GW=$BASE/gw-minimal-changed-post-g3-authority; GX=$BASE/gx-minimal-sentinel-helper-integration; CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
A=/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gv/attempt1-helper-pass-verifier-audit-20260911T222625
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp); trap 'rm -f "$T" /tmp/e003i-gy-bootstrap-prearm' EXIT
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process || fail overlap_guard
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
[ ! -e "$D/runtime-output" ] || fail prior_runtime_output
[ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] || fail prior_attempt
(cd "$A" && sha256sum -c MANIFEST.sha256 >/dev/null) || fail gv_archive
PYTHONDONTWRITEBYTECODE=1 python3 "$GW/verify-gw.py" >/dev/null || fail gw
PYTHONDONTWRITEBYTECODE=1 python3 "$GX/verify-gx.py" >/dev/null || fail gx
make -C "$K" M="$CW" clean >/dev/null; make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}'); [ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail cw_sha
mkdir -p "$D/build"; "$D/build-camss.sh" "$D/build/qcom-camss-gy.ko" >/dev/null; "$D/build-helper.sh" "$D/build/e003i-gy-sentinel-native-aec" >/dev/null; "$D/build-bootstrap.sh" /tmp/e003i-gy-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null || fail verify
[ "$(modinfo -F vermagic "$D/build/qcom-camss-gy.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail vermagic
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"||fail saved; ! grep -q '^next_entry=.'<<<"$ENV"||fail next
for m in qcom_camss imx681 ov13858;do [ ! -d /sys/module/$m ]||fail "module_$m";done
echo "GY_ROOT_PREARM=PASS GW_GX=PASS ONE_NEW_POST_G3_SENTINEL=PASS G5_G26_SHADOW=PASS CW_MODULE=$H"
