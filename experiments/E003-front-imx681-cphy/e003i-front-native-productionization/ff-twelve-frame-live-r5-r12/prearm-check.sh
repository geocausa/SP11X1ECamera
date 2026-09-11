#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ff-twelve-frame-live-r5-r12
FE=$BASE/fe-twelve-frame-r12-transport
FC=$BASE/fc-nine-generation-gain-feed-publisher
FD=$BASE/fd-r5-r12-producer-integration
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp); trap 'rm -f "$T" /tmp/e003i-ff-bootstrap-prearm' EXIT
PYTHONDONTWRITEBYTECODE=1 python3 "$FC/verify-fc.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$FD/verify-fd.py" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$FE/verify-fe.py" >/dev/null
grep -Fq '"status": "PASS_OFFLINE_G1_G9_C_PUBLISHER"' "$FC/RESULT.json" || fail fc_status
grep -Fq '"status": "PASS_OFFLINE_R5_R12_DYNAMIC_CAL_SLOT_INTEGRATION"' "$FD/RESULT.json" || fail fd_status
grep -Fq '"r12_capsule_sha256": "ee3dabc5519c8c4851cabc321ef2925824b13a6471c0a7e3bd72223544ecd373"' "$FD/RESULT.json" || fail fd_r12_hash
grep -Fq '"status": "PASS_OFFLINE_TWELVE_FRAME_TRANSPORT"' "$FE/RESULT.json" || fail fe_status
make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null
mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-ff.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-ff-twelve-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-ff-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null
[ "$(modinfo -F vermagic "$D/build/qcom-camss-ff.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camss_vermagic
[ "$(sha256sum "$D/build/camss/camss.c"|awk '{print $1}')" = 'deee56e61090bba938f602a7baeae054435762e6312e47d2cac9dbf9a210f15d' ] || fail ff_camss_source
[ "$(sha256sum "$D/build/helper/e003i-ff-twelve-frame-native-aec.c"|awk '{print $1}')" = 'e6f2a792dc070c9d6a726817f30d3a8b1da56b554debccbe2832bd0b18ae47de' ] || fail ff_helper_source
[ "$(sha256sum "$D/build/helper/gain-feed.c"|awk '{print $1}')" = '5c44634bf3082b480fbf6e904e6449164756709069f90bbe719c1c6df432ae67' ] || fail ff_gain_feed
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged
echo "FF_ROOT_PREARM=PASS FE_12_FRAME=PASS FC_G1_G9=PASS FD_R5_R12=PASS CW_MODULE=$H"
