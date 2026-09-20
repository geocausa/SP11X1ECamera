#!/usr/bin/env bash
# E004jp: retire only this uniquely identified synthetic virtual camera test.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004jp
B=/boot/sp11-7.1.5-e004jp-virtual-rear
G=/etc/grub.d/99zzzzzz_sp11_e004jp_virtual_rear_4k
S=/etc/systemd/system/sp11-e004jp-virtual-rear-4k.service
X=/usr/local/sbin/sp11-e004jp-virtual-rear-4k-run-once
ID=sp11-e004jp-virtual-rear-4k-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$D" == /var/lib/sp11-camera-e004jp &&
   "$B" == /boot/sp11-7.1.5-e004jp-virtual-rear ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test -e "$D/ATTEMPT-CONSUMED"
sudo -n test -s "$D/ATTEMPT-RESULT.txt"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e /dev/video90
[[ ! -d /sys/module/v4l2loopback ]]
sudo -n systemctl is-active --quiet sp11-e004jp-virtual-rear-4k.service && exit 1 || :
sudo -n systemctl disable sp11-e004jp-virtual-rear-4k.service
sudo -n rm -f "$S" "$X" "$G"
sudo -n systemctl daemon-reload
sudo -n rm -rf -- "$B"
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n rm -rf -- "$D"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
echo E004JP_RETIRED=PASS GOLDEN_UNCHANGED=YES SYNTHETIC_DEVICE_REMOVED=YES
