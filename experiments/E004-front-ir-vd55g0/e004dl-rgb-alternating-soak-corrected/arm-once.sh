#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dl-rgb-alternating-soak-corrected
ID=sp11-camera-e004dl-rgb-alternating-soak-corrected-one-shot
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[ -f "$D/INSTALL.txt" ] && grep -q 'status=INSTALLED_UNARMED' "$D/INSTALL.txt"
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ]
(cd "$R" && sha256sum -c "$D/KNOWN-DIRTY.sha256" >/dev/null)
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
sudo -n grub-reboot "$ID"
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx "next_entry=$ID"<<<"$ENV"
{ echo schema=sp11-camera-e004dl-arm-v1; echo status=ARMED_ONE_SHOT; echo time=$(date -Ins); echo head=$(git -C "$R" rev-parse HEAD); echo saved_entry=sp11-audio-fullio-v19c; echo next_entry=$ID; } > "$D/ARM.txt"
sync; echo "E004DL_ARMED=$ID REBOOT_REQUIRED=YES"
