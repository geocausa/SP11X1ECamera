#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -Eeuo pipefail
D=/var/lib/sp11-camera-upstream-front-20261014-06
token=sp11_camera_upstream_front_20261014_06=1
read -r -a words </proc/cmdline
found=0
for word in "${words[@]}"; do
    if [[ "$word" == "$token" ]]; then found=1; fi
done
[[ "$EUID" == 0 && "$found" == 1 ]] || exit 1
# The observer and independent timer may both request a return.
mkdir "$D/RETURN-REQUESTED" 2>/dev/null || exit 0
printf '%s\n' "${SERVICE_RESULT:-independent-watchdog}" >"$D/RETURN-SERVICE-RESULT"
cat /proc/sys/kernel/random/boot_id >"$D/RETURN-BOOT-ID"
dmesg >"$D/PRIVATE-RETURN-DMESG.txt" || true
if ! grub-reboot sp11-audio-fullio-v19c >"$D/RETURN-GRUB.log" 2>&1; then
    # Candidate next_entry has already been consumed by GRUB; saved default
    # remains Golden. Clear a stale next entry before returning.
    grub-editenv /boot/grub/grubenv unset next_entry >>"$D/RETURN-GRUB.log" 2>&1 || true
fi
sync
systemctl reboot --no-block
