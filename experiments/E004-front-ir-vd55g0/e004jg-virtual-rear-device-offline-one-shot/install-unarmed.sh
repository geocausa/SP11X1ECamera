#!/usr/bin/env bash
# E004jg: stage ONE isolated virtual-only V4L2 candidate, never activate.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004jg-virtual-rear-device-offline-one-shot
TMP=/tmp/sp11-e004jg-loopback-source-20260920
MODULE_SRC=$TMP/source/v4l2loopback/v4l2loopback.ko
DEB=$TMP/v4l2loopback-source_0.15.3-1ubuntu2_all.deb
RECEIVER_SRC=$R/experiments/E004-front-ir-vd55g0/e004je-rear-live-appsrc-bridge/nv12-appsrc-consumer.py
D=/var/lib/sp11-camera-e004jg
BOOT=/boot/sp11-7.1.5-e004jg-virtual-rear
ENTRY=/etc/grub.d/99zzzzzz_sp11_e004jg_virtual_rear
UNIT=/etc/systemd/system/sp11-e004jg-virtual-rear.service
RUNNER=/usr/local/sbin/sp11-e004jg-virtual-rear-run-once
ID=sp11-e004jg-virtual-rear-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]] || { echo E004JG_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process --stage-free e004jg
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$D" && ! -e "$BOOT" && ! -e /dev/video90 ]]
for file in "$ENTRY" "$UNIT" "$RUNNER"; do sudo -n test ! -e "$file"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sha256sum "$DEB" | awk '{print $1}')" == 007a2aa9a723976318407c871b2f1ecdbcd3dc065bf482b0b86f03b026ef40e0 ]]
[[ -f "$MODULE_SRC" && ! -L "$MODULE_SRC" ]]
[[ "$(sha256sum "$MODULE_SRC" | awk '{print $1}')" == 2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1 ]]
[[ "$(modinfo -F vermagic "$MODULE_SRC")" == '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ]]
[[ "$(modinfo -F license "$MODULE_SRC")" == GPL ]]
[[ "$(sha256sum "$RECEIVER_SRC" | awk '{print $1}')" == 9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613 ]]
bash -n "$H/run-once.sh" "$H/arm-once.sh" "$H/retire-after-golden.sh"
tail -n +3 "$H/99zzzzzz_sp11_e004jg_virtual_rear" | grub-script-check
# Only a separately identified and root-private copy of the unused module;
# no module install, auto-load, /lib/modules mutation or Golden DTB change.
sudo -n mkdir -m 0700 "$D"
sudo -n install -m 0644 "$MODULE_SRC" "$D/v4l2loopback.ko"
sudo -n install -m 0600 "$RECEIVER_SRC" "$D/nv12-appsrc-consumer.py"
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == 2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1 ]]
[[ "$(sudo -n sha256sum "$D/nv12-appsrc-consumer.py" | awk '{print $1}')" == 9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613 ]]
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-e004jg-virtual-rear.service" "$UNIT"
sudo -n systemd-analyze verify "$UNIT"
sudo -n mkdir -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-e004jg-virtual-rear"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb "$BOOT/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb"
sudo -n install -m 0755 "$H/99zzzzzz_sp11_e004jg_virtual_rear" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-e004jg-virtual-rear.service
sudo -n update-grub > "$TMP/UPDATE-GRUB.log"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n systemctl is-enabled sp11-e004jg-virtual-rear.service)" == enabled ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemctl is-active --quiet sp11-e004jg-virtual-rear.service && exit 1 || :
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004JG_INSTALLED=PASS ARMED=NO LOOPBACK_NOT_LOADED=YES GOLDEN_DEFAULT=UNCHANGED AUTO_RETURN=ENABLED
