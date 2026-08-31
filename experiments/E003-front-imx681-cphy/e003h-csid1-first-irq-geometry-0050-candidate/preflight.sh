#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-first-irq-geometry-0050-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static
STATIC_COMMIT=5613ea361e3361200921ccb063d2b0d8bfcda71f
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
git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail 'static 0050 checkpoint is not an ancestor'
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail 'not Golden kernel'
check /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a
check /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d
check "$CAMSS" b69a20b517953a96cf5ff806a26c78e52ce5e177ef8dcdf69afa0dd561e8439b
check "$SENSOR" 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388
check "$DTB" 019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f
check "$CAP" 6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20
check "$HELPER" d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09
check "$SETUP" 666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f
check "$WATCH" 8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84
check "$STATIC/0050-x1e-csid1-first-irq-geometry-readonly.patch" 61440f2452badd0d01f312af4ef4e08505c2263a3557af1693f1a5e04db7020b
check "$STATIC/linux-0050-csid1-first-irq-geometry-readonly-inspection.json" 6ccfd7e88586721dbc1b4050e041e8b128a8409d8ee2f1dd40fd0030f70a047d
check "$REPO/provenance/front-parity.json" 803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6
python3 - "$STATIC/linux-0050-csid1-first-irq-geometry-readonly-inspection.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
assert x['accepted'] is True
assert x['module_sha256']=='b69a20b517953a96cf5ff806a26c78e52ce5e177ef8dcdf69afa0dd561e8439b'
assert x['trace_max_entries']==8
assert x['new_mmio_read_callsites']==1 and x['new_mmio_writes']==0
assert x['irq_masks_changed'] is False and x['irq_clear_changed'] is False
assert x['crop_programming_changed'] is False and x['rup_aup_changed'] is False
assert x['sensor_changed'] is False and x['vfe_changed'] is False and x['rtcdm_changed'] is False
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
echo 'PASS: 0050 frozen inputs, ordered geometry telemetry proof, Golden rollback and front-only DT are clean'
