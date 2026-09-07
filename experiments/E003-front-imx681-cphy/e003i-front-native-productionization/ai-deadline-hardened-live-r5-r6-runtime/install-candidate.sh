#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ai-deadline-hardened-live-r5-r6-runtime
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
BOOT=/boot/sp11-7.1.5-camera-e003i-ai-live-iq
ENTRY=/etc/grub.d/99zd_sp11_camera_e003i_ai_live_iq
ID=sp11-camera-e003i-ai-live-iq-one-shot
"$D/prearm-check.sh"
[ ! -e "$BOOT" ] || { echo 'FAIL: boot dir exists' >&2; exit 1; }
sudo -n test ! -e "$ENTRY" || { echo 'FAIL: grub entry exists' >&2; exit 1; }
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV"; ! grep -q '^next_entry=.' <<<"$ENV"
sudo -n mkdir -p "$BOOT"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n cp /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e003i-ai-live-iq"
sudo -n cp "$B/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb" "$BOOT/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb"
sudo -n install -m 0755 "$D/99zd_sp11_camera_e003i_ai_live_iq" "$ENTRY"
sudo -n update-grub >/dev/null
sudo -n grep -Fq "menuentry 'SP11 Camera E003i-AI — bounded live trigger IQ producer'" /boot/grub/grub.cfg
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV"; ! grep -q '^next_entry=.' <<<"$ENV"
echo "PASS: installed $ID; remains unarmed"
