#!/bin/bash
set -euo pipefail
ROOT=/home/geoca/Documents/SP11-PROJECT
REPO=$ROOT/06-camera/SP11X1ECamera
EXP=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate
CAMSS=$ROOT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko
SENSOR=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-front-first-frame-runtime/imx681.ko
DTB=$EXP/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb
CAP=$EXP/firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin
HELPER=$EXP/e003h-pix-one-shot
check() { local got; got=$(sha256sum "$1" | cut -d' ' -f1); [ "$got" = "$2" ] || { echo "FAIL hash $1 $got" >&2; exit 1; }; }
[ "$(uname -r)" = 7.1.5-sp11-render-parity-v4+ ] || { echo 'FAIL kernel release'; exit 1; }
check /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a
check /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d
check "$CAMSS" 96e48ff176a048c391841d2c56bafdce76cfbe8a78b7310173caf175af49c9e9
check "$SENSOR" 389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388
check "$DTB" 083fd7d3a207cb329938c561aee84c8642cb02e52034b753b36aaff599a381ed
check "$CAP" 6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20
check "$HELPER" d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09
ENV=$(grub-editenv list)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || { echo 'FAIL saved_entry'; exit 1; }
if grep -q '^next_entry=.' <<<"$ENV"; then echo 'FAIL next_entry already armed' >&2; exit 1; fi
for m in qcom_camss imx681 ov13858; do [ ! -d "/sys/module/$m" ] || { echo "FAIL module already loaded: $m" >&2; exit 1; }; done
[ "$(fdtget -t s "$DTB" /soc@0/isp@acb7000/ports 2>/dev/null || true)" = '' ] || true
[ "$(fdtget -l "$DTB" /soc@0/isp@acb7000/ports | tr '\n' ' ' | xargs)" = 'port@2' ] || { echo 'FAIL front-only CAMSS ports'; exit 1; }
REG=$(fdtget -t x "$DTB" /soc@0/isp@acb7000 reg)
grep -q 'ac71000 0 f000' <<<"$REG" || { echo 'FAIL VFE1 span'; exit 1; }
grep -q 'ac26000 0 1000' <<<"$REG" || { echo 'FAIL RT-CDM1 resource'; exit 1; }
echo 'PASS: PIX one-shot package hashes, Golden rollback state, and front-only DT preflight clean'
