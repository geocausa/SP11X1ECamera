#!/usr/bin/env bash
# E004kh: arm ONLY the verified new one-shot GRUB target and reboot once.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=/var/lib/sp11-camera-e004kj
ID=sp11-camera-e004kj-front-rear-sequential-session-one-shot
cd "$R"
[[ ! -e "$R/experiments/E004-front-ir-vd55g0/e004kj-front-rear-sequential-session-one-shot/evidence/PRE-CAMERA-ABORT.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004kj-front-rear-sequential-session-one-shot/evidence/CONSUMED.json" && ! -e "$R/experiments/E004-front-ir-vd55g0/e004kj-front-rear-sequential-session-one-shot/RESULT.json" ]] || { echo E004KH_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ "$(sudo -n cat "$D/EXPECTED-HEAD")" == "$(git rev-parse HEAD)" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
[[ "$(sudo -n stat -c%s "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin")" == 41088 ]]
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin" | awk '{print $1}')" == 1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ]]
sudo -n test -s "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
for video in /dev/video90 /dev/video91; do sudo -n test ! -e "$video"; done
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == 8077fc12d7dc72fdde9237b2d383a26832ce17b022aeeac3e634cd95f9008537 ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-nv12-1080p-pipe-audit" | awk '{print $1}')" == 8160bf78849bf5dac08394f1dc8b935af5399447a79d72e89e141297fc67fdf5 ]]
[[ "$(sudo -n modinfo -F vermagic "$D/v4l2loopback.ko")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-rggb10p-to-nv12-1080" | awk '{print $1}')" == 8e810a80366844a46ec83348d8a019172dfe6c364ae5f6f112d477ab823b90a2 ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-rdi-raw10-pipe-audit" | awk '{print $1}')" == 2524c3588db803e052d28eef755149b8a9ffd0773954a804e1cc92d0ac70786f ]]
[[ "$(sudo -n sha256sum "$D/bridge/front-1080p-app.py" | awk '{print $1}')" == e165491ea22bcc4c452ea03073525662293c30ff3c274c67c4c6d4872e1c6b0a ]]
[[ "$(sudo -n sha256sum "$D/route-state.py" | awk '{print $1}')" == 53c2230114512b954c67fa4572df569394d3bd259fb3ae036691f72002009861 ]]
[[ "$(sudo -n sha256sum "$D/validate-front-rdi.py" | awk '{print $1}')" == 934fb0aea58c8996ec9edd1e9581c3ce83d7c48cff0ba8ae10923c4877ec95f4 ]]
sudo -n grep -Fq 'E004KH_RAW_FRONT_RAW_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KH_FRONT_RDI_BAYER_TO_NV12=PASS SOURCE=SRGGB10P_3840x2160 OUTPUT=NV12_1920x1080 FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$D/FRONT-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KH_NV12_1080P_PIPE=PASS REQUESTED_FRAMES=1 FULL_FRAMES=1' "$D/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
sudo -n grep -Fq 'E004KH_NV12_APPSRC_CONSUMER=PASS FRAMES=1 REQUESTED_FRAMES=1' "$D/FRONT-1080P-OFFLINE-PIPE-DRYRUN.txt"
sudo -n test ! -e "$D/ATTEMPT-ARMED"
[[ "$(sudo -n sha256sum "$D/stack/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sudo -n sha256sum "$D/stack/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
sudo -n sh -c 'cd /var/lib/sp11-camera-e004kj/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n systemctl is-enabled sp11-camera-e004kj-one-shot.service)" == enabled ]]
sudo -n systemctl is-active --quiet sp11-camera-e004kj-one-shot.service && exit 1 || :
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
printf 'arm_time=%s\nexpected_head=%s\nretry=NO\n' "$(date -Is)" "$(git rev-parse HEAD)" | sudo -n tee "$D/ATTEMPT-ARMED" >/dev/null
sudo -n sha256sum -c "$D/SESSION-ASSETS.sha256" >/dev/null
sudo -n grub-reboot "$ID"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "$ID" ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
sync
echo E004KH_ARMED=ONE_SHOT AUTO_RETURN_TO_GOLDEN_AFTER_RUN=ENABLED
sudo -n systemctl reboot --no-block
