#!/usr/bin/env bash
# E004mg: uniquely guarded LONG software RGB test, automatic Golden return.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004mg
ID=sp11-camera-e004mg-private-optical-rgb-visual-one-shot
cd "$R"
[[ ! -e "$R/experiments/E004-front-ir-vd55g0/e004mg-private-optical-rgb-visual-one-shot/evidence/PRE-CAMERA-ABORT.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004mg-private-optical-rgb-visual-one-shot/evidence/CONSUMED.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004mg-private-optical-rgb-visual-one-shot/RESULT.json" ]] || { echo E004MG_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
[[ "$(sudo -n stat -c%s "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin")" == 41088 ]]
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
sudo -n test -s "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
for video in /dev/video90 /dev/video91; do sudo -n test ! -e "$video"; done
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == be617fc944da4a85dabaf62b2e190f126f7c39a2ea655a8ae946ee50ea39134b ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-nv12-1080p-pipe-audit" | awk '{print $1}')" == 23e5152cea7dab8b437eae309f16a8f33e7c01b50f9ab61fa26f952d90b3600e ]]
[[ "$(sudo -n modinfo -F vermagic "$D/v4l2loopback.ko")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-rggb10p-to-nv12-1080" | awk '{print $1}')" == 820a6871f78e9ecaecfd4b1a16fc1e0bad9600aeeb6a1505133e467c1354dc82 ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-rdi-raw10-pipe-audit" | awk '{print $1}')" == 377a9c2e8704bd57687c5449608c632e1e06cc39067b87cc28aa3ac8a060d186 ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-1080p-app.py" | awk '{print $1}')" == e165491ea22bcc4c452ea03073525662293c30ff3c274c67c4c6d4872e1c6b0a ]]
[[ "$(sudo -n sha256sum "$D/route-state.py" | awk '{print $1}')" == 53c2230114512b954c67fa4572df569394d3bd259fb3ae036691f72002009861 ]]
[[ "$(sudo -n sha256sum "$D/validate-front-rdi.py" | awk '{print $1}')" == 934fb0aea58c8996ec9edd1e9581c3ce83d7c48cff0ba8ae10923c4877ec95f4 ]]
sudo -n grep -Fq 'E004KH_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KH_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$D/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
sudo -n python3 "$H/validate_boot_token.py" --candidate e004mg --front-source "$H/front-direct-publisher.c" --rear-source "$H/rear-direct-publisher.c" --front-elf "$D/bridge/front-direct-publisher" --rear-elf "$D/bridge/rear-direct-publisher"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sudo -n sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004mg/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004mg-one-shot.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004mg-one-shot.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'arm_time=%s\nexpected_head=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n sha256sum -c "$D/SESSION-ASSETS.sha256" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004MG_ARMED=ONE_SHOT AUTO_RETURN_TO_GOLDEN_AFTER_RUN=ENABLED
sudo -n systemctl reboot --no-block
