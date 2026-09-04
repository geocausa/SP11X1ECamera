#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
AUTH=$NEW/AUTHORIZATION.json
PKG=$NEW/package-inspection.json
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-static/0074-static-inspection.json
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate/runtime-0072-analysis.json
ATOMIC=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/atomic-runtime-capsules-manifest.json
PROV=$REPO/provenance/front-parity.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_request6_0074=1' /proc/cmdline || fail boot
grep -q 'sp11_entry=7.1.5-sp11-camera-e003h-request6-0074' /proc/cmdline || fail entry
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$STATIC" "$BASE" "$ATOMIC" "$PROV" "$REPO" "$NEW" <<'PY'
import hashlib,json,pathlib,subprocess,sys
ap,head,pp,mp,sp,bp,atp,prov,repo,new=sys.argv[1:]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
a=json.load(open(ap)); p=json.load(open(pp)); m=json.load(open(mp)); s=json.load(open(sp)); b=json.load(open(bp)); at=json.load(open(atp))
assert a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['installed_commit'],head],stdout=subprocess.DEVNULL)
assert a['package_inspection_sha256']==sha(pp) and a['asset_manifest_sha256']==sha(mp)
assert a['static_inspection_sha256']==sha(sp) and a['base_0072_runtime_sha256']==sha(bp)
assert a['atomic_manifest_sha256']==sha(atp) and a['bounded_provenance_sha256']==sha(prov)
assert p['accepted'] and p['candidate_boot_installed'] and not p['candidate_boot_armed']
assert p['golden_saved_default'] and p['request6'] and p['expected_indices']==[0,1,2,3,0,1]
assert s['accepted'] and not s['runtime_authorized'] and not s['request6_runtime_authorized']
assert b['accepted'] and b['execution']['golden_return_verified']
assert at['accepted']
e=a['execution_contract']
assert e['boot_count']==1 and e['v4l2_helper_invocation_count']==1 and e['sysfs_trigger_invocations']==0
assert e['initial_qbuf_count']==4 and e['expected_dqbuf_count']==6
assert e['expected_indices']==[0,1,2,3,0,1] and e['expected_sequences']==[0,1,2,3,4,5]
assert e['live_requeue_count']==2 and e['live_requeue_indices']==[0,1] and e['live_requeue_after_sequences']==[0,1]
assert e['request4'] and e['request5'] and e['request6'] and e['request5_via_iq_provider_fifo'] and e['request6_via_iq_provider_fifo']
assert e['provider_dequeue_ids']==[5,6] and e['asynchronous_streamon'] and not e['continuous_loop'] and not e['same_boot_retry']
assert e['mandatory_golden_reboot'] and e['hardware_delta_from_0072']=='EXACTLY_ONE_STEADY_REQUEST6_PLUS_SLOT1_REBIND_AND_SECOND_LIVE_REQUEUE'
for r,h in m['assets'].items(): assert sha(pathlib.Path(new)/r)==h,(r,h)
PY
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
for i in 0 1 2 3 4 5; do sudo -n test ! -e "$NEW/RUNTIME-V4L2-0074-QC10C-$i.bin" || fail prior_runtime; done
for f in "$NEW"/RUNTIME-V4L2-0074-{RUN.txt,RTCDM-STAGES.txt,WATCHER.ready,POST.txt,DMESG.txt,HASHES.txt}; do sudo -n test ! -e "$f" || fail prior_runtime; done
echo 'PASS: 0074 authorization-aware request6 runtime preflight clean'
