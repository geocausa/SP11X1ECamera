# E004dx — offline install/update/remove lifecycle

Status: **PASS / DISPOSABLE ROOT ONLY / LIVE ROOT UNTOUCHED**.

E004dw proved deterministic whole-stack staging. E004dx adds bounded filesystem lifecycle tooling and exercises it only against a disposable root under `/tmp`.

The installer verifies the staged package manifest before copying. It hard-refuses destination `/`. A previous managed install is updated by deleting only files listed in its prior managed manifest, then writing the new managed tree. It records install state under the disposable root's `var/lib/sp11-camera-stack` and does not create boot, initramfs, modprobe, modules-load, systemd, udev or kernel-module activation state.

Acceptance covered a fresh install, verification, same-package update/reinstall, a tampered-package negative test, bounded uninstall, preservation of unrelated `/etc` and `/var/local` sentinel files, and explicit refusal of live-root install/uninstall.

The uninstall path removes only files enumerated by the managed manifest and prunes empty directories only inside package-owned roots. It never recursively removes unrelated trees.

No camera runtime, module load, GRUB change, SecureISP action or protected-memory action occurred.
