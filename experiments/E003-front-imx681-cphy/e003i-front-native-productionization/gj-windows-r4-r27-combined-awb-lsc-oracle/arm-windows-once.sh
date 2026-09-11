#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/gj-windows-r4-r27-combined-awb-lsc-oracle
fail(){ echo "FAIL: $*" >&2; exit 1; }

PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify-gj.py" >/dev/null
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin_mismatch
git -C "$R" diff --quiet || fail tracked_dirty
git -C "$R" diff --cached --quiet || fail staged

ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved
! grep -q '^next_entry=.' <<<"$ENV" || fail grub_next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail "module_$m"; done
test -z "$(ls /dev/video* /dev/media* 2>/dev/null || true)" || fail camera_nodes

EFI=$(sudo -n efibootmgr)
grep -q '^Boot0006.*Windows Direct Oracle Temp' <<<"$EFI" || fail boot0006
! grep -q '^BootNext:' <<<"$EFI" || fail existing_bootnext

{
 echo 'schema=sp11-e003i-gj-preboot-v1'
 echo 'status=PREARM_WINDOWS_COMBINED_ORACLE'
 echo "time=$(date -Ins)"
 echo "head=$(git -C "$R" rev-parse HEAD)"
 echo "kernel=$(uname -r)"
 echo 'saved_entry=sp11-audio-fullio-v19c'
 echo 'next_entry='
 echo "$EFI"
} > "$D/PREBOOT-LINUX.txt"

sudo -n efibootmgr -n 0006 >/dev/null
EFI2=$(sudo -n efibootmgr)
grep -q '^BootNext: 0006' <<<"$EFI2" || fail bootnext_not_armed

{
 echo 'schema=sp11-e003i-gj-armed-windows-v1'
 echo 'status=ARMED_ONE_SHOT_DIRECT_WINDOWS'
 echo "time=$(date -Ins)"
 echo "head=$(git -C "$R" rev-parse HEAD)"
 echo "$EFI2"
} > "$D/ARMED-WINDOWS.txt"

sync
echo 'GJ_WINDOWS_BOOTNEXT=0006 ARMED_ONCE GOLDEN_GRUB_PERSISTENT'
