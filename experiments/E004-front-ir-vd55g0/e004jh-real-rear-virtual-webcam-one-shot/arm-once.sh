#!/usr/bin/env bash
# E004jh: arm ONLY the verified new one-shot GRUB target and reboot once.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004jh
ID=sp11-camera-e004jh-two-rgb-dma-guard-one-shot
cd "$R"
[[ ! -e "$R/experiments/E004-front-ir-vd55g0/e004jh-real-rear-virtual-webcam-one-shot/evidence/PRE-CAMERA-ABORT.json" ]] || { echo E004JH_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
[[ "$(sudo -n stat -c%s "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin")" == 41088 ]]
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
sudo -n test -s "$D/FRONT-LAUNCH-DRYRUN.json"
sudo -n test ! -e /dev/video90
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == 2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1 ]]
[[ "$(sudo -n sha256sum "$D/bridge/rear-bayer-stdin-to-nv12" | awk '{print $1}')" == a5b949303fbb40adbdcc62fe494823fec1524feca4d3cd7d5aa273eebdb73c15 ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-appsrc-consumer.py" | awk '{print $1}')" == 9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613 ]]
sudo -n grep -Fq 'E004JE_BAYER10_STREAM_NV12=PASS FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
sudo -n grep -Fq 'E004JE_NV12_APPSRC_CONSUMER=PASS FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
sudo -n grep -Fq 'E004JE_BAYER10_STREAM_NV12=PASS FRAMES=1' "$D/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
[[ "$(sudo -n sha256sum "$D/candidate/qcom-camss.ko" | awk '{print $1}')" == 4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d ]]
[[ "$(sudo -n sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004jh/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004jh-one-shot.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004jh-one-shot.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'arm_time=%s\nexpected_head=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004JH_ARMED=ONE_SHOT AUTO_RETURN_TO_GOLDEN_AFTER_RUN=ENABLED
sudo -n systemctl reboot --no-block
