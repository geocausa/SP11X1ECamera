#!/usr/bin/env bash
# Retire only E004lp assets after independent Golden observation.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004lp
BOOT=/boot/sp11-7.1.5-camera-e004lp-registration
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004lp
SERVICE=/etc/systemd/system/sp11-camera-e004lp-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004lp-run-once
ID=sp11-camera-e004lp-registration-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$D" == /var/lib/sp11-camera-e004lp && "$BOOT" == /boot/sp11-7.1.5-camera-e004lp-registration ]]
sudo -n test -f "$D/ATTEMPT-ARMED"
sudo -n test -f "$D/ATTEMPT-CONSUMED"
sudo -n test -s "$D/ATTEMPT-RESULT.txt"
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
! sudo -n systemctl is-active --quiet sp11-camera-e004lp-one-shot.service
sudo -n systemctl disable sp11-camera-e004lp-one-shot.service
sudo -n rm -f -- "$SERVICE" "$RUNNER" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n rm -rf -- "$BOOT"
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n rm -rf -- "$D"
# The compiled-in IPA/config path points to this separately root-sealed
# source/build tree. Delete it ONLY after the independent Golden proof.
B=/var/lib/sp11-e004lp-build
[[ "$B" == /var/lib/sp11-e004lp-build ]]
sudo -n test -d "$B"
sudo -n rm -rf -- "$B"

"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
echo E004LP_RETIRED=PASS_GOLDEN_UNCHANGED
