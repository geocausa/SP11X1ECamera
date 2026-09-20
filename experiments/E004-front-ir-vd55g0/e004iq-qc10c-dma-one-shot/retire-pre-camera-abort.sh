#!/usr/bin/env bash
# E004iq abort retirement. Only if the unique candidate stopped before
# camera-module load and rebooted to the unchanged protected Golden system.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004iq
BOOT=/boot/sp11-7.1.5-camera-e004iq-qc10c-dma-guard
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004iq
SERVICE=/etc/systemd/system/sp11-camera-e004iq-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004iq-run-once
ID=sp11-camera-e004iq-qc10c-dma-guard-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(sudo -n cat "$D/EXPECTED-HEAD")" ]]
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
sudo -n test -f "$D/ATTEMPT-ARMED"
sudo -n test -f "$D/ATTEMPT-RESULT.txt"
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n test ! -e "$D/output/FRONT-LAUNCHER.txt"
sudo -n test ! -e "$D/output/VALIDATION.txt"
[[ "$(sudo -n sed -n '1p' "$D/ATTEMPT-RESULT.txt")" == "FAIL_RC=1 ONE_SHOT_NO_RETRY" ]]
sudo -n journalctl -u sp11-camera-e004iq-one-shot.service -b -1 --no-pager |
  grep -Fq 'grub-editenv: error: invalid environment block'
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n systemctl is-active --quiet sp11-camera-e004iq-one-shot.service && exit 1 || :
[[ "$D" == /var/lib/sp11-camera-e004iq &&
   "$BOOT" == /boot/sp11-7.1.5-camera-e004iq-qc10c-dma-guard ]]
sudo -n systemctl disable sp11-camera-e004iq-one-shot.service
sudo -n rm -f -- "$SERVICE" "$RUNNER" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n rm -rf -- "$BOOT"
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n rm -rf -- "$D"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
echo E004IQ_ABORT_RETIRED=PASS GOLDEN_UNCHANGED=YES NO_CAMERA_ACTIVATION=YES
