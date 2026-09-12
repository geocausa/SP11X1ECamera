#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe
BOOT=/boot/sp11-7.1.5-camera-e004c-ir-idprobe
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004c_ir_idprobe
ID=sp11-camera-e004c-ir-idprobe-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(sudo -n sha256sum "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail kernel
[ "$(sudo -n sha256sum "$BOOT/initrd.img-7.1.5-sp11-camera-e004c-ir-idprobe"|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail initrd
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-e004b-ir-probe.dtb"|awk '{print $1}')" = '2b9ff2265606aa95006e3c952597c496367106e00aa1e2d1ec1e75b8f9e485e6' ] || fail dtb
[ "$(sha256sum "$D/build/sp11-vd55g0-idprobe.ko"|awk '{print $1}')" = 'd749fb549ff7c03e0ebcd1690b78b795d985d6d37083ab938a2a2663c397daed' ] || fail module
sudo -n test -x "$ENTRY" || fail entry
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
echo 'E004C_INSTALLED_VERIFY=PASS ARMED=NO'
