#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/gi-twentyfour-frame-live-r5-r24
FY=$BASE/fy-calibrated-awb-selector-replay
GD=$BASE/gd-windows-r4-r24-combined-awb-lsc-oracle
GE=$BASE/ge-r22-r24-continuation-authority
GF=$BASE/gf-twentyone-generation-gain-feed-publisher
GG=$BASE/gg-r5-r24-producer-integration
GH=$BASE/gh-twentyfour-frame-r24-transport
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp)
trap 'rm -f "$T" /tmp/e003i-gi-bootstrap-prearm' EXIT

[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged

PYTHONDONTWRITEBYTECODE=1 python3 "$FY/verify-fy.py" >/dev/null
A=/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gd/windows-r4-r24-20260911/capture
PYTHONDONTWRITEBYTECODE=1 python3 "$GD/analyze-gd.py" "$A" "$A/E003I-GD-oracle.log" "$A/E003I-GD-holder-output.txt" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$GF/verify-gf.py" >/dev/null
grep -Fq '"status": "PASS_OFFLINE_R22_R24_COMPOSABLE_AUTHORITY_CLOSED"' "$GE/RESULT.json" || fail ge_status
grep -Fq '"linux_live_r22_plus_allowed": true' "$GE/RESULT.json" || fail ge_live_gate
grep -Fq '"status": "PASS_OFFLINE_R5_R24_AUTHORIZED_INTEGRATION"' "$GG/RESULT.json" || fail gg_status
grep -Fq '"status": "PASS_OFFLINE_TWENTYFOUR_FRAME_TRANSPORT"' "$GH/RESULT.json" || fail gh_status

make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null

mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-gi.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-gi-twentyfour-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-gi-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null

[ "$(modinfo -F vermagic "$D/build/qcom-camss-gi.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camss_vermagic
[ "$(sha256sum "$D/build/camss/camss.c"|awk '{print $1}')" = 'b47e9ca26d4591b55d5208eaf40edcef1794d4d6d7fb2e3c33e72edf5f527386' ] || fail gi_camss_source
[ "$(sha256sum "$D/build/helper/e003i-gi-twentyfour-frame-native-aec.c"|awk '{print $1}')" = 'df20afacd4f839250b0338de22600b8d89a09b6320f4c685fdfcfa76e7fa6b79' ] || fail gi_helper_source
[ "$(sha256sum "$D/build/helper/gain-feed.c"|awk '{print $1}')" = '9a4ad8ae24f9672d897d4d6be58394f998df517c9103c8149b59fc0612c57593' ] || fail gi_gain_feed
[ "$(sha256sum "$D/build/helper/native-db-schedule.h"|awk '{print $1}')" = '71a88a4ebacb453a84e9eeaebd6f21354b73b3363f18a47d719336a3500c993b' ] || fail gi_schedule

ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done

echo "GI_ROOT_PREARM=PASS GH_24_FRAME=PASS GF_G1_G21=PASS GG_R5_R24=PASS FY_GD_R24=PASS CW_MODULE=$H"
