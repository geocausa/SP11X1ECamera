#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate
AUTH=$NEW/AUTHORIZATION.json
PKG=$NEW/package-inspection.json
RUNLOG=$NEW/RUNTIME-VFEAP-0058-RUN.txt
OUT=$NEW/RUNTIME-VFEAP-0058-QC10C.bin
STAGES=$NEW/RUNTIME-VFEAP-0058-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-VFEAP-0058-RTCDM.ready
VFELOG=$NEW/RUNTIME-VFEAP-0058-APERTURE.json
VFEREADY=$NEW/RUNTIME-VFEAP-0058-APERTURE.ready
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_vfeap_0058=1' /proc/cmdline || fail 'not 0058 candidate boot'
grep -q '/boot/sp11-7.1.5-camera-e003h-vfeap-0058/' /proc/cmdline || fail 'wrong candidate BOOT_IMAGE'
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'; git -C "$REPO" diff --cached --quiet || fail 'staged worktree dirty'
[ -f "$AUTH" ] || fail 'authorization absent'; [ -f "$PKG" ] || fail 'package inspection absent'
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$REPO/provenance/front-parity.json" "$REPO" <<'PY'
import hashlib,json,subprocess,sys,pathlib
ap,head,pp,mp,prov,repo=sys.argv[1:]; sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); a=json.load(open(ap)); p=json.load(open(pp)); m=json.load(open(mp))
assert a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']; subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['package_commit'],head],stdout=subprocess.DEVNULL)
assert a['package_inspection_sha256']==sha(pp) and a['asset_manifest_sha256']==sha(mp) and a['bounded_provenance_sha256']==sha(prov)
e=a['execution_contract']; assert e['boot_count']==1 and e['root_helper_invocation_count']==1 and e['same_boot_retry'] is False and e['persistent_rtcdm_observer_required'] and e['persistent_vfe_aperture_observer_required']; assert e['hardware_delta']=='NONE_VS_CONSUMED_0057_READ_ONLY_VFE_APERTURE_TELEMETRY'
assert p['accepted'] and not p['runtime_authorized']; assert m['accepted'] and not m['runtime_authorized']
for r,h in m['assets'].items(): assert sha(pathlib.Path(mp).parent/r)==h,(r,h)
PY
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail 'bounded provenance not green'
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'Golden saved_entry drift'; ! grep -q '^next_entry=.' <<<"$ENV" || fail 'next_entry must be empty after one-shot boot'
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module already loaded: $m"; done
for f in "$RUNLOG" "$OUT" "$STAGES" "$READY" "$VFELOG" "$VFEREADY"; do sudo -n test ! -e "$f" || fail "prior runtime artifact exists: $f"; done
echo 'PASS: 0058 authorization-aware runtime preflight clean before module load'
