#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-candidate
AUTH=$NEW/AUTHORIZATION.json
PKG=$NEW/package-inspection.json
RUNLOG=$NEW/RUNTIME-MODE2-0054-RUN.txt
OUT=$NEW/RUNTIME-MODE2-0054-QC10C.bin
STAGES=$NEW/RUNTIME-MODE2-0054-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-MODE2-0054-WATCHER.ready
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_mode2_0054=1' /proc/cmdline || fail 'not 0054 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-mode2-0054/' /proc/cmdline || fail 'wrong candidate BOOT_IMAGE'
HEAD=$(git -C "$REPO" rev-parse HEAD)
[ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'
git -C "$REPO" diff --cached --quiet || fail 'staged worktree dirty'
[ -f "$AUTH" ] || fail 'authorization file absent'
[ -f "$PKG" ] || fail 'package inspection absent'
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$REPO/provenance/front-parity.json" "$REPO" <<'PY'
import hashlib,json,subprocess,sys
au_path,head,pkg_path,manifest_path,prov_path,repo=sys.argv[1:]
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
au=json.load(open(au_path)); pkg=json.load(open(pkg_path)); man=json.load(open(manifest_path))
assert au.get('accepted') is True and au.get('runtime_authorized') is True and au.get('production_parity_authorized') is False
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',au['package_commit'],head],stdout=subprocess.DEVNULL)
ex=au['execution_contract']; assert ex['boot_count']==1 and ex['root_helper_invocation_count']==1 and ex['same_boot_retry'] is False and ex['persistent_rtcdm_observer_required'] is True
assert au['package_inspection_sha256']==sha(pkg_path) and au['bounded_provenance_sha256']==sha(prov_path)
assert au['boot']['id']=='sp11-camera-e003h-mode2-0054-one-shot' and au['boot']['cmdline_marker']=='sp11_camera_e003h_mode2_0054=1'
assert pkg.get('accepted') is True and pkg.get('candidate_boot_installed') is True and pkg.get('candidate_boot_armed') is False and pkg.get('runtime_authorized') is False
assert man['accepted'] is True and man['runtime_authorized'] is False
for rel,h in man['assets'].items(): assert sha(str(__import__('pathlib').Path(manifest_path).parent/rel))==h,(rel,h)
for k,rel in [('camss_sha256','qcom-camss.ko'),('sensor_sha256','imx681.ko'),('dtb_sha256','x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'),('capsule_sha256','firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'),('helper_sha256','e003h-pix-one-shot')]: assert au['candidate'][k]==man['assets'][rel]
PY
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail 'bounded provenance not green'
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'Golden saved_entry drift'
if grep -q '^next_entry=.' <<<"$ENV"; then fail 'next_entry must be empty after candidate one-shot boot'; fi
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module already loaded: $m"; done
[ ! -e "$RUNLOG" ] || fail 'RUN log already exists; refusing retry'
[ ! -e "$OUT" ] || fail 'output path already exists'
sudo -n test ! -e "$STAGES" || fail 'stages file already exists'
sudo -n test ! -e "$READY" || fail 'watcher ready file already exists'
echo 'PASS: 0054 authorization-aware runtime preflight is clean before module load'
