#!/usr/bin/env bash
# E004iw: consume exactly ONE camera-free diagnostic boot, then return Golden.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004iw
T=$R/experiments/E004-front-ir-vd55g0/e004iw-bootenv-owner-safe-diagnostic
ID=sp11-camera-e004iw-bootenv-diagnostic-one-shot
cd "$R"
[[ ! -f "$T/evidence/OBSERVED.json" ]]
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-ARMED"
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemd-analyze verify /etc/systemd/system/sp11-camera-e004iw-bootenv-diagnostic.service
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004iw-bootenv-diagnostic.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004iw-bootenv-diagnostic.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'arm_time=%s\nhead=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004IW_ONE_CAMERA_FREE_DIAGNOSTIC_BOOT_ARMED=PASS GOLDEN_PERSISTENT=YES
sudo -n systemctl reboot --no-block
