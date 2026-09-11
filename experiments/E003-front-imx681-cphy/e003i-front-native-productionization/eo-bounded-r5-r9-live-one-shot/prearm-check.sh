#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$B/eo-bounded-r5-r9-live-one-shot
EN=$B/en-r5-r9-live-producer-integration
EM=$B/em-post-r6-template-free-composer
EL=$B/el-calibrated-awb-scalar-join
EJ=$B/ej-clean-awb-cal-factor-replay
EK=$B/ek-linux-front-awb-otp-read-gate
CW=$B/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp); trap 'rm -f "$T" /tmp/e003i-eo-helper-prearm /tmp/e003i-eo-bootstrap-prearm' EXIT
PYTHONDONTWRITEBYTECODE=1 python3 "$EN/verify-en.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EM/verify-em.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EL/verify-el.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EJ/verify-ej.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EK/verify-ek.py" >/dev/null
make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko" | awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_module_sha_$H"
PYTHONDONTWRITEBYTECODE=1 python3 "$CW/prove-cw.py" >/dev/null
"$D/build-helper.sh" /tmp/e003i-eo-helper-prearm
"$D/build-bootstrap.sh" /tmp/e003i-eo-bootstrap-prearm
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null
modinfo -F vermagic "$CW/imx681.ko" | grep -Fxq '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' || fail vermagic
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved_entry
! grep -q '^next_entry=.' <<<"$ENV" || fail next_entry
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged_dirty
printf 'EO_ROOT_PREARM=PASS CW_MODULE=%s EN=PASS EM=PASS EL=PASS EJ=PASS EK=PASS\n' "$H"
