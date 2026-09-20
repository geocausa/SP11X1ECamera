#!/usr/bin/env bash
# E004jp: stage ONE isolated virtual-only V4L2 candidate, never activate.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
H=$R/experiments/E004-front-ir-vd55g0/e004jp-4k-synthetic-v4l2-one-shot
TMP=/tmp/sp11-e004jp-loopback-src.Yidxms
MODULE_SRC=$TMP/build/modules/v4l2loopback/v4l2loopback.ko
DEB=$TMP/v4l2loopback-source_0.15.3-1ubuntu2_all.deb
RECEIVER_SRC=$R/experiments/E004-front-ir-vd55g0/e004jn-rear-4k-appsrc-offline/nv12-4k-appsrc-consumer.py
D=/var/lib/sp11-camera-e004jp
BOOT=/boot/sp11-7.1.5-e004jp-virtual-rear
ENTRY=/etc/grub.d/99zzzzzz_sp11_e004jp_virtual_rear_4k
UNIT=/etc/systemd/system/sp11-e004jp-virtual-rear-4k.service
RUNNER=/usr/local/sbin/sp11-e004jp-virtual-rear-4k-run-once
ID=sp11-e004jp-virtual-rear-4k-one-shot
cd "$R"
[[ ! -e "$H/evidence/PRE-CAMERA-ABORT.json" ]] || { echo E004JP_IDENTITY_CONSUMED_DO_NOT_REARM >&2; exit 1; }
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process --stage-free e004jp
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$D" && ! -e "$BOOT" && ! -e /dev/video90 ]]
for file in "$ENTRY" "$UNIT" "$RUNNER"; do sudo -n test ! -e "$file"; done
! sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ ! -d /sys/module/v4l2loopback ]]
[[ "$(sha256sum "$DEB" | awk '{print $1}')" == 007a2aa9a723976318407c871b2f1ecdbcd3dc065bf482b0b86f03b026ef40e0 ]]
[[ -f "$MODULE_SRC" && ! -L "$MODULE_SRC" ]]
[[ "$(sha256sum "$MODULE_SRC" | awk '{print $1}')" == 305faddd6082eb1f460fe78954abe5c2ede90b4d823f7cb21f56c76d6bd22b3c ]]
[[ "$(modinfo -F vermagic "$MODULE_SRC")" == '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ]]
[[ "$(modinfo -F license "$MODULE_SRC")" == GPL ]]
[[ "$(sha256sum "$RECEIVER_SRC" | awk '{print $1}')" == 813d6ad77f5b936955df178c4b426c3c3844d6d640f4377dd7196b5f1fba96a5 ]]
bash -n "$H/run-once.sh" "$H/arm-once.sh" "$H/retire-after-golden.sh"
tail -n +3 "$H/99zzzzzz_sp11_e004jp_virtual_rear_4k" | grub-script-check
# Only a separately identified and root-private copy of the unused module;
# no module install, auto-load, /lib/modules mutation or Golden DTB change.
sudo -n mkdir -m 0700 "$D"
sudo -n install -m 0644 "$MODULE_SRC" "$D/v4l2loopback.ko"
sudo -n install -m 0600 "$RECEIVER_SRC" "$D/nv12-4k-appsrc-consumer.py"
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$D/EXPECTED-HEAD" >/dev/null
[[ "$(sudo -n sha256sum "$D/v4l2loopback.ko" | awk '{print $1}')" == 305faddd6082eb1f460fe78954abe5c2ede90b4d823f7cb21f56c76d6bd22b3c ]]
[[ "$(sudo -n sha256sum "$D/nv12-4k-appsrc-consumer.py" | awk '{print $1}')" == 813d6ad77f5b936955df178c4b426c3c3844d6d640f4377dd7196b5f1fba96a5 ]]
sudo -n install -m 0700 "$H/run-once.sh" "$RUNNER"
sudo -n install -m 0644 "$H/sp11-e004jp-virtual-rear-4k.service" "$UNIT"
sudo -n systemd-analyze verify "$UNIT"
sudo -n mkdir -m 0755 "$BOOT"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+ "$BOOT/vmlinuz-7.1.5-sp11-render-parity-v4+"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c "$BOOT/initrd.img-7.1.5-sp11-e004jp-virtual-rear-4k"
sudo -n install -m 0644 /boot/sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb "$BOOT/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb"
sudo -n install -m 0755 "$H/99zzzzzz_sp11_e004jp_virtual_rear_4k" "$ENTRY"
sudo -n systemctl daemon-reload
sudo -n systemctl enable sp11-e004jp-virtual-rear-4k.service
sudo -n update-grub > "$TMP/UPDATE-GRUB.log"
sudo -n grep -Fq "$ID" /boot/grub/grub.cfg
[[ "$(sudo -n systemctl is-enabled sp11-e004jp-virtual-rear-4k.service)" == enabled ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n test ! -e "$D/ATTEMPT-CONSUMED"
sudo -n systemctl is-active --quiet sp11-e004jp-virtual-rear-4k.service && exit 1 || :
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
echo E004JP_INSTALLED=PASS ARMED=NO LOOPBACK_NOT_LOADED=YES GOLDEN_DEFAULT=UNCHANGED AUTO_RETURN=ENABLED
