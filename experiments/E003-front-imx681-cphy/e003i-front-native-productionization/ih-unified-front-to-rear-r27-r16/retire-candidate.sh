#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ih-unified-front-to-rear-r27-r16
BOOT=/boot/sp11-7.1.5-camera-ih-front-to-rear-r27-r16
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_ih_front_to_rear_r27_r16
ID=sp11-camera-ih-front-to-rear-r27-r16-one-shot
"$D/golden-return-check.sh"
sudo -n rm -f "$ENTRY";sudo -n rm -rf "$BOOT";sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true);grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV";! grep -q '^next_entry=.'<<<"$ENV"
{ echo 'schema=sp11-camera-ih-front-to-rear-r27-r16-retire-v1'; echo 'status=PASS_CANDIDATE_RETIRED'; echo "time=$(date -Ins)"; echo "candidate_id=$ID"; } > "$D/RETIRE.txt"
echo 'IH_RETIRE=PASS'
