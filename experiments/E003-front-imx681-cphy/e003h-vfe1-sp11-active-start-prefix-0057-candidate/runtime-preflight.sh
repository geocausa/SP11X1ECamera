#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-candidate
AUTH=$NEW/AUTHORIZATION.json
PKG=$NEW/package-inspection.json
RUNLOG=$NEW/RUNTIME-VFEACTIVE-0057-RUN.txt
OUT=$NEW/RUNTIME-VFEACTIVE-0057-QC10C.bin
STAGES=$NEW/RUNTIME-VFEACTIVE-0057-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-VFEACTIVE-0057-WATCHER.ready
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_vfeactive_0057=1' /proc/cmdline || fail 'not 0057 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-vfeactive-0057/' /proc/cmdline || fail 'wrong candidate BOOT_IMAGE'
HEAD=$(git -C "$REPO" rev-parse HEAD)
[ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'
git -C "$REPO" diff --cached --quiet || fail 'staged worktree dirty'
[ -f "$AUTH" ] || fail 'authorization file absent'
[ -f "$PKG" ] || fail 'package inspection absent'
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$REPO/provenance/front-parity.json" "$REPO" <<'PY'
import hashlib,json,subprocess,sys,pathlib
ap,head,pp,mp,prov,repo=sys.argv[1:]; sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); a=json.load(open(ap)); p=json.load(open(pp)); m=json.load(open(mp))
assert a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']; subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['package_commit'],head],stdout=subprocess.DEVNULL)
assert a['package_inspection_sha256']==sha(pp) and a['asset_manifest_sha256']==sha(mp) and a['bounded_provenance_sha256']==sha(prov)
e=a['execution_contract']; assert e['boot_count']==1 and e['root_helper_invocation_count']==1 and e['same_boot_retry'] is False and e['persistent_rtcdm_observer_required'] is True
assert e['hardware_delta']=='VFE1_SP11_ACTIVE_DAL_PREFIX_0057_ONLY'
assert p['accepted'] and p['candidate_boot_installed'] and not p['candidate_boot_armed'] and not p['runtime_authorized']; assert m['accepted'] and not m['runtime_authorized']
for r,h in m['assets'].items(): assert sha(pathlib.Path(mp).parent/r)==h,(r,h)
PY
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail 'bounded provenance not green'
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'Golden saved_entry drift'; ! grep -q '^next_entry=.' <<<"$ENV" || fail 'next_entry must be empty after one-shot boot'
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module already loaded: $m"; done
[ ! -e "$RUNLOG" ] || fail 'RUN log already exists; refusing retry'
[ ! -e "$OUT" ] || fail 'output path already exists'
sudo -n test ! -e "$STAGES" || fail 'stages file already exists'; sudo -n test ! -e "$READY" || fail 'watcher ready file already exists'
echo 'PASS: 0057 authorization-aware runtime preflight clean before module load'
