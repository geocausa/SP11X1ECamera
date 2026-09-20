#!/usr/bin/env bash
# E004jw: arm ONLY the verified new one-shot GRUB target and reboot once.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004jw
ID=sp11-camera-e004jw-rear4k-cadence-one-shot
cd "$R"
[[ ! -e "$R/experiments/E004-front-ir-vd55g0/e004jw-rear4k-cadence-one-shot/evidence/PRE-CAMERA-ABORT.json" ]] || { echo E004JW_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
[[ "$(sudo -n stat -c%s "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin")" == 41088 ]]
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
sudo -n test -s "$D/FRONT-LAUNCH-DRYRUN.json"
sudo -n test ! -e /dev/video90
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == e55af362997d7f61c9e1cf79f964dabf6b69e8f17ab0b1dcd2ef3a2fccf3a8c3 ]]
[[ "$(sudo -n sha256sum "$D/bridge/rear-bayer-to-nv12-4k" | awk '{print $1}')" == bee13334b2cb0627373aca97c5edb6c018c7fe40d4a2fb9ce08c82a96554592a ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-4k-sustained-app.py" | awk '{print $1}')" == 805fdb15b92f62da88bdfb674e1ae2ba015ece35859b3bfc10228f528173613a ]]
sudo -n grep -Fq 'E004JW_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
sudo -n grep -Fq 'E004JV_NV12_APPSRC_CONSUMER=PASS FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
sudo -n grep -Fq 'E004JW_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$D/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sudo -n sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004jw/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004jw-one-shot.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004jw-one-shot.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'arm_time=%s\nexpected_head=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004JW_ARMED=ONE_SHOT AUTO_RETURN_TO_GOLDEN_AFTER_RUN=ENABLED
sudo -n systemctl reboot --no-block
