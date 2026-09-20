#!/usr/bin/env bash
# E004jg: ONLY new source-locked synthetic virtual webcam one-shot.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004jg-virtual-rear-device-offline-one-shot
D=/var/lib/sp11-camera-e004jg
ID=sp11-e004jg-virtual-rear-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]] || { echo E004JG_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
sudo -n test ! -e /dev/video90
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == 2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1 ]]
[[ "$(sudo -n sha256sum "$D/nv12-appsrc-consumer.py" | awk '{print $1}')" == 9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613 ]]
[[ "$(sudo -n systemctl is-enabled sp11-e004jg-virtual-rear.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-e004jg-virtual-rear.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'armed_at=%s\nhead=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004JG_ARMED_UNIQUE_SYNTHETIC_ONLY_AUTO_GOLDEN_RETURN=YES
sudo -n systemctl reboot --no-block
