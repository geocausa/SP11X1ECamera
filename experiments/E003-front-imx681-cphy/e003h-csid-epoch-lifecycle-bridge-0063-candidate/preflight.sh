#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid-epoch-lifecycle-bridge-0063-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-csid-epoch-lifecycle-bridge-0063-static
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-cgc-release-0062r1-candidate/runtime-0062r1-analysis.json
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail auth_exists
[ ! -e "$NEW/RUNTIME-CSIDEPOCH-0063-RUN.txt" ] || fail prior_run
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail provenance
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
git -C "$REPO" merge-base --is-ancestor 91aa6049e23f06c702856eaf66fb4617f3f05dac "$HEAD" || fail static_commit
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail Golden
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0063-static-inspection.json" "$BASE" <<'PY'
import hashlib,json,pathlib,sys
mp,new,sp,bp=sys.argv[1:]; new=pathlib.Path(new); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp)); si=json.load(open(sp)); b=json.load(open(bp))
assert m['accepted'] and not m['runtime_authorized'];
for r,h in m['assets'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
assert sha(sp)==m['static_inspection_sha256'] and si['accepted'] and not si['runtime_authorized']
assert si['module_sha256']==m['assets']['qcom-camss.ko']; d=si['delta']; assert d['new_mmio_reads']==d['new_mmio_writes']==d['new_register_values']==0 and not d['new_hardware_programming'] and d['runner_epoch_source']=='CSID1_IPP_ISR_latched_bit21'
assert sha(bp)==m['base_0062r1_analysis_sha256'] and b['accepted'] and b['golden_return_verified'] and b['csid_geometry']=='3840x2160' and b['rtcdm_fifo_bl_completed']==25 and b['ubwc_static_ctrl']=='0x00001046'
PY
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camssvermagic
[ "$(modinfo -F vermagic "$NEW/imx681.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail sensorvermagic
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail armed
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module_$m"; done
[ "$(fdtget -l "$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail dt
[ -L /etc/systemd/system/multi-user.target.wants/pislave.service ] || fail pislave
echo 'PASS: 0063 assets/static authority/Golden safety clean; unarmed'
