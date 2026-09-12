#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/hw-production-boot-bundle-activation-prep
HV=$BASE/hv-current-golden-camera-dtb-merge
BOOT=/boot/sp11-7.1.5-camera-e003i-hw-prod-activation
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e003i_hw_prod_activation
ID=sp11-camera-e003i-hw-prod-activation-one-shot
"$D/prearm-check.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e003i-hw-prod-activation"
sudo -n cp "$HV/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_e003i_hw_prod_activation" "$ENTRY"
sudo -n update-grub >/dev/null
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
{
 echo 'schema=sp11-e003i-hw-production-activation-install-v1'; echo 'status=INSTALLED_UNARMED'; echo "time=$(date -Ins)"; echo "head=$(git -C "$R" rev-parse HEAD)";
 sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-e003i-hw-prod-activation" "$BOOT/x1e80100-microsoft-denali-sp11-hv-current-golden-frontonly.dtb";
 sha256sum "$D/build/qcom-camss.ko" "$D/build/imx681.ko" "$D/package-root/PACKAGE-MANIFEST.sha256";
} > "$D/INSTALL.txt"
echo "HW_INSTALL=PASS ID=$ID ARMED=NO"
