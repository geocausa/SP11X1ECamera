#!/usr/bin/env bash
# E004js irreversible retirement after verified automatic Golden return.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004js
B=/boot/sp11-7.1.5-camera-e004js-graph
G=/etc/grub.d/99zzzzzz_sp11_camera_e004js
S=/etc/systemd/system/sp11-camera-e004js-one-shot.service
X=/usr/local/sbin/sp11-camera-e004js-run-once
ID=sp11-camera-e004js-graph-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
[[ "$D" == /var/lib/sp11-camera-e004js && "$B" == /boot/sp11-7.1.5-camera-e004js-graph ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test -s "$D/ATTEMPT-CONSUMED"
sudo -n test -s "$D/ATTEMPT-RESULT.txt"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n systemctl is-active --quiet sp11-camera-e004js-one-shot.service && exit 1 || :
sudo -n systemctl disable sp11-camera-e004js-one-shot.service
sudo -n rm -f "$S" "$X" "$G"
sudo -n systemctl daemon-reload
sudo -n rm -rf -- "$B"
sudo -n update-grub >/dev/null
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
# Repo stores only summarized non-image evidence; private device graphs and
# kernel logs are deleted after redacted diagnostics have been extracted.
sudo -n rm -rf -- "$D"
"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process
echo E004JS_RETIRED_GOLDEN_UNCHANGED=PASS
