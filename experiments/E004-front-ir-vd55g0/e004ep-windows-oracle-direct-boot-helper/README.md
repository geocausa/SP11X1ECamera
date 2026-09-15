# E004ep — direct Windows oracle one-shot helper

E004em exposed a boot-path trap on this SP11: the firmware entry labelled `Windows Boot Manager` points to Ubuntu GRUB, while the existing `Windows Direct Oracle Temp` entry points directly to `EFI/Microsoft/Boot/bootmgfw.efi` and reliably reaches the Windows oracle.

`tools/sp11-camera-windows-oracle-oneshot.sh` canonicalizes that distinction. It requires Golden Linux, clean camera overlap, HEAD==origin, Golden as the saved GRUB entry and no pending GRUB `next_entry`. It discovers exactly one `Windows Direct Oracle Temp` entry by both name and Microsoft EFI path instead of pinning the numeric boot ID. `--check-only` is non-mutating. `--reboot` sets only UEFI `BootNext`, verifies persistent `BootOrder` is unchanged, then reboots. It never changes the persistent firmware boot order or GRUB saved default.
