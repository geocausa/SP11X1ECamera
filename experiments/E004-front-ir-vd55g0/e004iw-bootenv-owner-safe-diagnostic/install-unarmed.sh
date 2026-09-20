#!/usr/bin/env bash
# E004iw: install a unique, camera-free GRUB diagnostic UNARMED.
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
T=$R/experiments/E004-front-ir-vd55g0/e004iw-bootenv-owner-safe-diagnostic
D=/var/lib/sp11-camera-e004iw
GRUB_SCRIPT=/etc/grub.d/99zzzzzz_sp11_camera_e004iw
UNIT=/etc/systemd/system/sp11-camera-e004iw-bootenv-diagnostic.service
RUN=/usr/local/sbin/sp11-camera-e004iw-bootenv-diagnostic
ID=sp11-camera-e004iw-bootenv-diagnostic-one-shot
cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$T/evidence/OBSERVED.json" ]]
for f in "$D" "$GRUB_SCRIPT" "$UNIT" "$RUN"; do sudo -n test ! -e "$f"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ -f /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ ]]
[[ -f /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c ]]
[[ -f /boot/sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb ]]
bash -n "$T/run-diagnostic-once.sh"
tail -n +3 "$T/99zzzzzz_sp11_camera_e004iw" | grub-script-check
systemctl cat grub2-common.service | grep -Fq '/boot/grub/grubenv unset recordfail'
systemctl cat grub-initrd-fallback.service | grep -Fq '/boot/grub/grubenv unset initrdfail'
grep -Fq 'After=local-fs.target grub2-common.service grub-initrd-fallback.service' "$T/sp11-camera-e004iw-bootenv-diagnostic.service"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n mkdir -m 0700 "$D"
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
sudo -n chmod 0600 "$D/EXPECTED-HEAD"
sudo -n install -m 0700 "$T/run-diagnostic-once.sh" "$RUN"
sudo -n install -m 0644 "$T/sp11-camera-e004iw-bootenv-diagnostic.service" "$UNIT"
sudo -n install -m 0755 "$T/99zzzzzz_sp11_camera_e004iw" "$GRUB_SCRIPT"
sudo -n systemctl daemon-reload
sudo -n systemd-analyze verify "$UNIT"
sudo -n systemctl enable sp11-camera-e004iw-bootenv-diagnostic.service
sudo -n update-grub >/dev/null
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemctl is-active --quiet sp11-camera-e004iw-bootenv-diagnostic.service && exit 1 || :
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
echo E004IW_DIAGNOSTIC_INSTALLED_UNARMED=PASS GOLDEN_UNMODIFIED=YES CAMERA_ACCESS=NO
