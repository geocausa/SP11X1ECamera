#!/usr/bin/env bash
set -euo pipefail
D=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff
BOOT=/boot/sp11-7.1.5-camera-e004dz-canonical-package-rgb-handoff
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004dz_canonical_package_rgb_handoff
ID=sp11-camera-e004dz-canonical-package-rgb-handoff-one-shot
"$D/golden-return-check.sh"; sudo -n rm -f "$ENTRY"; sudo -n rm -rf "$BOOT"; sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
{ echo schema=sp11-camera-e004dz-retire-v1; echo status=PASS_CANDIDATE_RETIRED; echo time=$(date -Ins); echo candidate_id=$ID; echo package_still_installed=YES; } > "$D/RETIRE.txt"
echo E004DZ_RETIRE=PASS PACKAGE=STILL_INSTALLED
