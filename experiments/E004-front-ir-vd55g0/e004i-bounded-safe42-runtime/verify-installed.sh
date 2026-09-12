#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004i-bounded-safe42-runtime
BOOT=/boot/sp11-7.1.5-camera-e004i-config42
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004i_config42
ID=sp11-camera-e004i-config42-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(sudo -n sha256sum "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail kernel
[ "$(sudo -n sha256sum "$BOOT/initrd.img-7.1.5-sp11-camera-e004i-config42"|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail initrd
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-e004h-config42.dtb"|awk '{print $1}')" = 'e29c787acf9e2f1330a4e73fd8014aba118a2f0a59be51c86859a9ab7fed4ef2' ] || fail dtb
[ "$(sha256sum "$D/build/sp11-vd55g0-config42probe.ko"|awk '{print $1}')" = '75eccb1ac7a8a5f247ec03a9f56339527d2dcd7cfab77450b3ba1f8efe563c5c' ] || fail module
sudo -n test -x "$ENTRY" || fail entry
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
echo 'E004I_INSTALLED_VERIFY=PASS ARMED=NO'
