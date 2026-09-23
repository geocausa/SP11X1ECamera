# E004nm — same-SP11 rear-native Windows ISP oracle (new session)

Initiated from verified Golden Linux `7.1.5-sp11-render-parity-v4+`, saved GRUB `sp11-audio-fullio-v19c`, 2026-09-23, active experiment branch prior HEAD `9b3fe125ff786ead0dbd1497eab860600d2e365c`. This experiment is **not** a reuse of an earlier consumed Windows/GRUB one-shot. Source-only E004nk and E004nl establish: front hardware VFE1 PIX 27 QC10C 2560×1440 frames proven; rear source 4076×2806 GRBG OV13858 D-PHY CSID0->VFE0 RDI0 RAW proven; Windows OEM outputs rear 3840×2160 NV12 VideoRecord but Linux rear VFE0 PIX physical frame unproven.

## Existing Windows static authority, read in place

`STATIC-ORACLE-READONLY.txt` records SHA256 and general kernel driver import/diagnostic observations from the **same SP11** Windows NTFS partition mounted with `ntfs-3g -o ro,norecover` and later unmounted. No binary, firmware, image/pixel/RAW/photo/hash or private Windows token was copied to this repo or another machine. The Windows ARM64 qccamisp8380 driver contains IFE/CSID packet management plus ICP/BPS/IPE paths, but this is **generic code**, not proof of active rear video hardware resource or output layout.

## One-time Windows boot + exact recovery

- Before every boot mutation: exact HEAD and live origin branch match, tracked clean, `camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process` PASS, and `tools/sp11-camera-windows-oracle-oneshot.sh --check-only` PASS.
- EFI Boot0006 is the verified DIRECT Windows `EFI/Microsoft/Boot/bootmgfw.efi`; Boot0004 labeled Windows Boot Manager is actually GRUB and must never be used as Windows oracle. `BootNext=0006` is ONE-TIME. Persistent EFI BootOrder remains Linux Boot0005 first, GRUB Golden v19c saved/default and empty next entry. No persistent boot/default/kernel/audio modification.
- Before Windows remote work verify live Windows native HostFabric agent `DESKTOP-AQ4SMTC` or Windows PiMaster and host/session identity, then start a bounded Windows watchdog **reboot** back to Linux Golden. If live agent unavailable, rely on SP7 KD/Windows network troubleshooting; do not invent a successful Windows session or repeatedly rearm.
- Optical data stays user-private on SP11 Windows. Do not write images/pixels/RAW/thumbs/spatial hashes to Git, Fabric, chat or SP7. Do not activate IR/Hello, flash ICP firmware, alter high-quality photo/normal video default camera profile, or attempt Linux OS suspend.
- Need direct Windows rear `VideoRecord` 3840×2160 (NV12), compare `VideoPreview` 1920×1080 and still/high-quality-photo as **distinct** modes. Dynamically determine which CSID/IFE resource, VFE0+CSID0 MMIO inputs, crop, output bytes/planes/FULL WM, IRQs, stats, IQ/RT-CDM, and ICP path are actually active, without equating host NV12 software buffers to hardware QC10C surfaces. Only evidence-backed scalars and metadata enter `RESULT.json`.
- On Windows reboot verify SP11 is back on protected Golden, Linux Wi-Fi/HostFabric reachable, EFI BootNext consumed, complete no-camera/IR guard, and Git head tracking origin.

**Status:** Windows dynamic mode/ISP evidence pending; static facts in `STATIC-ORACLE-READONLY.txt` are not rear native Linux ISP success.
