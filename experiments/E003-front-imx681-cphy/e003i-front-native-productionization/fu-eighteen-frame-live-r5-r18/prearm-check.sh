#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/fu-eighteen-frame-live-r5-r18
FT=$BASE/ft-eighteen-frame-r18-transport
FR=$BASE/fr-fifteen-generation-gain-feed-publisher
FS=$BASE/fs-r5-r18-producer-integration
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp)
trap 'rm -f "$T" /tmp/e003i-fu-bootstrap-prearm' EXIT

[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged

PYTHONDONTWRITEBYTECODE=1 python3 "$FR/verify-fr.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$FS/verify-fs.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$FT/verify-ft.py" >/dev/null
grep -Fq '"status": "PASS_OFFLINE_G1_G15_C_PUBLISHER"' "$FR/RESULT.json" || fail fr_status
grep -Fq '"status": "PASS_OFFLINE_R5_R18_AUTHORIZED_INTEGRATION"' "$FS/RESULT.json" || fail fs_status
grep -Fq '"status": "PASS_OFFLINE_EIGHTEEN_FRAME_TRANSPORT"' "$FT/RESULT.json" || fail ft_status

make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null

mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-fu.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-fu-eighteen-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-fu-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null

[ "$(modinfo -F vermagic "$D/build/qcom-camss-fu.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camss_vermagic
[ "$(sha256sum "$D/build/camss/camss.c"|awk '{print $1}')" = 'a096493ae74fc3a22945f71f670f8777f0ea375bd3ad667c7451c96116d2ef6c' ] || fail fu_camss_source
[ "$(sha256sum "$D/build/helper/e003i-fu-eighteen-frame-native-aec.c"|awk '{print $1}')" = '24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce' ] || fail fu_helper_source
[ "$(sha256sum "$D/build/helper/gain-feed.c"|awk '{print $1}')" = 'c8b03597649ec5e1a6e5b62110eb61ab7cd6a29073a3ecdcf9194f439b410627' ] || fail fu_gain_feed
[ "$(sha256sum "$D/build/helper/native-db-schedule.h"|awk '{print $1}')" = '092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf' ] || fail fu_schedule

ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done

echo "FU_ROOT_PREARM=PASS FT_18_FRAME=PASS FR_G1_G15=PASS FS_R5_R18=PASS CW_MODULE=$H"
