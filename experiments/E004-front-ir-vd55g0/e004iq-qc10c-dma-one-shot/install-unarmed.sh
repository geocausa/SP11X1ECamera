#!/usr/bin/env bash
# E004iq: install root-owned NON-DEFAULT, NON-ARMED one-shot test assets.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004iq-qc10c-dma-one-shot
SOURCE=/tmp/sp11-e004iq-qc10c-regression-20260920
D=/var/lib/sp11-camera-e004iq
BOOT=/boot/sp11-7.1.5-camera-e004iq-qc10c-dma-guard
ENTRY=/etc/grub.d/99zzzzzz_sp11_camera_e004iq
SERVICE=/etc/systemd/system/sp11-camera-e004iq-one-shot.service
RUNNER=/usr/local/sbin/sp11-camera-e004iq-run-once
ID=sp11-camera-e004iq-qc10c-dma-guard-one-shot
cd "$R"
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$D" && ! -e "$BOOT" ]]
for f in "$ENTRY" "$SERVICE" "$RUNNER"; do sudo -n test ! -e "$f"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
! grep -Fq 'sp11_camera_e004iq_qc10c_dma_guard=1' /proc/cmdline
[[ "$(sha256sum "$SOURCE/stage/CAMERA-STACK-MANIFEST.sha256" | awk '{print $1}')" == 11a649fafbfbfc3467f86f2f17d8ff4d4a86e2f5f4fc36c7f1d1c7839160c646 ]]
( cd "$SOURCE/stage"; sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null )
python3 "$R/src/sp11-camera-stack/verify-package.py" "$SOURCE/stage"
[[ "$(sha256sum "$SOURCE/candidate/camss/qcom-camss.ko" | awk '{print $1}')" == 950ca403fc224873762001a013ec278bf93b041eb12e1ad7a0bd3687c86b4f56 ]]
[[ "$(sha256sum "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/modules/qcom-camss.ko" | awk '{print $1}')" == 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]]
[[ "$(sha256sum "$SOURCE/stage/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" | awk '{print $1}')" == 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ]]
[[ "$(modinfo -F vermagic "$SOURCE/candidate/camss/qcom-camss.ko")" == "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64" ]]
find "$SOURCE/stage/usr" -type l | grep . && exit 1 || :
bash -n "$H/run-once.sh"
tail -n +3 "$H/99zzzzzz_sp11_camera_e004iq" | grub-script-check
systemd-analyze verify "$H/sp11-camera-e004iq-one-shot.service" 2>&1 |
  grep -v 'not executable: No such file or directory' || :
# Stage only the candidate assets in a newly created, root-owned directory.
sudo -n mkdir -m 0700 "$D"
sudo -n cp -a "$SOURCE/stage" "$D/stack"
sudo -n mkdir -m 0700 "$D/candidate"
sudo -n install -m 0644 "$SOURCE/candidate/camss/qcom-camss.ko" "$D/candidate/qcom-camss.ko"
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
sudo -n chown -R root:root "$D"
sudo -n chmod 0700 "$D"
sudo -n sh -c 'cd /var/lib/sp11-camera-e004iq/stack && sha256sum -c CAMERA-STACK-MANIFEST.sha256 >/dev/null'
[[ "$(sudo -n sha256sum "$D/candidate/qcom-camss.ko" | awk '{print $1}')" == 950ca403fc224873762001a013ec278bf93b041eb12e1ad7a0bd3687c86b4f56 ]]
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-camera-e004iq-one-shot.service" "$SERVICE"
sudo -n mkdir -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-camera-e004iq-qc10c-dma-guard"
sudo -n install -m 0644 "$D/stack/usr/lib/sp11-camera-stack/hardware/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$BOOT/"
sudo -n install -m 0755 "$H/99zzzzzz_sp11_camera_e004iq" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-camera-e004iq-one-shot.service
sudo -n update-grub > "$SOURCE/UPDATE-GRUB.log"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
sudo -n systemctl is-enabled sp11-camera-e004iq-one-shot.service
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemctl is-active --quiet sp11-camera-e004iq-one-shot.service && exit 1 || :
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004IQ_INSTALLED=PASS ARMED=NO ACTIVE_CAMERA=NO AUTOMATIC_GOLDEN_RETURN_UNIT=ENABLED
