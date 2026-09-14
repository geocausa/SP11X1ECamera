#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004ds-unified-rgb-ir-front-regression
DO=$R/experiments/E004-front-ir-vd55g0/e004do-unified-rgb-ir-offline-authority
BOOT=/boot/sp11-7.1.5-camera-e004ds-unified-rgb-ir-front
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004ds_unified_rgb_ir_front
"$D/prearm-check.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004ds-unified-rgb-ir-front"
sudo -n cp "$DO/x1e80100-microsoft-denali-sp11-e004do-unified-rgb-ir.dtb" "$BOOT/"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_e004ds_unified_rgb_ir_front" "$ENTRY"
sudo -n update-grub >/dev/null
"$D/verify-installed.sh"
{ echo schema=sp11-camera-e004ds-install-v1; echo status=INSTALLED_UNARMED; echo time=$(date -Ins); echo head=$(git -C "$R" rev-parse HEAD); sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-e004ds-unified-rgb-ir-front" "$BOOT/x1e80100-microsoft-denali-sp11-e004do-unified-rgb-ir.dtb"; cat "$D/build/AUTHORITY.sha256"; echo front_package_manifest_sha256=$(sha256sum "$D/package-root/PACKAGE-MANIFEST.sha256"|awk '{print $1}'); } > "$D/INSTALL.txt"
echo E004DS_INSTALL=PASS ARMED=NO
