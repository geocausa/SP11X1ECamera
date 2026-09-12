#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ic-unified-dtb-rear-regression-r16
ID=sp11-camera-ic-unified-rear-r16-one-shot
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
PYTHONDONTWRITEBYTECODE=1 "$D/verify-installed.py"
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
sudo -n grub-reboot "$ID"
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx "next_entry=$ID"<<<"$ENV"
{ echo 'schema=sp11-camera-ic-arm-v1'; echo 'status=ARMED_ONE_SHOT'; echo "time=$(date -Ins)"; echo "head=$(git -C "$R" rev-parse HEAD)"; echo "next_entry=$ID"; } > "$D/ARM.txt"
sync; echo "IC_ARMED=$ID REBOOT_REQUIRED=YES"
