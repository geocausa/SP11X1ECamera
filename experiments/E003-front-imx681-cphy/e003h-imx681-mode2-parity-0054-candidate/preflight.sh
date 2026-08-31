#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-static
CAP=$REPO/experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-imx681-mode-selection-capture-20260831/windows-imx681-mode-selection-oracle.json
STATIC_COMMIT=c690f67548dcce57ba6f017d98be836233a575e7
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail 'authorization exists at package-only gate'
[ ! -e "$NEW/RUNTIME-MODE2-0054-RUN.txt" ] || fail '0054 RUN already exists'
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail 'bounded provenance not green'
HEAD=$(git -C "$REPO" rev-parse HEAD)
[ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail 'static 0054 checkpoint is not an ancestor'
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail 'not Golden kernel'
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0054-static-inspection.json" "$CAP" <<'PY'
import hashlib,json,sys
m_path,new,si_path,cap_path=sys.argv[1:]
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
m=json.load(open(m_path)); assert m['accepted'] is True and m['runtime_authorized'] is False
assert m['static_commit']=='c690f67548dcce57ba6f017d98be836233a575e7'
for rel,h in m['assets'].items(): assert sha(new+'/'+rel)==h,(rel,sha(new+'/'+rel),h)
si=json.load(open(si_path)); assert sha(si_path)==m['static_proof']['0054_inspection']; assert si['accepted'] is True and si['runtime_authorized'] is False and si['hardware_execution_performed'] is False
assert si['selected_resolution_index']==2 and si['sensor']['mode_pairs']==68 and si['sensor']['windows_pair_equality'] is True and si['sensor']['changed_values']==7
assert si['camss']['geometry_gate_changes']==3 and si['camss']['new_mmio_writes']==0 and si['camss']['hardware_programming_values_changed'] is False
assert si['sensor']['module_sha256']==m['assets']['imx681.ko']; assert si['camss']['module_sha256']==m['assets']['qcom-camss.ko']
cap=json.load(open(cap_path)); assert sha(cap_path)==m['static_proof']['windows_mode_selection_oracle']; assert cap['accepted'] is True and cap['full_firmware_match']['matching_resolution_indices']==[2]
b=m['behavior_delta']; assert b['sensor_resolution_index_old']==0 and b['sensor_resolution_index_new']==2 and b['sensor_geometry_new']=='3840x2160' and b['sensor_changed_register_values']==7 and b['sensor_mode_pairs']==68 and b['windows_pair_equality'] is True
assert b['camss_geometry_gate_changes']==3 and b['new_camss_mmio_writes']==0 and b['csid_programming_values_changed'] is False and b['startup_csid_rtcdm_transport_preserved_from_0053'] is True
PY
[ "$(sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ | cut -d' ' -f1)" = bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a ] || fail 'Golden kernel hash'
[ "$(sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c | cut -d' ' -f1)" = ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d ] || fail 'Golden initrd hash'
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail 'CAMSS vermagic'
[ "$(modinfo -F vermagic "$NEW/imx681.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail 'sensor vermagic'
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'saved_entry is not Golden'
if grep -q '^next_entry=.' <<<"$ENV"; then fail 'next_entry already armed'; fi
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module already loaded: $m"; done
DTB=$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
[ "$(fdtget -l "$DTB" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail 'front-only CAMSS ports drift'
IOMMUS=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 iommus); [ "$IOMMUS" = '3d 800 60 3d 820 60 3d 840 60 3d 860 60 3d 18a0 0' ] || fail "CAMSS IOMMU set drift: $IOMMUS"
grep -q '3840x2160' "$NEW/setup-pix-media.sh" || fail 'media setup lacks mode2 geometry'
! grep -q '3840x2640' "$NEW/setup-pix-media.sh" || fail 'media setup retains mode0 geometry'
echo 'PASS: 0054 frozen mode2 package inputs, Golden rollback and front-only DT are clean'
