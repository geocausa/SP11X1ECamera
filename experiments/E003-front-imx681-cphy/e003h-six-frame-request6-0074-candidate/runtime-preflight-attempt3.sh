#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
AUTH=$NEW/AUTHORIZATION-ATTEMPT3.json
PKG=$NEW/package-inspection.json
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-static/0074-static-inspection.json
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate/runtime-0072-analysis.json
ATOMIC=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/atomic-runtime-capsules-manifest.json
PROV=$REPO/provenance/front-parity.json
A1=$NEW/ATTEMPT-0074-CLASSIFICATION.txt
G1=$NEW/GOLDEN-RETURN-0074-ATTEMPT1.txt
A2FAIL=$NEW/ATTEMPT2-BOOT-HANG-CLASSIFICATION.txt
BOOTPASS=$NEW/BOOTDIAG-PWRKEEP-RESULT.txt
BOOTPOST=$NEW/BOOTDIAG-PWRKEEP-POSTCHECK.txt
CONTRACT=$NEW/ATTEMPT3-RUNTIME-CONTRACT.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
CMD=$(cat /proc/cmdline)
for tok in 'sp11_camera_e003h_request6_0074_attempt3_pwrkeep=1' 'sp11_entry=7.1.5-sp11-camera-e003h-request6-0074-attempt3-pwrkeep' 'clk_ignore_unused' 'pd_ignore_unused' 'modprobe.blacklist=qcom_camss,imx681,ov13858'; do
  grep -Fq "$tok" <<<"$CMD" || fail "boot_token_$tok"
done
# Boot health must be pristine before any camera module load.
K=$(mktemp); trap 'rm -f "$K"' EXIT
journalctl -b -k --no-pager >"$K"
for needle in 'TLB sync timed out -- SMMU may be deadlocked' 'vblank wait timed out' 'Internal error: Oops' 'soft lockup'; do
  ! grep -Fiq "$needle" "$K" || fail "boot_health_$needle"
done
systemctl is-active --quiet pislave.service || fail pislave
HEAD=$(git -C "$REPO" rev-parse HEAD); ORIGIN=$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy); [ "$HEAD" = "$ORIGIN" ] || fail git_sync
git -C "$REPO" diff --quiet || fail tracked_dirty; git -C "$REPO" diff --cached --quiet || fail staged
sudo -n true || fail sudo_noninteractive
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$STATIC" "$BASE" "$ATOMIC" "$PROV" "$CONTRACT" "$A1" "$G1" "$A2FAIL" "$BOOTPASS" "$BOOTPOST" "$REPO" "$NEW" <<'PY2'
import hashlib,json,pathlib,subprocess,sys
ap,head,pp,mp,sp,bp,atp,prov,cp,a1p,g1p,a2fp,bpass,bpost,repo,new=sys.argv[1:]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
a=json.load(open(ap)); p=json.load(open(pp)); m=json.load(open(mp)); s=json.load(open(sp)); b=json.load(open(bp)); at=json.load(open(atp)); c=json.load(open(cp))
assert a['accepted'] and a['runtime_authorized'] and a['attempt']==3 and not a['production_parity_authorized']
assert a['runtime_contract_sha256']==sha(cp) and a['package_inspection_sha256']==sha(pp) and a['asset_manifest_sha256']==sha(mp)
assert a['static_inspection_sha256']==sha(sp) and a['base_0072_runtime_sha256']==sha(bp) and a['atomic_manifest_sha256']==sha(atp) and a['bounded_provenance_sha256']==sha(prov)
assert a['attempt1_classification_sha256']==sha(a1p) and a['attempt1_golden_return_sha256']==sha(g1p)
assert a['attempt2_boot_hang_classification_sha256']==sha(a2fp)
assert a['bootdiag_pwrkeep_result_sha256']==sha(bpass) and a['bootdiag_pwrkeep_postcheck_sha256']==sha(bpost)
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['runtime_contract_commit'],head],stdout=subprocess.DEVNULL)
assert p['accepted'] and p['candidate_boot_installed'] and p['golden_saved_default'] and p['request6']
assert p['expected_indices']==[0,1,2,3,0,1] and p['expected_sequences']==[0,1,2,3,4,5]
assert s['accepted'] and not s['runtime_authorized'] and not s['request6_runtime_authorized']
assert b['accepted'] and b['execution']['golden_return_verified'] and at['accepted']
assert 'result=PASS' in pathlib.Path(bpass).read_text()
for needle in ['smmu_tlb_sync_deadlocks=0','dpu_vblank_timeouts=0','oops=0','soft_lockups=0','camera_runtime_executed=false']:
    assert needle in pathlib.Path(bpass).read_text(),needle
assert c['accepted'] and c['attempt']==3 and c['privileged_media_setup'] and c['privileged_helper']
assert c['preopen_privilege_gate'] and c['atomic_helper_invocation_gate'] and c['expected_indices']==[0,1,2,3,0,1]
assert c['boot_health_gate'] and c['clk_ignore_unused'] and c['pd_ignore_unused']
for r,h in m['assets'].items(): assert sha(pathlib.Path(new)/r)==h,(r,h)
for r,h in c['script_sha256'].items(): assert sha(pathlib.Path(new)/r)==h,(r,h)
PY2
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
for i in 0 1 2 3 4 5; do sudo -n test ! -e "$NEW/RUNTIME-V4L2-0074-A3-QC10C-$i.bin" || fail prior_a3_output; done
for f in "$NEW"/RUNTIME-V4L2-0074-A3-{RUN.txt,RTCDM-STAGES.txt,WATCHER.ready,POST.txt,DMESG.txt,HASHES.txt,MEDIA.txt} "$NEW/ATTEMPT3-HELPER-CONSUMED.marker"; do sudo -n test ! -e "$f" || fail prior_a3_runtime; done
echo 'PASS: 0074 attempt3 hardened boot + authorization-aware preflight clean; sudo ready; no A3 runtime consumed'
