#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-parity-0056-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-parity-0056-static
BOOT=/boot/sp11-7.1.5-camera-e003h-camnoc300-0056
ENTRY=/etc/grub.d/99t_sp11_camera_e003h_camnoc300_0056
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail 'not Golden'
[ "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'HEAD/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'; git -C "$REPO" diff --cached --quiet || fail 'staged dirty'
git -C "$REPO" merge-base --is-ancestor 1f83a00ced3087cf35f8e6269026b164a07ed986 HEAD || fail '0056 static commit not ancestor'
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'saved_entry not Golden'; ! grep -q '^next_entry=.' <<<"$ENV" || fail 'next_entry armed'
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module loaded: $m"; done
[ ! -e "$BOOT" ] || fail '0056 boot directory exists'; sudo -n test ! -e "$ENTRY" || fail '0056 grub entry exists'
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail 'authorization already exists at package gate'
[ ! -e "$NEW/RUNTIME-CAMNOC300-0056-RUN.txt" ] || fail 'runtime evidence already exists at package gate'
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0056-static-inspection.json" "$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-0055-candidate/runtime-0055-analysis.json" <<'PY'
import hashlib,json,sys,pathlib
mp,root,sp,rp=sys.argv[1:]; root=pathlib.Path(root); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp))
assert m['accepted'] and not m['runtime_authorized']; assert m['behavior_delta']['new_clock_rate_requests']==1 and m['behavior_delta']['camera_register_changes']==0
for r,h in m['assets'].items(): assert sha(root/r)==h,(r,h)
assert sha(sp)==m['static_inspection_sha256']; assert sha(rp)==m['linux_0055_analysis_sha256']
PY
modinfo -F vermagic "$NEW/qcom-camss.ko" | grep -qx '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' || fail 'CAMSS vermagic mismatch'
echo 'PASS: 0056 package preflight on Golden; one CCF 300 MHz delta, unarmed'
