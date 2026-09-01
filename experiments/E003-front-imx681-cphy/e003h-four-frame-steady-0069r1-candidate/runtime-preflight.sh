#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069r1-candidate
AUTH=$NEW/AUTHORIZATION.json; PKG=$NEW/package-inspection.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_frame4_0069r1=1' /proc/cmdline || fail boot
grep -q 'sp11_entry=7.1.5-sp11-camera-e003h-frame4-0069r1' /proc/cmdline || fail entry
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
[ -f "$AUTH" ] && [ -f "$PKG" ] || fail auth_package
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$REPO/provenance/front-parity.json" "$REPO" <<'PY'
import hashlib,json,pathlib,subprocess,sys
ap,head,pp,mp,prov,repo=sys.argv[1:]; sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); a=json.load(open(ap)); p=json.load(open(pp)); m=json.load(open(mp))
assert a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']; subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['package_commit'],head],stdout=subprocess.DEVNULL)
assert a['package_inspection_sha256']==sha(pp) and a['asset_manifest_sha256']==sha(mp) and a['bounded_provenance_sha256']==sha(prov)
e=a['execution_contract']; assert e['boot_count']==1 and e['v4l2_helper_invocation_count']==1 and e['expected_dqbuf_count']==4 and e['same_boot_retry'] is False and e['sysfs_trigger_invocations']==0
assert e['slot_reuse'] is True and e['continuous_requeue'] is False and e['asynchronous_streamon'] is False and e['fifth_frame'] is False and e['forced_cci_rebind_or_reset'] is False
assert e['authorized_hardware_actions']==['one existing complete nine-client BUS retarget to proven-reusable slot1','one existing five-BL steady 0x958/request4 submission']
assert p['accepted'] and p['candidate_boot_installed'] and not p['candidate_boot_armed'] and not p['runtime_authorized']; assert m['accepted'] and not m['runtime_authorized'] and m['asset_identity_to_0069']=='BYTE_IDENTICAL'
for r,h in m['assets'].items(): assert sha(pathlib.Path(mp).parent/r)==h,(r,h)
PY
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
for f in "$NEW"/RUNTIME-V4L2-0069R1-{RUN.txt,QC10C-0.bin,QC10C-1.bin,QC10C-2.bin,QC10C-3.bin,RTCDM-STAGES.txt,WATCHER.ready}; do sudo -n test ! -e "$f" || fail prior_runtime; done
echo 'PASS: 0069r1 authorization-aware preflight clean before module load'
