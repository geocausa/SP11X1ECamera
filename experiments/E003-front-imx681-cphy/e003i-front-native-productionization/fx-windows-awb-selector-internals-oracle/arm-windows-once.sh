#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/fx-windows-awb-selector-internals-oracle
fail(){ echo "FAIL: $*" >&2; exit 1; }
PYTHONDONTWRITEBYTECODE=1 "$D/verify-fx.py" >/dev/null
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e003-front-imx681-cphy)" ] || fail origin
git -C "$R" diff --quiet || fail dirty
git -C "$R" diff --cached --quiet || fail staged
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list); grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$ENV" || fail saved; ! grep -q '^next_entry=.' <<<"$ENV" || fail next
for m in qcom_camss imx681 ov13858; do [ ! -d /sys/module/$m ] || fail module_$m; done
EFI=$(sudo -n efibootmgr); grep -q '^Boot0006.*Windows Direct Oracle Temp' <<<"$EFI" || fail boot0006; ! grep -q '^BootNext:' <<<"$EFI" || fail bootnext
printf 'schema=sp11-e003i-fx-preboot-v1\nstatus=PREARM_WINDOWS_SELECTOR_ORACLE\ntime=%s\nhead=%s\n' "$(date -Ins)" "$(git -C "$R" rev-parse HEAD)" > "$D/PREBOOT-LINUX.txt"
sudo -n efibootmgr -n 0006 >/dev/null
sudo -n efibootmgr | grep -q '^BootNext: 0006' || fail arm
printf 'schema=sp11-e003i-fx-armed-v1\nstatus=ARMED_ONE_SHOT_DIRECT_WINDOWS\ntime=%s\nhead=%s\n' "$(date -Ins)" "$(git -C "$R" rev-parse HEAD)" > "$D/ARMED-WINDOWS.txt"
sync
echo FX_WINDOWS_BOOTNEXT=0006 ARMED_ONCE
