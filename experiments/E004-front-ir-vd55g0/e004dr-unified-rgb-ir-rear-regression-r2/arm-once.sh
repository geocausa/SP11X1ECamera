#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dr-unified-rgb-ir-rear-regression-r2
ID=sp11-camera-e004dr-unified-rgb-ir-rear-r2-one-shot
"$D/verify-installed.sh"; "$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
sudo -n grub-reboot "$ID"; ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx "next_entry=$ID"<<<"$ENV"
{ echo schema=sp11-camera-e004dr-arm-v1; echo status=ARMED_ONE_SHOT; echo time=$(date -Ins); echo head=$(git -C "$R" rev-parse HEAD); echo saved_entry=sp11-audio-fullio-v19c; echo next_entry=$ID; } > "$D/ARM.txt"
sync; echo "E004DR_ARMED=$ID REBOOT_REQUIRED=YES"
