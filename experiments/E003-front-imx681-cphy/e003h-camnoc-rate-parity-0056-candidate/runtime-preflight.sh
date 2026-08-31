#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-parity-0056-candidate
AUTH=$NEW/AUTHORIZATION.json
PKG=$NEW/package-inspection.json
RUN=$NEW/RUNTIME-CAMNOC300-0056-RUN.txt
OUT=$NEW/RUNTIME-CAMNOC300-0056-QC10C.bin
STAGES=$NEW/RUNTIME-CAMNOC300-0056-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-CAMNOC300-0056-WATCHER.ready
CLOCK=$NEW/RUNTIME-CAMNOC300-0056-CLOCK.txt
CREADY=$NEW/RUNTIME-CAMNOC300-0056-CLOCK.ready
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_camnoc300_0056=1' /proc/cmdline || fail 'not 0056 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-camnoc300-0056/' /proc/cmdline || fail 'wrong candidate BOOT_IMAGE'
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'; git -C "$REPO" diff --quiet || fail 'tracked dirty'; git -C "$REPO" diff --cached --quiet || fail 'staged dirty'
[ -f "$AUTH" ] || fail 'authorization absent'; [ -f "$PKG" ] || fail 'package inspection absent'
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$REPO" <<'PY'
import hashlib,json,subprocess,sys,pathlib
ap,head,pp,mp,repo=sys.argv[1:]; sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); a=json.load(open(ap)); p=json.load(open(pp)); m=json.load(open(mp))
assert a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']; subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['package_commit'],head],stdout=subprocess.DEVNULL)
assert a['package_inspection_sha256']==sha(pp); assert a['asset_manifest_sha256']==sha(mp)
e=a['execution_contract']; assert e['boot_count']==1 and e['root_helper_invocation_count']==1 and e['same_boot_retry'] is False and e['camnoc_rate_hz']==300000000
assert p['accepted'] and p['candidate_boot_installed'] and not p['candidate_boot_armed'] and not p['runtime_authorized']; assert m['accepted'] and not m['runtime_authorized']
for r,h in m['assets'].items(): assert sha(pathlib.Path(mp).parent/r)==h,(r,h)
PY
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'Golden saved_entry drift'; ! grep -q '^next_entry=.' <<<"$ENV" || fail 'next_entry must be empty after one-shot boot'
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module already loaded: $m"; done
for p in "$RUN" "$OUT" "$STAGES" "$READY" "$CLOCK" "$CREADY"; do sudo -n test ! -e "$p" || fail "prior runtime artifact exists: $p"; done
echo 'PASS: 0056 authorization-aware runtime preflight clean before module load'
