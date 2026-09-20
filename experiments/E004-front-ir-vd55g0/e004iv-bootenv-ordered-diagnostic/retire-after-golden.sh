#!/usr/bin/env bash
# E004iv: retire ONLY this unique camera-free diagnostic after Golden return.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
T=$R/experiments/E004-front-ir-vd55g0/e004iv-bootenv-ordered-diagnostic
D=/var/lib/sp11-camera-e004iv
UNIT=/etc/systemd/system/sp11-camera-e004iv-bootenv-diagnostic.service
RUN=/usr/local/sbin/sp11-camera-e004iv-bootenv-diagnostic
GRUB_SCRIPT=/etc/grub.d/99zzzzzz_sp11_camera_e004iv
ID=sp11-camera-e004iv-bootenv-diagnostic-one-shot
cd "$R"
./tools/camera-overlap-guard.sh --require-golden --require-no-camera-process
sudo -n test -e "$D/ATTEMPT-ARMED"
sudo -n test -e "$D/ATTEMPT-CONSUMED"
sudo -n test -s "$D/ATTEMPT-RESULT.txt"
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n systemctl is-active --quiet sp11-camera-e004iv-bootenv-diagnostic.service && exit 1 || :
[[ "$D" == /var/lib/sp11-camera-e004iv ]]
sudo -n systemctl disable sp11-camera-e004iv-bootenv-diagnostic.service
sudo -n rm -f -- "$UNIT" "$RUN" "$GRUB_SCRIPT"
sudo -n systemctl daemon-reload
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n rm -rf -- "$D"
./tools/camera-overlap-guard.sh --require-golden --require-no-camera-process
echo E004IV_DIAGNOSTIC_RETIRED=PASS GOLDEN_DEFAULT_UNCHANGED=YES CAMERA_ACCESS=NO
