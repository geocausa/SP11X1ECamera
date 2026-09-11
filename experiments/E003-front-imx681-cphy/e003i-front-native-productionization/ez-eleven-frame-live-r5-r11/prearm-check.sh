#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ez-eleven-frame-live-r5-r11
EY=$BASE/ey-eleven-frame-r10-r11-transport
EW=$BASE/ew-eight-generation-gain-feed-publisher
EX=$BASE/ex-r5-r11-producer-integration
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp); trap 'rm -f "$T" /tmp/e003i-ez-bootstrap-prearm' EXIT
PYTHONDONTWRITEBYTECODE=1 python3 "$EW/verify-ew.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$EY/verify-ey.py" >/dev/null
grep -Fq '"status": "PASS_OFFLINE_G1_G8_C_PUBLISHER"' "$EW/RESULT.json" || fail ew_status
grep -Fq '"status": "PASS_OFFLINE_R5_R11_INTEGRATION"' "$EX/RESULT.json" || fail ex_status
grep -Fq '"r10_capsule_sha256": "ff9b6265c3ce990bb05a94f300df55082992bcc8aaca293b3f091b522209d64f"' "$EX/RESULT.json" || fail ex_r10_hash
grep -Fq '"r11_capsule_sha256": "3bcd19f2082e80ca41fa9a6200ef072c9a49a165b9f91896544dfad20dfe1736"' "$EX/RESULT.json" || fail ex_r11_hash
grep -Fq '"status": "PASS_OFFLINE_ELEVEN_FRAME_TRANSPORT"' "$EY/RESULT.json" || fail ey_status
make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null
mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-ez.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-ez-eleven-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-ez-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null
[ "$(modinfo -F vermagic "$D/build/qcom-camss-ez.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camss_vermagic
[ "$(sha256sum "$D/build/camss/camss.c"|awk '{print $1}')" = '335e15f48cac9835d9ddfa0f1dc96f559346f167f2e8cce1c384635b872d13aa' ] || fail ez_camss_source
[ "$(sha256sum "$D/build/helper/e003i-ez-eleven-frame-native-aec.c"|awk '{print $1}')" = 'b5ecb959b95c63eb38c1e7da98e1f37e9c71d9cc4abe4ee6fbc5456e9bd67993' ] || fail ez_helper_source
[ "$(sha256sum "$D/build/helper/gain-feed.c"|awk '{print $1}')" = '619970bcc9570bbbbaaee062312788e97d0bcbf3348b0722a53893316d8f79bd' ] || fail ez_gain_feed
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged
echo "EZ_ROOT_PREARM=PASS EY_11_FRAME=PASS EW_G1_G8=PASS EX_R5_R11=PASS CW_MODULE=$H"
