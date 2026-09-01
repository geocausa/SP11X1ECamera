#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-five-frame-request5-0070-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-request5-exact-oracle-0070-static
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069r1-candidate/runtime-0069r1-analysis.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail auth_exists
[ ! -e "$NEW/RUNTIME-V4L2-0070-RUN.txt" ] || fail prior_run
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail provenance
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
git -C "$REPO" merge-base --is-ancestor 468e852fbb4a65fe810e32d198e6aedf735cde86 "$HEAD" || fail static_commit
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail Golden
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0070-static-inspection.json" "$STATIC/WINDOWS-REQUEST5-ORACLE.json" "$BASE" <<'PY'
import hashlib,json,pathlib,struct,sys
mp,new,sp,wp,bp=sys.argv[1:]; new=pathlib.Path(new); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp)); si=json.load(open(sp)); wo=json.load(open(wp)); b=json.load(open(bp))
assert m['accepted'] and not m['runtime_authorized']; assert si['accepted'] and not si['runtime_authorized']; assert wo['accepted']; assert b['accepted']
for r,h in m['assets'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
assert sha(sp)==m['static_inspection_sha256']; assert sha(wp)==m['windows_request5_oracle_sha256']; assert sha(bp)==m['base_0069r1_analysis_sha256']
assert b['execution']['golden_return_verified'] and b['qc10c']['all_complete'] and b['qc10c']['all_distinct'] and b['rtcdm']['error']==0 and b['rtcdm']['faulted']==0 and b['rtcdm']['last_userdata']==4
assert si['new_direct_mmio'] is False and si['new_irq_programming'] is False and si['continuous_requeue'] is False and si['frame_limit']==5
assert si['new_hardware_actions']==['existing nine-client BUS retarget to proven-reusable slot0','existing 0x958 five-BL steady submit with request_id=5']
assert wo['exact_request5']['request_id']==5 and wo['cross_stream']['all_samples_same_command_skeleton'] is True
for name,req in [('firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin',4),('firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R5.bin',5)]:
 data=(new/name).read_bytes(); assert len(data)==41088 and struct.unpack_from('<Q',data,0x2c)[0]==req
PY
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camssvermagic
[ "$(modinfo -F vermagic "$NEW/imx681.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail sensorvermagic
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail armed
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ "$(fdtget -l "$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail dt
[ -L /etc/systemd/system/multi-user.target.wants/pislave.service ] || fail pislave
echo 'PASS: 0070 exact request5/static/0069r1 base/Golden safety clean; unarmed'
