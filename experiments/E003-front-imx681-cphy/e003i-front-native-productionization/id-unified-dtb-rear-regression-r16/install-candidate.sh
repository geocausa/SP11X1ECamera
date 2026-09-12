#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/id-unified-dtb-rear-regression-r16
IB=$BASE/ib-unified-current-golden-rear-front-dtb
BOOT=/boot/sp11-7.1.5-camera-id-unified-rear-r16
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_id_unified_rear_r16
ID=sp11-camera-id-unified-rear-r16-one-shot
"$D/prearm-check.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-id-unified-rear-r16"
sudo -n cp "$IB/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_id_unified_rear_r16" "$ENTRY"
sudo -n update-grub >/dev/null
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
{
 echo 'schema=sp11-camera-id-install-v1'; echo 'status=INSTALLED_UNARMED'; echo "time=$(date -Ins)"; echo "head=$(git -C "$R" rev-parse HEAD)";
 sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-id-unified-rear-r16" "$BOOT/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb";
 sha256sum "$D/build/qcom-camss.ko" "$D/build/imx681.ko" "$D/build/ov13858-production.ko" "$D/package-root/PACKAGE-MANIFEST.sha256";
} > "$D/INSTALL.txt"
echo "ID_INSTALL=PASS ID=$ID ARMED=NO"
