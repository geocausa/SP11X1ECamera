#!/usr/bin/env bash
# E004js single-use bounded read-only diagnostics on camera candidate.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004js-live-graph-diagnostic-one-shot
D=/var/lib/sp11-camera-e004js
ID=sp11-camera-e004js-graph-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]]
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
[[ "$(sudo -n sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | cut -d' ' -f1)" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004js/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n sha256sum "$D/camera-media-graph-diagnostic.py" | cut -d' ' -f1)" == "$(sudo -n cat "$D/EXPECTED-DIAGNOSTIC-SHA256")" ]]
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004js-one-shot.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004js-one-shot.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'armed_at=%s\nhead=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004JS_ONE_SHOT_ARMED_RETURN_GOLDEN_AFTER=YES
sudo -n systemctl reboot --no-block
