#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-static/0072-static-inspection.json
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-live-requeue-0071-candidate/runtime-0071-analysis.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(uname -r)" = '7.1.5-sp11-render-parity-v4+' ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail golden_cmdline
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved_entry
! grep -q '^next_entry=.' <<<"$ENV" || fail next_entry
HEAD=$(git -C "$REPO" rev-parse HEAD); ORIGIN=$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy); [ "$HEAD" = "$ORIGIN" ] || fail git_sync
git -C "$REPO" diff --quiet || fail tracked_dirty; git -C "$REPO" diff --cached --quiet || fail staged
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
python3 - "$NEW/asset-manifest.json" "$STATIC" "$BASE" "$NEW" <<'PY'
import hashlib,json,pathlib,sys
mp,sp,bp,new=sys.argv[1:]; sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=json.load(open(mp)); s=json.load(open(sp)); b=json.load(open(bp))
assert m['accepted'] and not m['runtime_authorized'] and m['hardware_delta']=='NONE' and not m['request6']
assert s['accepted'] and not s['runtime_authorized'] and not s['request6_runtime_authorized']
assert b['accepted'] and b['classification']['first_live_v4l2_dqbuf_qbuf_requeue_achieved']
assert m['static_inspection_sha256']==sha(sp) and m['base_0071_runtime_sha256']==sha(bp)
for r,h in m['assets'].items(): assert sha(pathlib.Path(new)/r)==h,(r,h)
PY
for f in "$NEW"/RUNTIME-V4L2-0072-* "$NEW"/AUTHORIZATION.json "$NEW"/package-inspection.json; do [ ! -e "$f" ] || fail prior_runtime_or_auth; done
echo 'PASS: 0072 IQ FIFO regression package clean on Golden; unarmed'
