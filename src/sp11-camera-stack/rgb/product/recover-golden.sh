#!/usr/bin/env bash
set -Eeuo pipefail
[[ "$EUID" == 0 ]]
env=$(/usr/bin/grub-editenv /boot/grub/grubenv list)
grep -Fxq 'saved_entry=sp11-audio-fullio-v19c' <<<"$env"
/usr/bin/systemctl stop 'sp11-camera-rgb-publisher@front.service' 'sp11-camera-rgb-publisher@rear.service' || :
/usr/sbin/grub-reboot sp11-audio-fullio-v19c
/usr/bin/sync
/usr/bin/systemctl reboot --no-block
