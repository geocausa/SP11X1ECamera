#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ev-nine-frame-live-r5-r9-gainfeed
EU=$BASE/eu-six-generation-gain-feed-publisher
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp); trap 'rm -f "$T" /tmp/e003i-ev-bootstrap-prearm' EXIT
PYTHONDONTWRITEBYTECODE=1 python3 "$EU/verify-eu.py" >/dev/null
grep -Fq '"status": "PASS_OFFLINE_G1_G6_C_PUBLISHER"' "$EU/RESULT.json" || fail eu_status
make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null
mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-ev.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-ev-nine-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-ev-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null
[ "$(modinfo -F vermagic "$D/build/qcom-camss-ev.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camss_vermagic
[ "$(sha256sum "$D/build/helper/gain-feed.c"|awk '{print $1}')" = '2dbd4856294fe3aceecc1f7027643b6a0c559e7ce5469d902846b9073a466b3c' ] || fail ev_gain_feed_copy
[ "$(sha256sum "$D/build/helper/e003i-ev-nine-frame-native-aec.c"|awk '{print $1}')" = '12a6c6f4f9000a6bfde7aca9b124cb8a281c39ecd65676f20c81b704ce5b4a51' ] || fail ev_helper_source
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged
echo "EV_ROOT_PREARM=PASS EU_C_PUBLISHER_G1_G6=PASS ES_NINE_FRAME=PASS CW_MODULE=$H EN_R5_R9=UNCHANGED EP_R9_SELECTOR=UNCHANGED"
