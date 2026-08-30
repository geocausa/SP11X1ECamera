#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-vfe1-timeout-readonly-0046-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static
STATIC_COMMIT=8fd83d98847b46426c116bec172ee0d296080c42
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
git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail 'static 0046 checkpoint is not an ancestor'
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail 'not Golden kernel'
check /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a
check /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d
check "$CAMSS" f1b5ce5dc973a140b29257927c02b2749f96f379fc01b78a10841443a15ab4be
check "$SENSOR" 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388
check "$DTB" 019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f
check "$CAP" 6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20
check "$HELPER" d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09
check "$SETUP" 666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f
check "$WATCH" 8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84
check "$STATIC/0046-x1e-vfe1-timeout-readonly-telemetry.patch" 6ce9d732d73e6a09d73b756b1726b6f0e13702bede1d9ba0b61f9a5805d3b709
check "$STATIC/linux-0046-vfe1-timeout-readonly-inspection.json" 2e9e0460e72567db162eaeac382fa7912656a85c2441ad582351e267f00edeca
check "$STATIC/vfe1-timeout-readonly-telemetry-oracle.json" 403f762c4d161823ca10deec27df733a50ca7d9d0d4aec4fb2cac05863ca6705
check "$REPO/provenance/front-parity.json" 803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6
python3 - "$STATIC/linux-0046-vfe1-timeout-readonly-inspection.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
assert x['accepted'] is True
assert x['module_sha256']=='f1b5ce5dc973a140b29257927c02b2749f96f379fc01b78a10841443a15ab4be'
assert x['telemetry_read_count']==30
assert x['mmio_writes_added']==0 and x['polling_primitives_added']==0
assert x['start_stop_irq_clear_buffer_programming_changed'] is False
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
echo 'PASS: 0046 frozen inputs, read-only telemetry proof, Golden rollback and front-only DT are clean'
