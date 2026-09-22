#!/usr/bin/env bash
# Retire only E004lo assets after independent Golden observation.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004lo
BOOT=/boot/sp11-7.1.5-camera-e004lo-libcamera
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004lo
SERVICE=/etc/systemd/system/sp11-camera-e004lo-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004lo-run-once
ID=sp11-camera-e004lo-libcamera-registration-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$D" == /var/lib/sp11-camera-e004lo && "$BOOT" == /boot/sp11-7.1.5-camera-e004lo-libcamera ]]
sudo -n test -f "$D/ATTEMPT-ARMED"
sudo -n test -f "$D/ATTEMPT-CONSUMED"
sudo -n test -s "$D/ATTEMPT-RESULT.txt"
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
! sudo -n systemctl is-active --quiet sp11-camera-e004lo-one-shot.service
sudo -n systemctl disable sp11-camera-e004lo-one-shot.service
sudo -n rm -f -- "$SERVICE" "$RUNNER" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n rm -rf -- "$BOOT"
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n rm -rf -- "$D"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
echo E004LO_RETIRED=PASS_GOLDEN_UNCHANGED
