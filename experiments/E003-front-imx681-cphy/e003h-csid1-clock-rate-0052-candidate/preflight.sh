#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-clock-rate-0052-candidate
STATIC=$REPO/experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static
STATIC_COMMIT=23ea4ce8b6ddc2bc76e15f2121087eeef34b8484
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
git -C "$REPO" merge-base --is-ancestor "$STATIC_COMMIT" "$HEAD" || fail 'static 0052 checkpoint is not an ancestor'
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || fail 'not Golden kernel'
check /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a
check /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d
check "$CAMSS" 42662121c848d863b06e3aba737e0f80a35fc047faf8cf5b0f47e2554ba3e92a
check "$SENSOR" 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388
check "$DTB" 019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f
check "$CAP" 6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20
check "$HELPER" d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09
check "$SETUP" 666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f
check "$WATCH" 8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84
check "$STATIC/0052-x1e-front-csid-link-clock-rate.patch" 55c27634af4837e615145a7df9f4e92119b75c7a5b53957fa5864ddd16266788
check "$STATIC/linux-0052-x1e-front-link-clock-rate-inspection.json" e20bf446fde42298988c586b941e4c96ec8017f8c67bc4a396b824f359f676ad
check "$STATIC/x1e-csid-clock-hbi-correlation/x1e-csid-clock-hbi-correlation-oracle.json" f913e0dd3766077cfa9cf6875f77d7494bfe60a1bceea0ffe9f9c928d7d00dd0
check "$STATIC/windows-linux-first-eof-geometry-boundary/first-eof-geometry-boundary-oracle.json" db4476e159872f9005a127d84ea41032191402de2709a0835d2c2c5fbc9dffde
check "$STATIC/../e003h-csid1-rupdone-no-regupdate-0051-candidate/runtime-0051-analysis.json" 2e1fbd740073b98e9e86ef477f1986d9b7e94a26a5e486f4386197b8e331f9d1
check "$REPO/provenance/front-parity.json" 803d09be7a18b321b07db7dac5a81d837dd09b1f6dfd883b2f27daefa7e8ffb6
python3 - "$STATIC/linux-0052-x1e-front-link-clock-rate-inspection.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1])); assert x['accepted'] is True
assert x['module_sha256']=='42662121c848d863b06e3aba737e0f80a35fc047faf8cf5b0f47e2554ba3e92a'
assert x['old_requested_rate_hz']==300000000 and x['new_link_derived_rate_hz']==400000000
assert x['scope']=={'soc':'X1E80100','csid':1,'csiphy':2,'phy':'C-PHY','trios':1,'clock_names':['csid','csid_csiphy_rx']}
assert x['new_mmio_reads']==0 and x['new_mmio_writes']==0 and x['new_register_values']==0
assert x['clock_tables_changed'] is False and x['clock_margin_changed'] is False
for k in ('crop_changed','rup_aup_changed','irq_changed','rtcdm_changed','vfe_changed','csiphy_programming_changed','sensor_changed','dt_changed'):
    assert x[k] is False, k
assert x['direct_windows_400mhz_vote_proven'] is False and x['hbi_400_300_correlation_proven'] is True
assert x['runtime_authorized'] is False
PY
ENV=$(grub-editenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail 'saved_entry is not Golden'
if grep -q '^next_entry=.' <<<"$ENV"; then fail 'next_entry already armed'; fi
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || fail "module already loaded: $m"; done
[ "$(fdtget -l "$DTB" /soc@0/isp@acb7000/ports | tr '
' ' ' | xargs)" = 'port@2' ] || fail 'front-only CAMSS ports drift'
REG=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 reg); grep -q 'ac71000 0 f000' <<<"$REG" || fail 'VFE1 span drift'; grep -q 'ac26000 0 1000' <<<"$REG" || fail 'RT-CDM1 resource drift'
IOMMUS=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 iommus); [ "$IOMMUS" = '3d 800 60 3d 820 60 3d 840 60 3d 860 60 3d 18a0 0' ] || fail "CAMSS IOMMU set drift: $IOMMUS"
echo 'PASS: 0052 frozen inputs, X1E CSID clock/HBI proof, Golden rollback and front-only DT are clean'
