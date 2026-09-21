#!/usr/bin/env bash
# E004kf: arm ONLY the verified new one-shot GRUB target and reboot once.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004kf
ID=sp11-camera-e004kf-front-rdi-optical-native1080-one-shot
cd "$R"
[[ ! -e "$R/experiments/E004-front-ir-vd55g0/e004kf-front-rdi-optical-native1080-one-shot/evidence/PRE-CAMERA-ABORT.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004kf-front-rdi-optical-native1080-one-shot/evidence/CONSUMED.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004kf-front-rdi-optical-native1080-one-shot/RESULT.json" ]] || { echo E004KF_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
[[ "$(sudo -n stat -c%s "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin")" == 41088 ]]
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
sudo -n test -s "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
for video in /dev/video90 /dev/video91; do sudo -n test ! -e "$video"; done
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-rggb10p-to-nv12-1080" | awk '{print $1}')" == 3b4120431e0bc00429967dc476a24fc1edf5b2d082e12e814c1065bdf17724db ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-rdi-raw10-pipe-audit" | awk '{print $1}')" == 9ef2bcc93b85ba8e1af3337f77d6e8dbe0d8a2bd23ea70793f84c293e7be14df ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-1080p-app.py" | awk '{print $1}')" == 38fe90ca920b31edb1dced7bb36874d29a7ebc129754220546410130a20c068e ]]
[[ "$(sudo -n sha256sum "$D/route-state.py" | awk '{print $1}')" == 91dbfe9b1ae299c69792e62efcc8cf2e2e0da665dc46d90743c64b83d5cec035 ]]
[[ "$(sudo -n sha256sum "$D/validate-front-rdi.py" | awk '{print $1}')" == ad5592776eb77cb941b96763cb4cb3419cff95a3f2b62cca50cd526dbc643c8b ]]
sudo -n grep -Fq 'E004KF_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KE_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KF_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sudo -n sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004kf/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004kf-one-shot.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004kf-one-shot.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'arm_time=%s\nexpected_head=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004KF_ARMED=ONE_SHOT AUTO_RETURN_TO_GOLDEN_AFTER_RUN=ENABLED
sudo -n systemctl reboot --no-block
