#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/go-twentyseven-frame-live-r5-r27
GJ=$BASE/gj-windows-r4-r27-combined-awb-lsc-oracle
GK=$BASE/gk-r25-r27-continuation-authority
GL=$BASE/gl-twentyfour-generation-gain-feed-publisher
GM=$BASE/gm-r5-r27-producer-integration
GN=$BASE/gn-twentyseven-frame-r27-transport
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
GJA=/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gj/windows-r4-r27-20260911
fail(){ echo "FAIL: $*" >&2; exit 1; }
T=$(mktemp); trap 'rm -f "$T" /tmp/e003i-go-bootstrap-prearm' EXIT

"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process || fail overlap_guard
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
[ ! -e "$D/runtime-output" ] || fail prior_runtime_output
[ ! -e "$D/HELPER-CONSUMED.marker" ] || fail consumed_marker
[ ! -e "$D/ATTEMPT1-PASS.json" ] && [ ! -e "$D/ATTEMPT1-FAILURE.json" ] || fail prior_attempt_record
! grep -Fq 'sp11_camera_e003i_go_twentyseven_frame_r5_r27=1' /proc/cmdline || fail already_candidate_boot

python3 - <<'PY'
import json
from pathlib import Path
b=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003i-front-native-productionization')
gj=json.loads((b/'gj-windows-r4-r27-combined-awb-lsc-oracle/RESULT.json').read_text())
assert gj['status']=='PASS_WINDOWS_COMBINED_R4_R27_AWB_LSC'
assert gj['windows_stream_count']==1 and gj['combined_r27_completion'] is True
assert gj['awb_result']['bit_exact']=='24/24'
assert gj['lsc_result']['clean_lsc_replay']=='24/24 byte-exact LSC0/LSC1/LSC2/GIC'
PY
(cd "$GJA" && sha256sum -c MANIFEST.sha256 >/dev/null) || fail gj_archive_manifest
PYTHONDONTWRITEBYTECODE=1 python3 "$GK/verify-gk.py" >/dev/null || fail gk_verify
PYTHONDONTWRITEBYTECODE=1 python3 "$GL/verify-gl.py" >/dev/null || fail gl_verify
PYTHONDONTWRITEBYTECODE=1 python3 "$GM/verify-gm.py" >/dev/null || fail gm_verify
PYTHONDONTWRITEBYTECODE=1 python3 "$GN/verify-gn.py" >/dev/null || fail gn_verify

make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko"|awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null || fail cw_proof

mkdir -p "$D/build"
"$D/build-camss.sh" "$D/build/qcom-camss-go.ko" >/dev/null
"$D/build-helper.sh" "$D/build/e003i-go-twentyseven-frame-native-aec" >/dev/null
"$D/build-bootstrap.sh" /tmp/e003i-go-bootstrap-prearm >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify.py" >/dev/null || fail go_verify

[ "$(modinfo -F vermagic "$D/build/qcom-camss-go.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camss_vermagic
[ "$(sha256sum "$D/build/camss/camss.c"|awk '{print $1}')" = '117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95' ] || fail go_camss_source
[ "$(sha256sum "$D/build/helper/e003i-go-twentyseven-frame-native-aec.c"|awk '{print $1}')" = '32ecff0848a3f47fe149ead36ccf63eec26a8c78180075129253a65792dedf1e' ] || fail go_helper_source
[ "$(sha256sum "$D/build/helper/gain-feed.c"|awk '{print $1}')" = '2ad568beeeaf0ef9a5229b234ff172e6cbb5f2a3848f063eec103995595031c1' ] || fail go_gain_feed
[ "$(sha256sum "$D/build/helper/native-db-schedule.h"|awk '{print $1}')" = 'b3db42c9a38da0f428277fccbe79b01cc25a5a42d7f4cf26112d1096e0eedfee' ] || fail go_schedule

ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "golden_module_$m"; done

echo "GO_ROOT_PREARM=PASS GN_27_FRAME=PASS GL_G1_G24=PASS GM_R5_R27=PASS GJ_GK_R27=PASS CW_MODULE=$H"
