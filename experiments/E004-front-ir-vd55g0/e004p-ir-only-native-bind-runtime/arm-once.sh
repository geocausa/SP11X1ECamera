#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004p-ir-only-native-bind-runtime
ID=sp11-camera-e004p-ir-only-bind-one-shot
HEAD=$(git -C "$R" rev-parse HEAD); ORIGIN=$(git -C "$R" rev-parse '@{u}')
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process --expect-head "$HEAD" --expect-origin "$ORIGIN"
[ "$HEAD" = "$ORIGIN" ]
[ -z "$(git -C "$R" status --porcelain -- experiments/E004-front-ir-vd55g0 src/front-ir-vd55g0)" ]
"$D/verify-installed.sh"
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
sudo -n grub-reboot "$ID"
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx "next_entry=$ID"<<<"$ENV"
{
 echo 'schema=sp11-camera-e004p-arm-v1'; echo 'status=ARMED_ONE_SHOT'; echo "time=$(date -Ins)"
 echo "head=$HEAD"; echo 'saved_entry=sp11-audio-fullio-v19c'; echo "next_entry=$ID"
} > "$D/ARM.txt"
sync
echo "E004P_ARMED=$ID REBOOT_REQUIRED=YES"
