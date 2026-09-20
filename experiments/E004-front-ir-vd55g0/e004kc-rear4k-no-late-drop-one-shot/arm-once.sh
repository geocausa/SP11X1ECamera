#!/usr/bin/env bash
# E004kc: arm ONLY the verified new one-shot GRUB target and reboot once.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004kc
ID=sp11-camera-e004kc-rear4k-no-late-drop-one-shot
cd "$R"
[[ ! -e "$R/experiments/E004-front-ir-vd55g0/e004kc-rear4k-no-late-drop-one-shot/evidence/PRE-CAMERA-ABORT.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004kc-rear4k-no-late-drop-one-shot/evidence/CONSUMED.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004kc-rear4k-no-late-drop-one-shot/RESULT.json" ]] || { echo E004KC_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
[[ "$(sudo -n stat -c%s "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin")" == 41088 ]]
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
sudo -n test -s "$D/FRONT-LAUNCH-DRYRUN.json"
sudo -n test ! -e /dev/video90
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == a8fb487b1a9bd92ea13c6c0d9eea956ebb065ab14ba1ffe690d8c0c079958b8d ]]
[[ "$(sudo -n sha256sum "$D/bridge/rear-bayer-to-nv12-4k" | awk '{print $1}')" == f272fb31d626a71a3f619fd00162c68488a62b4a9e68231b3dce11af186abea8 ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-4k-partial-telemetry-app.py" | awk '{print $1}')" == 1e129b385d9d849808eadd1e8b43224e721c19c3bb364513975604d05ce7e0b8 ]]
[[ "$(sudo -n sha256sum "$D/validate-partial.py" | awk '{print $1}')" == 268ffc5e778b8d5e5411424ac0f62f7b56a8e029d6c18c789c79c5f900676606 ]]
[[ "$(sudo -n sha256sum "$D/bridge/nv12-4k-pipe-audit" | awk '{print $1}')" == aad050944551f77f71c760031bfa3d25968e9ab2e5accf74ffdae561be3e852b ]]
sudo -n grep -Fq 'E004JZ_4K_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/REAR-PIPE-AUDIT-DRYRUN.txt"
sudo -n grep -Fq 'E004KC_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
sudo -n grep -Fq 'E004JX_NV12_APPSRC_CONSUMER=PASS FRAMES=1' "$D/REAR-APP-DRYRUN.txt"
sudo -n grep -Fq 'E004KC_OFFLINE_4K=PASS SOURCE=pgAA_4076x2806 OUTPUT=NV12_3840x2160 FRAMES=1' "$D/REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sudo -n sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004kc/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004kc-one-shot.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004kc-one-shot.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'arm_time=%s\nexpected_head=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004KC_ARMED=ONE_SHOT AUTO_RETURN_TO_GOLDEN_AFTER_RUN=ENABLED
sudo -n systemctl reboot --no-block
