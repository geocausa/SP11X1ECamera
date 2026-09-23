#!/usr/bin/env bash
# E004mx: retire only this test's root-owned package, GRUB entry and service
# after an observed return to protected Golden. Do NOT rerun the one-shot.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004mx
B=/boot/sp11-7.1.5-camera-e004mx-rgb-session
G=/etc/grub.d/99zzzzzz_sp11_camera_e004mx
S=/etc/systemd/system/sp11-camera-e004mx-one-shot.service
X=/usr/local/sbin/sp11-camera-e004mx-run-once
ID=sp11-camera-e004mx-front-gain-tone-guarded-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$D" == /var/lib/sp11-camera-e004mx &&
   "$B" == /boot/sp11-7.1.5-camera-e004mx-rgb-session ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test -e "$D/ATTEMPT-CONSUMED"
sudo -n test -s "$D/ATTEMPT-RESULT.txt"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n systemctl is-active --quiet sp11-camera-e004mx-one-shot.service && exit 1 || :
sudo -n systemctl disable sp11-camera-e004mx-one-shot.service
sudo -n rm -f "$S" "$X" "$G"
sudo -n systemctl stop sp11-camera-e004mx-session@front.service sp11-camera-e004mx-session@rear.service
sudo -n rm -f /etc/systemd/system/sp11-camera-e004mx-session@.service
sudo -n rm -rf -- /usr/local/lib/sp11-camera-e004mx
sudo -n systemctl daemon-reload
sudo -n rm -rf -- "$B"
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
# Preserve only the already-inspected redacted status in the repository;
# raw camera QC10C frame files and system logs remain private until deletion.
# The only intentional local photo export is from root-private candidate
# storage to the same SP11 user's private Pictures folder AFTER Golden.
# Never copy images to repository/evidence, network or remote connector.
LOCAL=/home/geoca/Pictures/SP11-Camera-Private-E004mx
all_private_pngs=YES
for camera in front rear; do
 for stage in baseline gain; do
  f="$D/private-optical/$camera-$stage-private.png"
  if ! sudo -n test -s "$f"; then all_private_pngs=NO; fi
 done
done
if [[ "$all_private_pngs" == YES ]]; then
 [[ ! -e "$LOCAL" && ! -L "$LOCAL" ]]
 sudo -n install -d -m 0700 -o geoca -g geoca "$LOCAL"
 for camera in front rear; do
  for stage in baseline gain; do
   sudo -n install -m 0600 -o geoca -g geoca \
     "$D/private-optical/$camera-$stage-private.png" \
     "$LOCAL/$camera-$stage-private.png"
  done
 done
 echo "E004MX_LOCAL_PRIVATE_OPTICAL_PICTURES=$LOCAL FRONT_REAR_BASELINE_GAIN=YES REMOTE_EXPORT=NO"
else
 echo "E004MX_LOCAL_PRIVATE_OPTICAL_PICTURES=INCOMPLETE_NOT_EXPORTED"
fi
sudo -n rm -rf -- "$D"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
echo E004MX_RETIRED=PASS GOLDEN_PERSISTENT=YES CAMERA_DEFAULT=UNCHANGED
