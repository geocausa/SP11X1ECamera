#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-lowtop-readonly-0059-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-lowtop-readonly-0059-static
BASE=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate/runtime-0058-analysis.json
STATIC_COMMIT=9d93a5e1362e2bce9f0a85b7f0977e1821c2f9b0
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail 'authorization exists at package gate'
[ ! -e "$NEW/RUNTIME-VFELOWTOP-0059-RUN.txt" ] || fail '0059 RUN already exists'
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail provenance
HEAD=$(git -C "$REPO" rev-parse HEAD); [ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail git
git -C "$REPO" diff --quiet || fail dirty; git -C "$REPO" diff --cached --quiet || fail staged
git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail static
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail kernel
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail Golden
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0059-static-inspection.json" "$BASE" <<'PY'
import hashlib,json,sys,pathlib
mp,new,sp,bp=sys.argv[1:]; new=pathlib.Path(new); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp)); si=json.load(open(sp)); b=json.load(open(bp))
assert m['accepted'] and m['runtime_authorized'] is False and m['static_commit']=='9d93a5e1362e2bce9f0a85b7f0977e1821c2f9b0'
for r,h in m['assets'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
assert sha(sp)==m['static_inspection_sha256'] and si['accepted'] and si['runtime_authorized'] is False
assert si['module_sha256']==m['assets']['qcom-camss.ko'] and si['new_direct_mmio_reads']==13 and si['new_mmio_writes']==0 and si['camera_programming_changed'] is False
assert sha(bp)==m['consumed_0058_analysis_sha256'] and b['accepted'] and b['authorization_consumed'] and b['classification']['new_programming_write_justified'] is False
bd=m['behavior_delta']; assert bd['new_direct_mmio_reads']==13 and bd['new_mmio_writes']==0 and bd['camera_programming_changed'] is False
PY
[ "$(sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ | cut -d' ' -f1)" = bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a ] || fail kernelhash
[ "$(sha256sum /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c | cut -d' ' -f1)" = ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d ] || fail initrdhash
[ "$(modinfo -F vermagic "$NEW/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail camssvermagic
[ "$(modinfo -F vermagic "$NEW/imx681.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ] || fail sensorvermagic
ENV=$(grub-editenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail armed
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module $m loaded"; done
DTB=$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
[ "$(fdtget -l "$DTB" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail dt
[ "$(fdtget -t x "$DTB" /soc@0/isp@acb7000 iommus)" = '3d 800 60 3d 820 60 3d 840 60 3d 860 60 3d 18a0 0' ] || fail iommu
grep -q '3840x2160' "$NEW/setup-pix-media.sh" || fail geometry; ! grep -q '3840x2640' "$NEW/setup-pix-media.sh" || fail oldgeometry
echo 'PASS: 0059 read-only low-TOP telemetry package assets and Golden safety clean; unarmed'
