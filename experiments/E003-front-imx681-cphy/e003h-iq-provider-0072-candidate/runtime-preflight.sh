#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate
AUTH=$NEW/AUTHORIZATION.json; PKG=$NEW/package-inspection.json; STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-static/0072-static-inspection.json; BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-live-requeue-0071-candidate/runtime-0071-analysis.json; PROV=$REPO/provenance/front-parity.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
grep -q 'sp11_camera_e003h_iqfifo_0072=1' /proc/cmdline || fail boot
grep -q 'sp11_entry=7.1.5-sp11-camera-e003h-iqfifo-0072' /proc/cmdline || fail entry
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
python3 - "$AUTH" "$HEAD" "$PKG" "$NEW/asset-manifest.json" "$STATIC" "$BASE" "$PROV" "$REPO" <<'PY'
import hashlib,json,pathlib,subprocess,sys
ap,head,pp,mp,sp,bp,prov,repo=sys.argv[1:]; sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
a=json.load(open(ap)); p=json.load(open(pp)); m=json.load(open(mp)); s=json.load(open(sp)); b=json.load(open(bp))
assert a['accepted'] and a['runtime_authorized'] and not a['production_parity_authorized']
subprocess.check_call(['git','-C',repo,'merge-base','--is-ancestor',a['installed_commit'],head],stdout=subprocess.DEVNULL)
assert a['package_inspection_sha256']==sha(pp) and a['asset_manifest_sha256']==sha(mp) and a['static_inspection_sha256']==sha(sp) and a['base_0071_runtime_sha256']==sha(bp) and a['bounded_provenance_sha256']==sha(prov)
assert p['accepted'] and p['candidate_boot_installed'] and not p['candidate_boot_armed'] and not p['runtime_authorized'] and p['hardware_delta']=='NONE' and not p['request6']
assert s['accepted'] and not s['runtime_authorized'] and not s['request6_runtime_authorized']
assert b['accepted'] and b['classification']['first_live_v4l2_dqbuf_qbuf_requeue_achieved']
e=a['execution_contract']; assert e['boot_count']==1 and e['v4l2_helper_invocation_count']==1 and e['sysfs_trigger_invocations']==0
assert e['initial_qbuf_count']==4 and e['expected_dqbuf_count']==5 and e['expected_indices']==[0,1,2,3,0] and e['expected_sequences']==[0,1,2,3,4]
assert e['live_requeue_count']==1 and e['live_requeue_index']==0 and e['live_requeue_after_sequence']==0 and e['asynchronous_streamon']
assert e['request4'] and e['request5'] and e['request5_via_iq_provider_fifo'] and not e['request6'] and not e['continuous_loop'] and e['hardware_delta_from_0071']=='NONE' and not e['same_boot_retry']
for r,h in m['assets'].items(): assert sha(pathlib.Path(mp).parent/r)==h,(r,h)
PY
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
for f in "$NEW"/RUNTIME-V4L2-0072-{RUN.txt,QC10C-0.bin,QC10C-1.bin,QC10C-2.bin,QC10C-3.bin,QC10C-4.bin,RTCDM-STAGES.txt,WATCHER.ready}; do sudo -n test ! -e "$f" || fail prior_runtime; done
echo 'PASS: 0072 authorization-aware IQ FIFO regression preflight clean'
