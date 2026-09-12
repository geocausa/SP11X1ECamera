#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004s-dynamic-ir-bind-runtime-r4
BOOT=/boot/sp11-7.1.5-camera-e004s-dynamic-ir-bind-r4
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004s_dynamic_ir_bind_r4
ID=sp11-camera-e004s-dynamic-ir-bind-r4-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(sudo -n sha256sum "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail kernel
[ "$(sudo -n sha256sum "$BOOT/initrd.img-7.1.5-sp11-camera-e004s-dynamic-ir-bind-r4"|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail initrd
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb"|awk '{print $1}')" = 'fffacde38934d1baa8392f6b5687827cf0490d7af9e20fd37858347c157f5742' ] || fail dtb
[ "$(sha256sum "$D/build/sp11-vd55g0.ko"|awk '{print $1}')" = '4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72' ] || fail sensor
[ "$(sha256sum "$D/build/e004s_stream_block_test.ko"|awk '{print $1}')" = 'f1cd5f44504251224253939f509c95c1ef86c603ba19002c0dce1f3314cfab57' ] || fail harness
sudo -n test -x "$ENTRY" || fail entry
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
echo 'E004S_INSTALLED_VERIFY=PASS ARMED=NO'
