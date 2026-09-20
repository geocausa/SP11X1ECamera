#!/usr/bin/env bash
# E004ka: retire only this test's root-owned package, GRUB entry and service
# after an observed return to protected Golden. Do NOT rerun the one-shot.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004ka
B=/boot/sp11-7.1.5-camera-e004ka-boundary
G=/etc/grub.d/99zzzzzz_sp11_camera_e004ka
S=/etc/systemd/system/sp11-camera-e004ka-one-shot.service
X=/usr/local/sbin/sp11-camera-e004ka-run-once
ID=sp11-camera-e004ka-rear4k-byte-boundary-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$D" == /var/lib/sp11-camera-e004ka &&
   "$B" == /boot/sp11-7.1.5-camera-e004ka-boundary ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test -e "$D/ATTEMPT-CONSUMED"
sudo -n test -s "$D/ATTEMPT-RESULT.txt"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n systemctl is-active --quiet sp11-camera-e004ka-one-shot.service && exit 1 || :
sudo -n systemctl disable sp11-camera-e004ka-one-shot.service
sudo -n rm -f "$S" "$X" "$G"
sudo -n systemctl daemon-reload
sudo -n rm -rf -- "$B"
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
# Preserve only the already-inspected redacted status in the repository;
# raw camera QC10C frame files and system logs remain private until deletion.
sudo -n rm -rf -- "$D"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
echo E004KA_RETIRED=PASS GOLDEN_PERSISTENT=YES CAMERA_DEFAULT=UNCHANGED
