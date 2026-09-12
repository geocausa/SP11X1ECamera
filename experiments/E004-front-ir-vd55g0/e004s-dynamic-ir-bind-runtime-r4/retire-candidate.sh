#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004s-dynamic-ir-bind-runtime-r4
BOOT=/boot/sp11-7.1.5-camera-e004s-dynamic-ir-bind-r4
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004s_dynamic_ir_bind_r4
ID=sp11-camera-e004s-dynamic-ir-bind-r4-one-shot
"$D/golden-return-check.sh"
sudo -n rm -f "$ENTRY"; sudo -n rm -rf "$BOOT"; sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
rm -rf "$D/build"
{
 echo 'schema=sp11-camera-e004s-retire-v1'; echo 'status=PASS_CANDIDATE_RETIRED'; echo "time=$(date -Ins)"; echo "candidate_id=$ID"
} > "$D/RETIRE.txt"
echo 'E004S_RETIRE=PASS'
