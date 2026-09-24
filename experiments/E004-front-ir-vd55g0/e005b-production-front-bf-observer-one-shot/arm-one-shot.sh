#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Only arms a NEW one-shot nonGolden FRONT-ONLY boot, no reboot here.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e005b-production-front-bf-observer-one-shot"
ID=sp11-camera-e005b-prod-front-bf-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked \
 --require-golden --require-no-camera-process \
 --expect-head 73c990762d2aadde4aed3e7cc6d3700366b0c07b \
 --expect-origin 73c990762d2aadde4aed3e7cc6d3700366b0c07b
test -s "$D/INSTALL.txt" && test -s "$D/E005B-GRUB-STAGED"
test ! -e "$D/ARM.txt" && test ! -e "$D/ATTEMPT1-CONSUMED.marker"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[ "$(sudo -n grub-editenv /boot/grub/grubenv list|grep '^saved_entry=')" = \
 'saved_entry=sp11-audio-fullio-v19c' ]
! sudo -n grub-editenv /boot/grub/grubenv list | grep -q '^next_entry=.'
sudo -n grub-reboot "$ID"
[ "$(sudo -n grub-editenv /boot/grub/grubenv list|grep '^next_entry=')" = "next_entry=$ID" ]
# ARM.txt makes replay impossible. Persist before caller dispatches reboot.
{ echo 'schema=E005b-fresh-production-front-scalar-one-shot-arm-v1';
  echo 'status=ARMED_FRESH_NON_GOLDEN_BOOT';
  echo "time=$(date -Ins)";
  echo "Golden_saved=sp11-audio-fullio-v19c";
  echo "next_entry=$ID";
  echo "parent_git=$(git rev-parse HEAD)";
  echo 'rear_processed_ISP_runtime_authorized=NO';
} > "$D/ARM.txt"
sync
echo E005B_FRONT_ONLY_ONE_SHOT_BOOT_ARMED_RETURN_GOLDEN_PERSISTENT
