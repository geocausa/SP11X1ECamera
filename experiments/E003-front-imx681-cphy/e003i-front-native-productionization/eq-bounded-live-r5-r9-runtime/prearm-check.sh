#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/eq-bounded-live-r5-r9-runtime
EN=$BASE/en-r5-r9-producer-integration
EP=$BASE/ep-gainadj-multiside-r9-replay
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp);trap 'rm -f "$T" /tmp/e003i-eq-helper-prearm /tmp/e003i-eq-bootstrap-prearm' EXIT
make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T";fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}');[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ]||fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EN/verify-en.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EP/verify-ep.py" >/dev/null
"$D/build-helper.sh" /tmp/e003i-eq-helper-prearm
"$D/build-bootstrap.sh" /tmp/e003i-eq-bootstrap-prearm
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py"
modinfo -F vermagic "$CW/imx681.ko"|grep -Fxq '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'||fail vermagic
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true);grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"||fail saved;! grep -q '^next_entry=.'<<<"$ENV"||fail next
for m in qcom_camss imx681 ov13858;do [ ! -d /sys/module/$m ]||fail "golden_module_$m";done
printf 'EQ_ROOT_PREARM=PASS CW_MODULE=%s EN_R5_R9=PASS EP_R9_SELECTOR=PASS\n' "$H"
