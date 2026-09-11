#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/go-twentyseven-frame-live-r5-r27
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
BOOT=/boot/sp11-7.1.5-camera-e003i-go-twentyseven-frame-r5-r27
ENTRY=/etc/grub.d/99zy_sp11_camera_e003i_go_twentyseven_frame_r5_r27
ID=sp11-camera-e003i-go-twentyseven-frame-r5-r27-one-shot

"$D/prearm-check.sh"
[ ! -e "$BOOT" ] || { echo 'FAIL: GO boot dir exists' >&2; exit 1; }
sudo -n test ! -e "$ENTRY" || { echo 'FAIL: GO grub entry exists' >&2; exit 1; }

ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV"
! grep -q '^next_entry=.' <<<"$ENV"

sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e003i-go-twentyseven-frame-r5-r27"
sudo -n cp "$B/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb"
sudo -n install -m 0755 "$D/99zy_sp11_camera_e003i_go_twentyseven_frame_r5_r27" "$ENTRY"
sudo -n update-grub >/dev/null
sudo -n grep -Fq "menuentry 'SP11 Camera E003i-GO — bounded twenty-seven-frame R5-R27 one-shot'" /boot/grub/grub.cfg

ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV"
! grep -q '^next_entry=.' <<<"$ENV"

{
 echo 'schema=sp11-e003i-go-install-v1'
 echo 'status=INSTALLED_UNARMED'
 echo "time=$(date -Ins)"
 echo "head=$(git -C "$R" rev-parse HEAD)"
 sha256sum "$ENTRY" "$BOOT"/* "$D/build/qcom-camss-go.ko"
} > "$D/INSTALL.txt"
echo "PASS: installed $ID; remains unarmed"
