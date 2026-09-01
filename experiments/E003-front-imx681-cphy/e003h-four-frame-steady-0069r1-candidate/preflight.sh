#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069r1-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069-static
PREV=$REPO/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069-candidate/runtime-0069-pre-capture-failure-analysis.json
ORIG=$REPO/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069-candidate
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail auth_exists
[ ! -e "$NEW/RUNTIME-V4L2-0069R1-RUN.txt" ] || fail prior_run
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail provenance
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
git -C "$REPO" merge-base --is-ancestor 095dad351fc582906c98e9a461a579ae5d655ee4 "$HEAD" || fail prev_failure_commit
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail Golden
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0069-static-inspection.json" "$PREV" "$ORIG" <<'PY'
import hashlib,json,pathlib,sys
mp,new,sp,fp,orig=sys.argv[1:]; new=pathlib.Path(new); orig=pathlib.Path(orig); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp)); si=json.load(open(sp)); f=json.load(open(fp))
assert m['accepted'] and not m['runtime_authorized']; assert si['accepted'] and not si['runtime_authorized']; assert f['accepted']
assert sha(sp)==m['static_inspection_sha256']; assert sha(fp)==m['previous_0069_failure_analysis_sha256']
assert f['classification']['camera_transaction_not_started'] and f['classification']['helper_invocation_count']==0 and f['classification']['streamon_count']==0 and f['observations']['forced_sysfs_cci_rebind_performed'] is False
for r,h in m['assets'].items(): assert sha(new/r)==h and sha(orig/r)==h,(r,sha(new/r),sha(orig/r),h)
assert m['asset_identity_to_0069']=='BYTE_IDENTICAL' and m['retry_scope']['new_camera_hardware_delta_from_0069']=='NONE'
assert m['retry_scope']['previous_helper_invocations']==0 and m['retry_scope']['previous_streamon_count']==0 and m['retry_scope']['forced_cci_rebind_or_reset'] is False
assert m['execution_scope']['expected_dqbuf_count']==4 and m['execution_scope']['fifth_frame'] is False and m['execution_scope']['continuous_requeue'] is False and m['execution_scope']['asynchronous_streamon'] is False
PY
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camssvermagic
[ "$(modinfo -F vermagic "$NEW/imx681.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail sensorvermagic
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail armed
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ "$(fdtget -l "$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail dt
[ -L /etc/systemd/system/multi-user.target.wants/pislave.service ] || fail pislave
echo 'PASS: 0069r1 byte-identical retry package/previous pre-capture failure/Golden safety clean; unarmed'
