#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-three-frame-slot-reuse-0068-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-three-frame-slot-reuse-0068-static
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-slot-lifetime-0067-candidate/runtime-0067-analysis.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail auth_exists
[ ! -e "$NEW/RUNTIME-V4L2-0068-RUN.txt" ] || fail prior_run
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail provenance
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
git -C "$REPO" merge-base --is-ancestor 41bbab57a90a20ac942512073fd19f868e1edee0 "$HEAD" || fail static_commit
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail Golden
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0068-static-inspection.json" "$BASE" <<'PY'
import hashlib,json,pathlib,sys
mp,new,sp,bp=sys.argv[1:]; new=pathlib.Path(new); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp)); si=json.load(open(sp)); b=json.load(open(bp))
assert m['accepted'] and not m['runtime_authorized']
for r,h in m['assets'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
assert sha(sp)==m['static_inspection_sha256'] and si['accepted'] and not si['runtime_authorized']
assert sha(bp)==m['base_0067_analysis_sha256'] and b['accepted']
assert b['execution']['golden_return_verified'] and b['qc10c']['both_complete']
assert b['classification']['both_two_slot_bundles_reusable'] is True
assert si['delta']['new_mmio_primitive_calls']==0 and si['delta']['new_register_literals']==0
assert si['delta']['slot0_rebind_requires_prior_five_group_retirement'] is True
assert si['delta']['continuous_requeue_not_authorized'] is True
assert si['delta']['new_hardware_actions']==['one existing nine-client BUS update targeting reused slot0','one existing replay3/request3 submission']
for r,h in m['unchanged_from_0067'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
PY
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camssvermagic
[ "$(modinfo -F vermagic "$NEW/imx681.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail sensorvermagic
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail armed
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ "$(fdtget -l "$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail dt
[ -L /etc/systemd/system/multi-user.target.wants/pislave.service ] || fail pislave
echo 'PASS: 0068 static authority/0067 reusable-slot base/Golden safety clean; unarmed'
