#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-startup-csid-companion-rtcdm-0053-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static
STATIC_COMMIT=d977480aa80c4b5a115d263c15e5c79caa810e69
CAMSS=$NEW/qcom-camss.ko
SENSOR=$NEW/imx681.ko
DTB=$NEW/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
CAP=$NEW/firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin
HELPER=$NEW/e003h-pix-one-shot
SETUP=$NEW/setup-pix-media.sh
WATCH=$NEW/watch-rtcdm-stage.py
fail(){ echo "FAIL: $*" >&2; exit 1; }
check(){ local got; got=$(sha256sum "$1" | cut -d' ' -f1); [ "$got" = "$2" ] || fail "hash $1 $got"; }
[ ! -e "$NEW/AUTHORIZATION.json" ] || fail 'authorization exists at package-only gate'
python3 "$REPO/tools/check-front-parity-provenance.py" --repo "$REPO" --target bounded_first_pix
HEAD=$(git -C "$REPO" rev-parse HEAD)
[ "$HEAD" = "$(git -C "$REPO" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail 'repo/origin divergence'
git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail 'static 0053 checkpoint is not an ancestor'
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail 'not Golden kernel'
check /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a
check /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d
check "$CAMSS" f04189d766f478083e09fd38b26e73c99c03306ce1f2fb81d68b2ebd0d2be876
check "$SENSOR" 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388
check "$DTB" 019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f
check "$CAP" 6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20
check "$HELPER" d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09
check "$SETUP" 666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f
check "$WATCH" 8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84
check "$STATIC/0053-x1e-startup-csid-companion-rtcdm-transport.patch" dba1d21fdc01f4091af89ce051283464661952ce2d1acd1f59afb75c8b52cfd6
check "$STATIC/linux-0053-startup-csid-companion-rtcdm-transport-inspection.json" 72ceb0880f673bc1d17698eb228612a88b8bf4683b8f034a9de4f1b784120fea
check "$STATIC/csid1-startup-companion-transport-0053/startup-companion-transport-0053-oracle.json" 4b70a61a2e226b37d9310b4b4dee4d77c7516f975498973ee89dc29d772e2e5c
check "$STATIC/../e003h-csid1-clock-rate-0052-candidate/runtime-0052-analysis.json" 4367b9fe31552baf59cd7212743585fc990a07638794a81da178a22e1591ddba
check "$REPO/provenance/front-parity.json" 803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6
python3 - "$STATIC/linux-0053-startup-csid-companion-rtcdm-transport-inspection.json" "$STATIC/csid1-startup-companion-transport-0053/startup-companion-transport-0053-oracle.json" <<'PY'
import json,sys
li=json.load(open(sys.argv[1])); o=json.load(open(sys.argv[2]))
assert li['accepted'] is True and li['runtime_authorized'] is False
assert li['module_sha256']=='f04189d766f478083e09fd38b26e73c99c03306ce1f2fb81d68b2ebd0d2be876'
p=li['proved']
assert p['startup_packet_count']==4 and p['startup_rtcdm_commits_per_packet']==4
assert p['startup_rtcdm_order']==['CHANGE_BASE(VFE1)','IFE startup main','CHANGE_BASE(CSID1)','exact CSID descriptor-1 companion']
assert p['csid1_change_base']=='0x08057000'
assert p['packet0_companion_sha256']=='1872731eaa3eb2233436029c2658682097c61ebf97e3facf46e31224ee25e2a2'
assert p['packet1_3_companion_sha256']=='45d059ec64587ea4f55eb8df64704520782801418c4a754f512831c7473fb5c7'
assert p['cpu_startup_companion_calls_removed']==4
assert p['new_direct_mmio_reads']==0 and p['new_direct_mmio_writes']==0 and p['new_register_values']==0
for k in ('crop_coordinates_changed','rup_aup_changed','vfe_programming_changed','sensor_programming_changed','csiphy_programming_changed'):
    assert p[k] is False, k
assert li['classification']['crop_failure_causality_proven'] is False
assert o['accepted'] is True and o['classification']['transport_ownership_mismatch_proven'] is True
assert o['windows']['csid1_change_base']=='0x00057000'
assert o['classification']['crop_failure_causality_proven'] is False
PY
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'saved_entry is not Golden'
if grep -q '^next_entry=.' <<<"$ENV"; then fail 'next_entry already armed'; fi
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module already loaded: $m"; done
[ "$(fdtget -l "$DTB" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail 'front-only CAMSS ports drift'
REG=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 reg); grep -q 'ac71000 0 f000' <<<"$REG" || fail 'VFE1 span drift'; grep -q 'ac26000 0 1000' <<<"$REG" || fail 'RT-CDM1 resource drift'
IOMMUS=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 iommus); [ "$IOMMUS" = '3d 800 60 3d 820 60 3d 840 60 3d 860 60 3d 18a0 0' ] || fail "CAMSS IOMMU set drift: $IOMMUS"
echo 'PASS: 0053 frozen inputs, exact startup CSID RT-CDM transport proof, Golden rollback and front-only DT are clean'
