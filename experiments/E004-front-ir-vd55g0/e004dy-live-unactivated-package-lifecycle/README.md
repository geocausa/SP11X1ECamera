# E004dy — live filesystem lifecycle without activation

Status: **PASS / LIVE FILESYSTEM TESTED / ZERO CAMERA ACTIVATION**.

E004dx proved package lifecycle against a disposable root. E004dy then exercised the exact same staged package on the real Golden filesystem because all target product paths were initially absent.

The guarded live installer requires protected Golden, no camera process, no loaded camera modules, no media node and the exact E004dw stack-manifest hash. It installs only package files under `/usr` plus managed state under `/var/lib/sp11-camera-stack`. It contains no boot, initramfs, GRUB, udev, modprobe, modules-load or systemd activation logic.

Acceptance sequence:

- fresh live install + full manifest verification;
- same-package managed update/reinstall + full verification;
- bounded uninstall;
- package-owned live paths absent afterward.

Before install, after install, after update and after uninstall, E004dy hashed Golden kernel/initrd, GRUB state/config and all files under the relevant modprobe, modules-load, systemd, udev and initramfs configuration surfaces. All four snapshots are byte-identical. No camera module loaded and no `/dev/media*` node appeared at any point.

This closes filesystem lifecycle only. It does not make the camera package boot-active or default.
