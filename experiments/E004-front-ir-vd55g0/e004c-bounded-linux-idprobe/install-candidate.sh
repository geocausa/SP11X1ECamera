#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E004-front-ir-vd55g0/e004b-linux-probe-authority
D=$R/experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe
BOOT=/boot/sp11-7.1.5-camera-e004c-ir-idprobe
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004c_ir_idprobe
ID=sp11-camera-e004c-ir-idprobe-one-shot
"$D/prearm-check.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004c-ir-idprobe"
sudo -n cp "$B/x1e80100-microsoft-denali-sp11-e004b-ir-probe.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e004b-ir-probe.dtb"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_e004c_ir_idprobe" "$ENTRY"
sudo -n update-grub >/dev/null
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
"$D/verify-installed.sh"
{
 echo 'schema=sp11-camera-e004c-install-v1'
 echo 'status=INSTALLED_UNARMED'
 echo "time=$(date -Ins)"
 echo "head=$(git -C "$R" rev-parse HEAD)"
 sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-e004c-ir-idprobe" "$BOOT/x1e80100-microsoft-denali-sp11-e004b-ir-probe.dtb"
 sha256sum "$D/build/sp11-vd55g0-idprobe.ko"
} > "$D/INSTALL.txt"
echo "E004C_INSTALL=PASS ID=$ID ARMED=NO"
