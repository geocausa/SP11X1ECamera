#!/usr/bin/env bash
# E004kd: arm ONLY the verified new one-shot GRUB target and reboot once.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004kd
ID=sp11-camera-e004kd-rear4k-extended-unique-app-one-shot
cd "$R"
[[ ! -e "$R/experiments/E004-front-ir-vd55g0/e004kd-rear4k-extended-unique-app-one-shot/evidence/PRE-CAMERA-ABORT.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004kd-rear4k-extended-unique-app-one-shot/evidence/CONSUMED.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004kd-rear4k-extended-unique-app-one-shot/RESULT.json" ]] || { echo E004KD_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
[[ "$(sudo -n stat -c%s "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin")" == 41088 ]]
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
sudo -n test -s "$D/FRONT-LAUNCH-DRYRUN.json"
sudo -n test ! -e /dev/video90
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == 1f8378df078a118860e2bc35825fd127678ae164063e19e7d1cea2012d61259a ]]
[[ "$(sudo -n sha256sum "$D/bridge/rear-bayer-to-nv12-4k" | awk '{print $1}')" == 35f658158f5d6d74ba5ea3a25c2d3d6b291fa0ba49dcd8b9c27005f124acc406 ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-4k-partial-telemetry-app.py" | awk '{print $1}')" == 1e129b385d9d849808eadd1e8b43224e721c19c3bb364513975604d05ce7e0b8 ]]
[[ "$(sudo -n sha256sum "$D/validate-partial.py" | awk '{print $1}')" == fd23a7eec5fbdb5dd8576b3682652633e2dab60ffe0df9a6e6416bff430f40ea ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-4k-pipe-audit" | awk '{print $1}')" == aad050944551f77f71c760031bfa3d25968e9ab2e5accf74ffdae561be3e852b ]]
sudo -n grep -Fq 'E004JZ_4K_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/REAR-PIPE-AUDIT-DRYRUN.txt"
sudo -n grep -Fq 'E004KD_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
sudo -n grep -Fq 'E004JX_NV12_APPSRC_CONSUMER=PASS FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
sudo -n grep -Fq 'E004KD_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$D/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sudo -n sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004kd/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004kd-one-shot.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004kd-one-shot.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'arm_time=%s\nexpected_head=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004KD_ARMED=ONE_SHOT AUTO_RETURN_TO_GOLDEN_AFTER_RUN=ENABLED
sudo -n systemctl reboot --no-block
