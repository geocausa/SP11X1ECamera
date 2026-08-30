#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-ipp-irq-history-0048-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static
STATIC_COMMIT=cbf40db7557e4a52e220494f633bc933abf3a079
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
git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail 'static 0048 checkpoint is not an ancestor'
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail 'not Golden kernel'
check /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a
check /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d
check "$CAMSS" 94cc14d9702492bffa2b4e72989db45356cf59ffcce7f4c382be13e7130030b7
check "$SENSOR" 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388
check "$DTB" 019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f
check "$CAP" 6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20
check "$HELPER" d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09
check "$SETUP" 666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f
check "$WATCH" 8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84
check "$STATIC/0048-x1e-csid1-ipp-irq-history-readonly.patch" 91d292888e563c2d4e0ffc65664cfa4b0a3225cb1f56af9053652998ff0be1d7
check "$STATIC/linux-0048-csid1-ipp-irq-history-inspection.json" 6e98360aa0a83c8c61db1e67bd5c12f4fb6c7856698f48aea404a23100de8eb2
check "$STATIC/windows-linux-irq-observer-integrity/irq-observer-integrity-oracle.json" 23bc970a9bacff901e1336208282904cb9c0add0dfd5bea311194caeacb5451d
check "$REPO/provenance/front-parity.json" 803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6
python3 - "$STATIC/linux-0048-csid1-ipp-irq-history-inspection.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
assert x['accepted'] is True
assert x['module_sha256']=='94cc14d9702492bffa2b4e72989db45356cf59ffcce7f4c382be13e7130030b7'
assert x['new_mmio_reads']==0 and x['new_mmio_writes']==0
assert x['hardware_behavior_changed'] is False
assert x['runtime_authorized'] is False
PY
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'saved_entry is not Golden'
if grep -q '^next_entry=.' <<<"$ENV"; then fail 'next_entry already armed'; fi
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module already loaded: $m"; done
[ "$(fdtget -l "$DTB" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || fail 'front-only CAMSS ports drift'
REG=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 reg)
grep -q 'ac71000 0 f000' <<<"$REG" || fail 'VFE1 span drift'
grep -q 'ac26000 0 1000' <<<"$REG" || fail 'RT-CDM1 resource drift'
IOMMUS=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 iommus)
[ "$IOMMUS" = '3d 800 60 3d 820 60 3d 840 60 3d 860 60 3d 18a0 0' ] || fail "CAMSS IOMMU set drift: $IOMMUS"
echo 'PASS: 0048 frozen inputs, observer-integrity proof, Golden rollback and front-only DT are clean'
