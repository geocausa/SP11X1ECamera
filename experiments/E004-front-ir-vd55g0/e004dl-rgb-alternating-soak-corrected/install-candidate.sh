#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dl-rgb-alternating-soak-corrected
IB=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ib-unified-current-golden-rear-front-dtb
BOOT=/boot/sp11-7.1.5-camera-e004dl-rgb-alternating-soak-corrected
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004dl_rgb_alternating_soak_corrected
ID=sp11-camera-e004dl-rgb-alternating-soak-corrected-one-shot
"$D/prearm-check.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004dl-rgb-alternating-soak-corrected"
sudo -n cp "$IB/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb" "$BOOT/"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_e004dl_rgb_alternating_soak_corrected" "$ENTRY"
sudo -n update-grub >/dev/null
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
{
 echo schema=sp11-camera-e004dl-install-v1; echo status=INSTALLED_UNARMED; echo time=$(date -Ins); echo head=$(git -C "$R" rev-parse HEAD)
 sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-e004dl-rgb-alternating-soak-corrected" "$BOOT/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb"
 sha256sum "$D/build/qcom-camss.ko" "$D/build/imx681.ko" "$D/build/ov13858-production.ko" "$D/package-root/PACKAGE-MANIFEST.sha256"
} > "$D/INSTALL.txt"
echo "E004DL_INSTALL=PASS ID=$ID ARMED=NO"
