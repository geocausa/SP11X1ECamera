# SP11 retired camera boot cleanup — 2026-09-10

This checkpoint preserves the exact custom camera GRUB scripts and a file/size inventory of every retired `/boot/sp11-*-camera-*` bundle immediately before cleanup.

Scope is intentionally narrow: remove custom camera/E002/E003 boot-menu scripts and their duplicate boot bundles only. Keep the saved Golden Linux entry and bundle, Windows discovery, normal distro entries, firmware settings, and all Git experiment/source history.

The bulky boot binaries are not copied into Git: they are disposable experiment products and are reconstructible from their experiment sources/scripts. `GRUB-ENTRY-SNAPSHOT.txt` preserves the exact menu scripts that selected them.
