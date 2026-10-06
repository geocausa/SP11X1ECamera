#!/usr/bin/env bash
set -Eeuo pipefail
[[ "$EUID" == 0 ]]
grep -qw 'sp11_camera_rgb_product=1' /proc/cmdline
systemctl stop sp11-camera-rgb.service sp11-camera-rgb-publisher@front.service sp11-camera-rgb-publisher@rear.service || :
grub-reboot sp11-audio-fullio-v19c
sync
echo E012E_RETURN_GOLDEN=ARMED
systemctl reboot --no-block
