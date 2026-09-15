#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004en-natural-cap-release-one-shot-runtime
BOOT=/boot/sp11-7.1.5-camera-e004en-natural-cap-release-one-shot-runtime
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004en_natural_cap_release
"$D/prearm-live.sh"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004en-natural-cap-release-one-shot-runtime"
sudo -n cp /usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb "$BOOT/"
sudo -n install -m 0755 "$D/99zzzzzz_sp11_camera_e004en_natural_cap_release" "$ENTRY"
sudo -n update-grub >/dev/null
"$D/verify-installed.sh"
{ echo schema=sp11-camera-e004en-install-v1; echo status=INSTALLED_UNARMED; echo time=$(date -Ins); echo head=$(git -C "$R" rev-parse HEAD); sudo -n sha256sum "$ENTRY" "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+" "$BOOT/initrd.img-7.1.5-sp11-camera-e004en-natural-cap-release-one-shot-runtime" "$BOOT/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"; echo package_manifest_sha256=$(sha256sum /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256|awk '{print $1}'); } > "$D/INSTALL.txt"
echo E004EN_INSTALL=PASS ARMED=NO
