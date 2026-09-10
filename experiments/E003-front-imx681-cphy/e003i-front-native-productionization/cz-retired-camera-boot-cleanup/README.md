# SP11 retired camera boot cleanup — 2026-09-10

This checkpoint preserves the exact custom camera GRUB scripts and a file/size inventory of every retired `/boot/sp11-*-camera-*` bundle immediately before cleanup.

Scope is intentionally narrow: remove custom camera/E002/E003 boot-menu scripts and their duplicate boot bundles only. Keep the saved Golden Linux entry and bundle, Windows discovery, normal distro entries, firmware settings, and all Git experiment/source history.

The bulky boot binaries are not copied into Git: they are disposable experiment products and are reconstructible from their experiment sources/scripts. `GRUB-ENTRY-SNAPSHOT.txt` preserves the exact menu scripts that selected them.


## Completed cleanup

Cleanup completed after CY Golden return was verified and its live evidence was committed. All 89 custom camera GRUB scripts and all 83 `/boot/sp11-*-camera-*` bundles were removed, followed by `update-grub`. The generated menu contains zero camera/E002/E003/IMX681/OV13858 experiment entries. The saved Golden entry and Windows Boot Manager remain present.

`AFTER.txt` records the exact post-cleanup state and reclaimed bytes. Git experiment/source history and CY raw runtime captures were not deleted.
