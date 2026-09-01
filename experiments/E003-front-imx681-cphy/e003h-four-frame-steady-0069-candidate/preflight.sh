#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069-static
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-three-frame-slot-reuse-0068-candidate/runtime-0068-analysis.json
OLD_CAP=$REPO/experiments/E003-front-imx681-cphy/e003h-three-frame-slot-reuse-0068-candidate/firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail auth_exists
[ ! -e "$NEW/RUNTIME-V4L2-0069-RUN.txt" ] || fail prior_run
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail provenance
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
git -C "$REPO" merge-base --is-ancestor 58319634e4a57e70f0c4cb3c758838ca9867841f "$HEAD" || fail static_commit
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail Golden
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0069-static-inspection.json" "$BASE" "$OLD_CAP" <<'PY'
import hashlib,json,pathlib,struct,sys
mp,new,sp,bp,op=sys.argv[1:]; new=pathlib.Path(new); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp)); si=json.load(open(sp)); b=json.load(open(bp))
assert m['accepted'] and not m['runtime_authorized']
for r,h in m['assets'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
assert sha(sp)==m['static_inspection_sha256'] and si['accepted'] and not si['runtime_authorized']
assert sha(bp)==m['base_0068_analysis_sha256'] and b['accepted']
assert b['execution']['golden_return_verified'] and b['qc10c']['all_complete'] and b['qc10c']['all_sha_distinct']
assert b['classification']['first_actual_two_slot_hardware_reuse_achieved'] is True
assert si['delta']['new_mmio_primitive_calls']==0 and si['delta']['new_register_literals']==0
assert si['delta']['slot1_rebind_requires_prior_five_group_retirement'] is True
assert si['delta']['continuous_requeue_not_authorized'] is True and si['delta']['asynchronous_streamon_not_authorized'] is True
assert si['delta']['new_hardware_actions']==['one existing nine-client BUS update targeting proven-reusable slot1','one existing five-BL steady 0x958/request4 submission']
for r,h in m['unchanged_from_0068'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
old=pathlib.Path(op).read_bytes(); cap=(new/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin').read_bytes(); dif=[i for i,(a,z) in enumerate(zip(old,cap)) if a!=z]
assert len(old)==len(cap)==41088 and dif==[0x2c] and struct.unpack_from('<Q',old,0x2c)[0]==2 and struct.unpack_from('<Q',cap,0x2c)[0]==4
assert m['capsule_delta']['only_byte_diff']=='0x2c: 0x02 -> 0x04' and m['capsule_delta']['request_id']==4
PY
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camssvermagic
[ "$(modinfo -F vermagic "$NEW/imx681.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail sensorvermagic
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail armed
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ "$(fdtget -l "$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail dt
[ -L /etc/systemd/system/multi-user.target.wants/pislave.service ] || fail pislave
echo 'PASS: 0069 static authority/0068 three-frame reuse base/Golden safety clean; unarmed'
