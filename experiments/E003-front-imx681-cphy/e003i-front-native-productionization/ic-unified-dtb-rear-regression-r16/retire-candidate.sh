#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ic-unified-dtb-rear-regression-r16
BOOT=/boot/sp11-7.1.5-camera-ic-unified-rear-r16; ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_ic_unified_rear_r16; ID=sp11-camera-ic-unified-rear-r16-one-shot
"$D/golden-return-check.sh"
sudo -n rm -f "$ENTRY"; sudo -n rm -rf "$BOOT"; sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
{ echo 'schema=sp11-camera-ic-retire-v1'; echo 'status=PASS_CANDIDATE_RETIRED'; echo "time=$(date -Ins)"; echo "candidate_id=$ID"; } > "$D/RETIRE.txt"
echo 'IC_RETIRE=PASS'
