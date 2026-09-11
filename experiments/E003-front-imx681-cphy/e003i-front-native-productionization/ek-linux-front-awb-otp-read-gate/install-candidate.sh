#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ek-linux-front-awb-otp-read-gate
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
BOOT=/boot/sp11-7.1.5-camera-e003i-ek-awb-otp
ENTRY=/etc/grub.d/99zj_sp11_camera_e003i_ek_awb_otp
ID=sp11-camera-e003i-ek-awb-otp-one-shot
"$D/prearm-check.sh"
[ ! -e "$BOOT" ] || { echo 'FAIL: EK boot dir exists' >&2; exit 1; }
sudo -n test ! -e "$ENTRY" || { echo 'FAIL: EK grub entry exists' >&2; exit 1; }
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e003i-ek-awb-otp"
sudo -n cp "$B/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb"
sudo -n install -m 0755 "$D/99zj_sp11_camera_e003i_ek_awb_otp" "$ENTRY"
sudo -n update-grub >/dev/null
sudo -n grep -Fq "menuentry 'SP11 Camera E003i-EK — Linux AWB OTP read one-shot'" /boot/grub/grub.cfg
{
 echo 'schema=sp11-e003i-ek-install-v1'; echo 'status=INSTALLED_UNARMED'; echo "time=$(date -Ins)"; echo "head=$(git -C "$R" rev-parse HEAD)";
 sha256sum "$D/imx681.ko" "$ENTRY" "$BOOT"/*;
} > "$D/INSTALL.txt"
echo "PASS: installed $ID; remains unarmed"
