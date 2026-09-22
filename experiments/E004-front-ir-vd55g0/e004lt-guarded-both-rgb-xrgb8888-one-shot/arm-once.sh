#!/usr/bin/env bash
# E004lt: mark ONE attempt consumed before scheduling one-time diagnostic boot.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004lt-guarded-both-rgb-xrgb8888-one-shot
D=/var/lib/sp11-camera-e004lt
ID=sp11-camera-e004lt-xrgb8888-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$H/CONSUMED.json" && ! -e "$H/RESULT.json" ]]
sudo -n test ! -e "$D/ATTEMPT-ARMED"
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004lt && sha256sum -c SESSION-ASSETS.sha256 >/dev/null'
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004lt-one-shot.service)" == enabled ]]
! sudo -n systemctl is-active --quiet sp11-camera-e004lt-one-shot.service
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
for name in /dev/media0 /dev/video90 /dev/video91; do [[ ! -e "$name" ]]; done
# A failed/suspended arm still consumes the fresh identity. No retry.
printf 'arm_time=%s\nexpected_head=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" |
  sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
sync
echo E004LT_ARMED=ONE_SHOT_GOLDEN_DEFAULT_UNCHANGED
sudo -n systemctl reboot --no-block
