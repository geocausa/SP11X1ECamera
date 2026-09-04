#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
AUTH=$NEW/AUTHORIZATION-ATTEMPT2.json
PKG=$NEW/package-inspection.json
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-static/0074-static-inspection.json
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate/runtime-0072-analysis.json
ATOMIC=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/atomic-runtime-capsules-manifest.json
PROV=$REPO/provenance/front-parity.json
A1=$NEW/ATTEMPT-0074-CLASSIFICATION.txt
G1=$NEW/GOLDEN-RETURN-0074-ATTEMPT1.txt
CONTRACT=$NEW/ATTEMPT2-RUNTIME-CONTRACT.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_request6_0074=1' /proc/cmdline || fail boot
grep -q 'sp11_entry=7.1.5-sp11-camera-e003h-request6-0074' /proc/cmdline || fail entry
HEAD=$(git -C "$REPO" rev-parse HEAD); ORIGIN=$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy); [ "$HEAD" = "$ORIGIN" ] || fail git_sync
git -C "$REPO" diff --quiet || fail tracked_dirty; git -C "$REPO" diff --cached --quiet || fail staged
sudo -n true || fail sudo_noninteractive
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$STATIC" "$BASE" "$ATOMIC" "$PROV" "$CONTRACT" "$A1" "$G1" "$REPO" "$NEW" <<'PY'
import hashlib,json,pathlib,subprocess,sys
ap,head,pp,mp,sp,bp,atp,prov,cp,a1p,g1p,repo,new=sys.argv[1:]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
a=json.load(open(ap)); p=json.load(open(pp)); m=json.load(open(mp)); s=json.load(open(sp)); b=json.load(open(bp)); at=json.load(open(atp)); c=json.load(open(cp))
assert a['accepted'] and a['runtime_authorized'] and a['attempt']==2 and not a['production_parity_authorized']
assert a['runtime_contract_sha256']==sha(cp) and a['package_inspection_sha256']==sha(pp) and a['asset_manifest_sha256']==sha(mp)
assert a['static_inspection_sha256']==sha(sp) and a['base_0072_runtime_sha256']==sha(bp) and a['atomic_manifest_sha256']==sha(atp) and a['bounded_provenance_sha256']==sha(prov)
assert a['attempt1_classification_sha256']==sha(a1p) and a['attempt1_golden_return_sha256']==sha(g1p)
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['runtime_contract_commit'],head],stdout=subprocess.DEVNULL)
assert p['accepted'] and p['candidate_boot_installed'] and p['golden_saved_default'] and p['request6']
assert p['expected_indices']==[0,1,2,3,0,1] and p['expected_sequences']==[0,1,2,3,4,5]
assert s['accepted'] and not s['runtime_authorized'] and not s['request6_runtime_authorized']
assert b['accepted'] and b['execution']['golden_return_verified'] and at['accepted']
a1=pathlib.Path(a1p).read_text(); g1=pathlib.Path(g1p).read_text()
for needle in ['AUTHORIZATION_CONSUMED_PREOPEN_PERMISSION_FAILURE','STREAMON_INVOCATIONS=0','KERNEL_REQUEST6_EXECUTED=false','SAME_BOOT_RETRY=false']:
    assert needle in a1,needle
for needle in ['sp11_entry=7.1.5-sp11-fullio-v19c','next_entry=','qcom_camss=absent','imx681=absent']:
    assert needle in g1,needle
assert c['accepted'] and c['attempt']==2 and c['privileged_media_setup'] and c['privileged_helper']
assert c['preopen_privilege_gate'] and c['atomic_helper_invocation_gate'] and c['expected_indices']==[0,1,2,3,0,1]
for r,h in m['assets'].items(): assert sha(pathlib.Path(new)/r)==h,(r,h)
for r,h in c['script_sha256'].items(): assert sha(pathlib.Path(new)/r)==h,(r,h)
PY
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
for i in 0 1 2 3 4 5; do sudo -n test ! -e "$NEW/RUNTIME-V4L2-0074-A2-QC10C-$i.bin" || fail prior_a2_output; done
for f in "$NEW"/RUNTIME-V4L2-0074-A2-{RUN.txt,RTCDM-STAGES.txt,WATCHER.ready,POST.txt,DMESG.txt,HASHES.txt,MEDIA.txt} "$NEW/ATTEMPT2-HELPER-CONSUMED.marker"; do sudo -n test ! -e "$f" || fail prior_a2_runtime; done
echo 'PASS: 0074 attempt2 authorization-aware preflight clean; sudo ready; no A2 runtime consumed'
