#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-static/0074-static-inspection.json
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate/runtime-0072-analysis.json
ATOMIC=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/atomic-runtime-capsules-manifest.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(uname -r)" = '7.1.5-sp11-render-parity-v4+' ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail golden_cmdline
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved_entry
! grep -q '^next_entry=.' <<<"$ENV" || fail next_entry
HEAD=$(git -C "$REPO" rev-parse HEAD); ORIGIN=$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy); [ "$HEAD" = "$ORIGIN" ] || fail git_sync
git -C "$REPO" diff --quiet || fail tracked_dirty
git -C "$REPO" diff --cached --quiet || fail staged
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
python3 - "$NEW/asset-manifest.json" "$STATIC" "$BASE" "$ATOMIC" "$NEW" <<'PY'
import hashlib,json,pathlib,sys
mp,sp,bp,ap,new=sys.argv[1:]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=json.load(open(mp)); s=json.load(open(sp)); b=json.load(open(bp)); a=json.load(open(ap))
assert m['accepted'] and not m['runtime_authorized']
assert m['expected_dqbuf_indices']==[0,1,2,3,0,1] and m['expected_sequences']==[0,1,2,3,4,5]
assert m['live_requeue_indices']==[0,1] and m['live_requeue_after_sequences']==[0,1]
assert m['request4'] and m['request5'] and m['request6'] and m['provider_dequeue_ids']==[5,6]
assert not m['same_boot_retry'] and m['mandatory_golden_reboot']
assert s['accepted'] and not s['runtime_authorized'] and not s['request6_runtime_authorized']
assert s['expected_indices']==[0,1,2,3,0,1] and s['provider_dequeue_ids']==[5,6]
assert b['accepted'] and b['execution']['golden_return_verified'] and b['execution']['helper_invocations']==1
assert b['classification']['accepted_0071_live_requeue_preserved'] and b['classification']['iq_provider_fifo_compatibility_proven']
assert a['accepted']
assert m['static_inspection_sha256']==sha(sp) and m['base_0072_runtime_sha256']==sha(bp) and m['atomic_manifest_sha256']==sha(ap)
for r,h in m['assets'].items(): assert sha(pathlib.Path(new)/r)==h,(r,h)
assert m['assets']['firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin']==a['requests']['4']['output_sha256']
assert m['assets']['firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R5.bin']==a['requests']['5']['output_sha256']
assert m['assets']['firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R6.bin']==a['requests']['6']['output_sha256']
PY
for f in "$NEW"/RUNTIME-V4L2-0074-* "$NEW"/AUTHORIZATION.json "$NEW"/package-inspection.json "$NEW"/runtime-0074-analysis.json "$NEW"/RESULT.md; do [ ! -e "$f" ] || fail prior_runtime_or_auth; done
echo 'PASS: 0074 six-frame request6 package clean on persistent Golden; unarmed'
