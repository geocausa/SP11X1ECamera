#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004q-ir-only-bind-runtime-r2
O=$R/experiments/E004-front-ir-vd55g0/e004o-ir-only-graph-authority
BOOT=/boot/sp11-7.1.5-camera-e004q-ir-only-bind-r2
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004q_ir_only_bind_r2
"$D/prearm-check.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004q-ir-only-bind-r2"
sudo -n cp "$O/x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_e004q_ir_only_bind_r2" "$ENTRY"
sudo -n update-grub >/dev/null
"$D/verify-installed.sh"
{
 echo 'schema=sp11-camera-e004q-install-v1'; echo 'status=INSTALLED_UNARMED'; echo "time=$(date -Ins)"
 echo "head=$(git -C "$R" rev-parse HEAD)"
 sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-e004q-ir-only-bind-r2" "$BOOT/x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb"
 sha256sum "$D/build/sp11-vd55g0.ko" "$D/build/e004q_stream_block_test.ko"
} > "$D/INSTALL.txt"
echo 'E004Q_INSTALL=PASS ARMED=NO'
