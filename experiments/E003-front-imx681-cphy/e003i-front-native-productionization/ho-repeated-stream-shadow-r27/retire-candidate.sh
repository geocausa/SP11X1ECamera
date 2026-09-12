#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ho-repeated-stream-shadow-r27
BOOT=/boot/sp11-7.1.5-camera-e003i-ho-repeat-shadow-r27
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e003i_ho_repeat_shadow_r27
ID=sp11-camera-e003i-ho-repeat-shadow-r27-one-shot
"$D/golden-return-check.sh"
sudo -n rm -f "$ENTRY"
sudo -n rm -rf "$BOOT"
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
{ echo 'schema=sp11-e003i-ho-repeat-shadow-retire-v1'; echo 'status=PASS_CANDIDATE_RETIRED'; echo "time=$(date -Ins)"; echo "head=$(git -C "$R" rev-parse HEAD)"; echo "candidate_id=$ID"; } > "$D/RETIRE.txt"
echo 'HO_RETIRE=PASS'
