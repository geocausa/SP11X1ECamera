#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-static
BASELINE=$REPO/experiments/E003-front-imx681-cphy/e003h-camnoc-rate-parity-0056-candidate/runtime-0056-analysis.json
STATIC_COMMIT=139aeb16e4296041234ae97da91cfef105ee7d46
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail 'authorization exists at package-only gate'
[ ! -e "$NEW/RUNTIME-VFEACTIVE-0057-RUN.txt" ] || fail '0057 RUN already exists'
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix >/dev/null || fail 'bounded provenance not green'
HEAD=$(git -C "$REPO" rev-parse HEAD)
[ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" diff --quiet || fail 'tracked worktree dirty'
git -C "$REPO" diff --cached --quiet || fail 'staged worktree dirty'
git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail '0057 static checkpoint is not an ancestor'
grep -q 'sp11_entry=7.1.5-sp11-fullio-v19c' /proc/cmdline || fail 'not Golden boot'
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail 'not Golden kernel'
python3 - "$NEW/asset-manifest.json" "$NEW" "$STATIC/0057-static-inspection.json" "$BASELINE" <<'PY'
import hashlib,json,sys,pathlib
mp,new,sp,bp=sys.argv[1:]; new=pathlib.Path(new); sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(); m=json.load(open(mp))
assert m['accepted'] and m['runtime_authorized'] is False and m['static_commit']=='139aeb16e4296041234ae97da91cfef105ee7d46'
for r,h in m['assets'].items(): assert sha(new/r)==h,(r,sha(new/r),h)
si=json.load(open(sp)); assert sha(sp)==m['static_inspection_sha256'] and si['accepted'] and si['runtime_authorized'] is False
assert si['module_sha256']==m['assets']['qcom-camss.ko'] and si['new_direct_mmio_write_calls']==2 and si['new_direct_mmio_reads']==0
assert si['new_write_offsets']==['0x28','0xc08'] and si['steady_state_windows_bus_mask0_retained']=='0xd0000000'
base=json.load(open(bp)); assert sha(bp)==m['consumed_0056_analysis_sha256'] and base['accepted'] and base['classification']['retain_300mhz_correction'] is True
b=m['behavior_delta']; assert b['new_direct_mmio_write_calls']==2 and b['new_direct_mmio_reads']==0 and b['sensor_changes']==0 and b['csid_changes']==0 and b['rtcdm_changes']==0 and b['csiphy_changes']==0 and b['dt_changes']==0 and b['runner_changes']==0
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
echo 'PASS: 0057 frozen assets/static proof, Golden rollback and front-only DT clean; package unarmed'
