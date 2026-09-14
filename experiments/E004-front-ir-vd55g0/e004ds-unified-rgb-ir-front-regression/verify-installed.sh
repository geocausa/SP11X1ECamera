#!/usr/bin/env bash
set -euo pipefail
D=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E004-front-ir-vd55g0/e004ds-unified-rgb-ir-front-regression
BOOT=/boot/sp11-7.1.5-camera-e004ds-unified-rgb-ir-front
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004ds_unified_rgb_ir_front
ID=sp11-camera-e004ds-unified-rgb-ir-front-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(sudo -n sha256sum "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"|awk '{print $1}')" = bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a ] || fail kernel
[ "$(sudo -n sha256sum "$BOOT/initrd.img-7.1.5-sp11-camera-e004ds-unified-rgb-ir-front"|awk '{print $1}')" = ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d ] || fail initrd
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-e004do-unified-rgb-ir.dtb"|awk '{print $1}')" = 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ] || fail dtb
(cd "$D/build" && sha256sum -c AUTHORITY.sha256 >/dev/null) || fail build
[ "$(sha256sum "$D/package-root/PACKAGE-MANIFEST.sha256"|awk '{print $1}')" = 60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a ] || fail package
(cd "$D/package-root" && sha256sum -c PACKAGE-MANIFEST.sha256 >/dev/null) || fail package_files
sudo -n test -x "$ENTRY" || fail entry; sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved; ! grep -q '^next_entry=.'<<<"$ENV" || fail next
echo E004DS_INSTALLED_VERIFY=PASS ARMED=NO
