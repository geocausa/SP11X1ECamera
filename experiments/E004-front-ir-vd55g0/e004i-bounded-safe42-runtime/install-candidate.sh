#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
E=$R/experiments/E004-front-ir-vd55g0/e004h-safe42-config-authority
D=$R/experiments/E004-front-ir-vd55g0/e004i-bounded-safe42-runtime
BOOT=/boot/sp11-7.1.5-camera-e004i-config42
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004i_config42
ID=sp11-camera-e004i-config42-one-shot
"$D/prearm-check.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004i-config42"
sudo -n cp "$E/x1e80100-microsoft-denali-sp11-e004h-config42.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e004h-config42.dtb"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_e004i_config42" "$ENTRY"
sudo -n update-grub >/dev/null
"$D/verify-installed.sh"
{
 echo 'schema=sp11-camera-e004i-install-v1'; echo 'status=INSTALLED_UNARMED'; echo "time=$(date -Ins)"
 echo "head=$(git -C "$R" rev-parse HEAD)"
 sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-e004i-config42" "$BOOT/x1e80100-microsoft-denali-sp11-e004h-config42.dtb"
 sha256sum "$D/build/sp11-vd55g0-config42probe.ko"
} > "$D/INSTALL.txt"
echo "E004I_INSTALL=PASS ID=$ID ARMED=NO"
