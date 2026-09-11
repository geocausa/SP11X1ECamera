#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/et-nine-frame-live-r5-r9-runtime
ES=$BASE/es-nine-frame-r7-r9-transport
EN=$BASE/en-r5-r9-producer-integration
EP=$BASE/ep-gainadj-multiside-r9-replay
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp);trap 'rm -f "$T" /tmp/e003i-et-bootstrap-prearm' EXIT
PYTHONDONTWRITEBYTECODE=1 python3 "$ES/verify-es.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EN/verify-en.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EP/verify-ep.py" >/dev/null
make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T";fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}');[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ]||fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null
mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-et.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-et-nine-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-et-bootstrap-prearm
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null
[ "$(modinfo -F vermagic "$D/build/qcom-camss-et.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ]||fail camss_vermagic
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true);grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"||fail saved;! grep -q '^next_entry=.'<<<"$ENV"||fail next
for m in qcom_camss imx681 ov13858;do [ ! -d /sys/module/$m ]||fail "golden_module_$m";done
git -C "$R" diff --quiet||fail tracked_dirty;git -C "$R" diff --cached --quiet||fail staged
echo "ET_ROOT_PREARM=PASS ES_NINE_FRAME=PASS CW_MODULE=$H EN_R5_R9=PASS EP_R9_SELECTOR=PASS"
