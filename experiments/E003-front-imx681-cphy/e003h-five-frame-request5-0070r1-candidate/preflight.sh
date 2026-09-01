#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-five-frame-request5-0070r1-candidate
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-five-frame-request5-0070-candidate
FAIL=$BASE/runtime-0070-pre-capture-consumed-analysis.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail auth_exists
[ ! -e "$NEW/RUNTIME-V4L2-0070R1-RUN.txt" ] || fail prior_run
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail golden
python3 - "$NEW/asset-manifest.json" "$NEW" "$BASE" "$FAIL" <<'PY'
import hashlib,json,pathlib,sys
mp,np,bp,fp=sys.argv[1:]; n=pathlib.Path(np); b=pathlib.Path(bp); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp)); f=json.load(open(fp))
assert m['accepted'] and not m['runtime_authorized']; assert f['accepted'] and f['camera_transaction_started'] is False and f['video_device_opened'] is False and f['streamon_called'] is False and f['rtcdm_idle'] is True and f['same_boot_retry_refused'] is True and f['golden_return_verified'] is True
assert sha(fp)==m['base_0070_consumed_analysis_sha256']; assert m['asset_identity_to_0070']=='BYTE_IDENTICAL'; assert m['retry_scope']['new_camera_hardware_delta_from_0070']=='NONE'
for r,h in m['assets'].items(): assert sha(n/r)==h and sha(b/r)==h,(r,h)
PY
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camssvermagic
[ "$(modinfo -F vermagic "$NEW/imx681.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail sensorvermagic
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail armed
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ "$(fdtget -l "$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail dt
[ -L /etc/systemd/system/multi-user.target.wants/pislave.service ] || fail pislave
echo 'PASS: 0070r1 byte-identical request5 retry/0070 zero-transaction record/Golden safety clean; unarmed'
