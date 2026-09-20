#!/usr/bin/env bash
# E004iy: remove ONLY this service-order drop-in. Does not reboot or repair GRUB.
set -Eeuo pipefail
umask 077
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
T=$R/experiments/E004-front-ir-vd55g0/e004iy-grub-writer-order-reversible
ROOT=/var/lib/sp11-camera-e004iy
SERVICE=/etc/systemd/system/grub2-common.service.d
DROP=$SERVICE/90-sp11-serialize-grubenv-writers.conf
cd "$R"
./tools/camera-overlap-guard.sh --require-golden --require-no-camera-process
sudo -n test -f "$ROOT/grubenv-before.bin"
sudo -n test -f "$DROP"
sudo -n cmp --silent "$T/90-sp11-serialize-grubenv-writers.conf" "$DROP"
[[ "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^saved_entry=//p')" == sp11-audio-fullio-v19c ]]
[[ -z "$(sudo -n grub-editenv /boot/grub/grubenv list | sed -n 's/^next_entry=//p')" ]]
sudo -n rm -f -- "$DROP"
sudo -n rmdir -- "$SERVICE"
sudo -n systemctl daemon-reload
[[ "$(systemctl show grub2-common.service -p DropInPaths --value)" == "" ]]
! systemctl show grub2-common.service -p After --value | grep -q 'grub-initrd-fallback.service'
sudo -n grub-editenv /boot/grub/grubenv list | grep -qx 'saved_entry=sp11-audio-fullio-v19c'
sudo -n grub-editenv /boot/grub/grubenv list | grep -qx 'next_entry='
# Historical boot-environment snapshot has no reason to remain on disk.
[[ "$ROOT" == /var/lib/sp11-camera-e004iy ]]
sudo -n rm -rf -- "$ROOT"
./tools/camera-overlap-guard.sh --require-golden --require-no-camera-process
echo E004IY_BOOT_SERVICE_DROPIN_REMOVED_GOLDEN_DEFAULT_PRESERVED=PASS
