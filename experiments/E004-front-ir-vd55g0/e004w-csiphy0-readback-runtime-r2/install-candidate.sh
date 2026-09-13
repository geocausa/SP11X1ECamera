#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004w-csiphy0-readback-runtime-r2
V=$R/experiments/E004-front-ir-vd55g0/e004v-csiphy0-aperture-authority
BOOT=/boot/sp11-7.1.5-camera-e004w-csiphy0-readback-r2
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004w_csiphy0_readback_r2
"$D/prearm-check.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004w-csiphy0-readback-r2"
sudo -n cp "$V/x1e80100-microsoft-denali-sp11-e004v-ir-csiphy0-8k.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e004v-ir-csiphy0-8k.dtb"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_e004w_csiphy0_readback_r2" "$ENTRY"
sudo -n update-grub >/dev/null
"$D/verify-installed.sh"
{
 echo 'schema=sp11-camera-e004w-install-v1'; echo 'status=INSTALLED_UNARMED'; echo "time=$(date -Ins)"
 echo "head=$(git -C "$R" rev-parse HEAD)"
 sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-e004w-csiphy0-readback-r2" "$BOOT/x1e80100-microsoft-denali-sp11-e004v-ir-csiphy0-8k.dtb"
 sha256sum "$D/build/sp11-vd55g0.ko" "$D/build/e004t_csiphy_readback_test.ko"
} > "$D/INSTALL.txt"
echo 'E004W_INSTALL=PASS ARMED=NO'
