#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/gc-twentyone-frame-live-r5-r21
FY=$BASE/fy-calibrated-awb-selector-replay
FW=$BASE/fw-windows-r4-r21-combined-awb-lsc-oracle
FV=$BASE/fv-r19-r21-continuation-authority
FZ=$BASE/fz-eighteen-generation-gain-feed-publisher
GA=$BASE/ga-r5-r21-producer-integration
GB=$BASE/gb-twentyone-frame-r21-transport
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp)
trap 'rm -f "$T" /tmp/e003i-gc-bootstrap-prearm' EXIT

[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged

PYTHONDONTWRITEBYTECODE=1 python3 "$FY/verify-fy.py" >/dev/null
A=/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fw/windows-r4-r21-20260911/capture
PYTHONDONTWRITEBYTECODE=1 python3 "$FW/analyze-fw.py" "$A" "$A/E003I-FW-oracle.log" "$A/E003I-FW-holder-output.txt" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$FZ/verify-fz.py" >/dev/null
grep -Fq '"status": "PASS_OFFLINE_R19_R21_COMPOSABLE_AUTHORITY_CLOSED"' "$FV/RESULT.json" || fail fv_status
grep -Fq '"linux_live_r19_plus_allowed": true' "$FV/RESULT.json" || fail fv_live_gate
grep -Fq '"status": "PASS_OFFLINE_R5_R21_AUTHORIZED_INTEGRATION"' "$GA/RESULT.json" || fail ga_status
grep -Fq '"status": "PASS_OFFLINE_TWENTYONE_FRAME_TRANSPORT"' "$GB/RESULT.json" || fail gb_status

make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null

mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-gc.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-gc-twentyone-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-gc-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null

[ "$(modinfo -F vermagic "$D/build/qcom-camss-gc.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camss_vermagic
[ "$(sha256sum "$D/build/camss/camss.c"|awk '{print $1}')" = 'd09cd0bf6d91ed7c51c981455d9643d1f486cb0374fec23a375376b83e837fb4' ] || fail gc_camss_source
[ "$(sha256sum "$D/build/helper/e003i-gc-twentyone-frame-native-aec.c"|awk '{print $1}')" = '8cb43bb96c629ce25c08014192898cc30e21abe226d101d06600f25dba829af5' ] || fail gc_helper_source
[ "$(sha256sum "$D/build/helper/gain-feed.c"|awk '{print $1}')" = '7f91b0ba03ff494e7544d3ac4c793d4cf2522e3761df43ff620a0799d0e9d4ee' ] || fail gc_gain_feed
[ "$(sha256sum "$D/build/helper/native-db-schedule.h"|awk '{print $1}')" = 'fca5d49b12524a9f24bfca673072cf3bbb85d33645045d3a2cb4b155b58c6aae' ] || fail gc_schedule

ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done

echo "GC_ROOT_PREARM=PASS GB_21_FRAME=PASS FZ_G1_G18=PASS GA_R5_R21=PASS FY_FW_R21=PASS CW_MODULE=$H"
