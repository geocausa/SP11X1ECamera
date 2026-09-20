#!/usr/bin/env bash
# E004iy: install ONLY a removable systemd ordering edge, NEVER arm a boot.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
T=$R/experiments/E004-front-ir-vd55g0/e004iy-grub-writer-order-reversible
ROOT=/var/lib/sp11-camera-e004iy
UNIT=grub2-common.service
SERVICE=/etc/systemd/system/grub2-common.service.d
DROP=$SERVICE/90-sp11-serialize-grubenv-writers.conf
BASE=/usr/lib/systemd/system/grub2-common.service
cd "$R"
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/experiment/e004-front-ir-vd55g0)" ]]
[[ ! -e "$ROOT" ]]
sudo -n test ! -e "$ROOT"
sudo -n test ! -e "$DROP"
sudo -n test ! -e "$SERVICE"
sudo -n test -f "$BASE"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" == "" ]]
[[ "$(systemctl show "$UNIT" -p DropInPaths --value)" == "" ]]
! systemctl show "$UNIT" -p After --value | grep -q 'grub-initrd-fallback.service'
[[ "$(cat /proc/sys/kernel/random/boot_id)" != "" ]]
# Archive the untouched GRUB block and stock unit checksums privately.
sudo -n install -d -m 0700 "$ROOT"
sudo -n cp -- /boot/grub/grubenv "$ROOT/grubenv-before.bin"
sudo -n chmod 0600 "$ROOT/grubenv-before.bin"
sudo -n sha256sum "$ROOT/grubenv-before.bin" | sudo -n tee "$ROOT/grubenv-before.sha256" >/dev/null
sudo -n sha256sum "$BASE" | sudo -n tee "$ROOT/stock-grub2-common.sha256" >/dev/null
git rev-parse HEAD | sudo -n tee "$ROOT/EXPECTED-HEAD" >/dev/null
sudo -n install -d -m 0755 "$SERVICE"
sudo -n install -m 0644 "$T/90-sp11-serialize-grubenv-writers.conf" "$DROP"
sudo -n systemctl daemon-reload
sudo -n systemd-analyze verify "$BASE" /usr/lib/systemd/system/grub-initrd-fallback.service
[[ "$(systemctl show "$UNIT" -p DropInPaths --value)" == "$DROP" ]]
systemctl show "$UNIT" -p After --value | grep -q 'grub-initrd-fallback.service'
systemctl show "$UNIT" -p Wants --value | grep -q 'grub-initrd-fallback.service'
sudo -n cmp --silent /boot/grub/grubenv "$ROOT/grubenv-before.bin"
echo E004IY_REVERSIBLE_WRITER_ORDER_INSTALLED_NO_BOOT_ARMED=PASS
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
