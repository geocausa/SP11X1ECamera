#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004m-native-bind-runtime
BOOT=/boot/sp11-7.1.5-camera-e004m-native-bind
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004m_native_bind
ID=sp11-camera-e004m-native-bind-one-shot
fail(){ echo "FAIL: $*" >&2; exit 1; }
[ "$(sudo -n sha256sum "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"|awk '{print $1}')" = 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a' ] || fail kernel
[ "$(sudo -n sha256sum "$BOOT/initrd.img-7.1.5-sp11-camera-e004m-native-bind"|awk '{print $1}')" = 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d' ] || fail initrd
[ "$(sudo -n sha256sum "$BOOT/x1e80100-microsoft-denali-sp11-e004l-native-bind.dtb"|awk '{print $1}')" = 'dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b' ] || fail dtb
[ "$(sha256sum "$D/build/sp11-vd55g0.ko"|awk '{print $1}')" = '4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72' ] || fail sensor
[ "$(sha256sum "$D/build/e004m_stream_block_test.ko"|awk '{print $1}')" = '93f947e9737c1472cf11df15b62223d07cae8adb330ebb359d27952172e5a926' ] || fail harness
sudo -n test -x "$ENTRY" || fail entry
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg || fail grub
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV" || fail saved
! grep -q '^next_entry=.'<<<"$ENV" || fail next
echo 'E004M_INSTALLED_VERIFY=PASS ARMED=NO'
