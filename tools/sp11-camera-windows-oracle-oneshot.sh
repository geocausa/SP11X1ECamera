#!/usr/bin/env bash
set -euo pipefail

R=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
MODE=${1:---check-only}
case "$MODE" in
  --check-only|--reboot) ;;
  *) echo "usage: $0 [--check-only|--reboot]" >&2; exit 2 ;;
esac

fail(){ echo "SP11_WINDOWS_ORACLE_ONESHOT=FAIL $*" >&2; exit 1; }

"$R/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process >/dev/null || fail overlap_guard
[ "$(git -C "$R" rev-parse HEAD)" = "$(git -C "$R" rev-parse origin/experiment/e004-front-ir-vd55g0)" ] || fail head_not_origin

GRUB=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null || true)
grep -qx 'saved_entry=sp11-audio-fullio-v19c' <<<"$GRUB" || fail saved_entry_not_golden
! grep -q '^next_entry=.' <<<"$GRUB" || fail grub_next_entry_already_set

EFI=$(sudo -n efibootmgr -v)
mapfile -t MATCHES < <(printf '%s\n' "$EFI" | grep -E '^Boot[0-9A-Fa-f]{4}\*?[[:space:]]+Windows Direct Oracle Temp' | grep -F '\EFI\Microsoft\Boot\bootmgfw.efi' || true)
[ "${#MATCHES[@]}" -eq 1 ] || fail direct_windows_entry_count_${#MATCHES[@]}
BOOTNUM=$(sed -E 's/^Boot([0-9A-Fa-f]{4}).*/\1/' <<<"${MATCHES[0]}")
[[ "$BOOTNUM" =~ ^[0-9A-Fa-f]{4}$ ]] || fail invalid_bootnum
BOOTORDER_BEFORE=$(sed -n 's/^BootOrder: //p' <<<"$EFI" | head -1)
[ -n "$BOOTORDER_BEFORE" ] || fail no_bootorder

printf 'SP11_WINDOWS_ORACLE_DIRECT_ENTRY=PASS BOOT=%s PATH=EFI/Microsoft/Boot/bootmgfw.efi\n' "$BOOTNUM"
printf 'SP11_WINDOWS_ORACLE_BOOTORDER=%s\n' "$BOOTORDER_BEFORE"

if [ "$MODE" = --check-only ]; then
  echo 'SP11_WINDOWS_ORACLE_ONESHOT=PASS CHECK_ONLY=YES MUTATED=NO'
  exit 0
fi

sudo -n efibootmgr -n "$BOOTNUM" >/dev/null
EFI_AFTER=$(sudo -n efibootmgr)
BOOTORDER_AFTER=$(sed -n 's/^BootOrder: //p' <<<"$EFI_AFTER" | head -1)
BOOTNEXT=$(sed -n 's/^BootNext: //p' <<<"$EFI_AFTER" | head -1)
[ "$BOOTORDER_AFTER" = "$BOOTORDER_BEFORE" ] || fail bootorder_changed
[ "${BOOTNEXT^^}" = "${BOOTNUM^^}" ] || fail bootnext_not_direct_windows
printf 'SP11_WINDOWS_ORACLE_ONESHOT=PASS ARMED=YES BOOTNEXT=%s BOOTORDER_UNCHANGED=YES GOLDEN_PERSISTENT=YES\n' "$BOOTNUM"
sync
sudo -n systemctl reboot --no-block
