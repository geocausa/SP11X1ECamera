#!/usr/bin/env bash
# E004js install distinct non-default candidate, NEVER arm or activate.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004js-live-graph-diagnostic-one-shot
T=$(cat /tmp/sp11-e004js-current-stage-location)
D=/var/lib/sp11-camera-e004js
B=/boot/sp11-7.1.5-camera-e004js-graph
G=/etc/grub.d/99zzzzzz_sp11_camera_e004js
S=/etc/systemd/system/sp11-camera-e004js-one-shot.service
X=/usr/local/sbin/sp11-camera-e004js-run-once
ID=sp11-camera-e004js-graph-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]]
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process --stage-free e004js
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$D" && ! -e "$B" && ! -e /dev/video90 ]]
for f in "$G" "$S" "$X"; do sudo -n test ! -e "$f"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ ! -d /sys/module/qcom_camss && ! -d /sys/module/v4l2loopback ]]
[[ "$T" == /tmp/sp11-e004js-diagnostic.* && -d "$T/stage" ]]
[[ "$(sha256sum "$T/stage/CAMERA-STACK-MANIFEST.sha256" | cut -d' ' -f1)" == 9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455 ]]
python3 src/sp11-camera-stack/verify-package.py "$T/stage" --require-r4
( cd "$T/stage"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null )
[[ "$(sha256sum "$T/stage/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" | cut -d' ' -f1)" == 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ]]
[[ "$(sha256sum "$T/stage/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | cut -d' ' -f1)" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
bash -n "$H/run-once.sh" "$H/arm-once.sh" "$H/retire-after-golden.sh"
tail -n +3 "$H/99zzzzzz_sp11_camera_e004js" | grub-script-check
# Exact package is root-private and never installed in protected Golden.
sudo -n mkdir -m 0700 "$D"
sudo -n cp -a "$T/stage" "$D/stack"
sudo -n install -m 0600 "$R/experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic/camera-media-graph-diagnostic.py" "$D/camera-media-graph-diagnostic.py"
sha256sum "$R/experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic/camera-media-graph-diagnostic.py" | cut -d' ' -f1 | sudo -n tee "$D/EXPECTED-DIAGNOSTIC-SHA256" >/dev/null
git rev-parse HEAD | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
sudo -n chown -R root:root "$D"
sudo -n chmod 0700 "$D"
sudo -n sh -c 'cd /var/lib/sp11-camera-e004js/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
sudo -n systemctl is-active --quiet sp11-camera-e004js-one-shot.service && exit 1 || :
sudo -n install -m 0700 "$H/run-once.sh" "$X"
sudo -n install -m 0644 "$H/sp11-camera-e004js-one-shot.service" "$S"
sudo -n systemd-analyze verify "$S"
sudo -n mkdir -m 0755 "$B"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$B/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$B/initrd.img-7.1.5-sp11-camera-e004js-graph"
sudo -n install -m 0644 "$D/stack/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$B/"
sudo -n install -m 0755 "$H/99zzzzzz_sp11_camera_e004js" "$G"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-camera-e004js-one-shot.service
sudo -n update-grub > "$T/UPDATE-GRUB.txt"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004JS_INSTALLED_NOT_ARMED=PASS CAMERA_NOT_ACTIVE=YES GOLDEN_DEFAULT_UNCHANGED=YES
