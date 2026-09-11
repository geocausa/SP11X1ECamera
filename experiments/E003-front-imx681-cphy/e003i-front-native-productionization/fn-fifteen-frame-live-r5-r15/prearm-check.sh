#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/fn-fifteen-frame-live-r5-r15
FM=$BASE/fm-fifteen-frame-r15-transport
FK=$BASE/fk-twelve-generation-gain-feed-publisher
FL=$BASE/fl-r5-r15-producer-integration
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp); trap 'rm -f "$T" /tmp/e003i-fn-bootstrap-prearm' EXIT

[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged

PYTHONDONTWRITEBYTECODE=1 python3 "$FK/verify-fk.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$FL/verify-fl.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$FM/verify-fm.py" >/dev/null
grep -Fq '"status": "PASS_OFFLINE_G1_G12_C_PUBLISHER"' "$FK/RESULT.json" || fail fk_status
grep -Fq '"status": "PASS_OFFLINE_R5_R15_AUTHORIZED_INTEGRATION"' "$FL/RESULT.json" || fail fl_status
grep -Fq '"status": "PASS_OFFLINE_FIFTEEN_FRAME_TRANSPORT"' "$FM/RESULT.json" || fail fm_status

make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null

mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-fn.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-fn-fifteen-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-fn-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null

[ "$(modinfo -F vermagic "$D/build/qcom-camss-fn.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camss_vermagic
[ "$(sha256sum "$D/build/camss/camss.c"|awk '{print $1}')" = '592f31d591ff9542f8f67d8228e5f45808afb63088368107ce56422b4d8e34d6' ] || fail fn_camss_source
[ "$(sha256sum "$D/build/helper/e003i-fn-fifteen-frame-native-aec.c"|awk '{print $1}')" = 'f68413ae23cdfbfb84ee39129582e40ecee2fd4b3a37ee242a5bceb4997fb4b4' ] || fail fn_helper_source
[ "$(sha256sum "$D/build/helper/gain-feed.c"|awk '{print $1}')" = '93e284bca519366817324962278d5403c05cdc7fd0454b8a4e8fe683d2b90b2e' ] || fail fn_gain_feed
[ "$(sha256sum "$D/build/helper/native-db-schedule.h"|awk '{print $1}')" = 'b080113d1a07a2600eb8a06b3e5b045422debe0858577d84ab7d61fae03ff54d' ] || fail fn_schedule

ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done

echo "FN_ROOT_PREARM=PASS FM_15_FRAME=PASS FK_G1_G12=PASS FL_R5_R15=PASS CW_MODULE=$H"
