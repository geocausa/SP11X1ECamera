#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ev-nine-frame-live-r5-r9-gainfeed
ID=sp11-camera-e003i-ev-nine-frame-r5-r9-one-shot
"$D/prearm-check.sh"
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true);grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV";! grep -q '^next_entry=.'<<<"$ENV";sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n grub-reboot "$ID"
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true);grep -qx "next_entry=$ID"<<<"$ENV"
{ echo 'schema=sp11-e003i-ev-arm-v1';echo 'status=ARMED_ONE_SHOT';echo "time=$(date -Ins)";echo "head=$(git -C "$R" rev-parse HEAD)";echo 'saved_entry=sp11-audio-fullio-v19c';echo "next_entry=$ID"; } > "$D/ARM.txt"
sync;echo "ARMED: $ID; reboot required"
