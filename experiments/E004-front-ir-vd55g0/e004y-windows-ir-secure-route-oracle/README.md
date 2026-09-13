# E004y — same-machine Windows IR secure-route oracle

E004y resolves the question that blocked E004x: **Windows does not send the Surface IR Camera Front stream through the observable standard CAMSS CSID/VFE route.**

## What was captured

SP11 was booted one-shot into Windows while SP7 KDNET captured the camera hardware. The selected WinRT source was exactly:

- `Surface IR Camera Front`
- SourceKind: `Infrared`
- stream: `VideoPreview`
- output: NV12 644x604 at 60 fps

The stronger second holder did not merely call `StartAsync()`. It repeatedly called `TryAcquireLatestFrame()` and successfully acquired **12 real frames** before KD froze the machine for LIVE2.

Both runs stopped cleanly. SP11 then returned to unchanged Golden Linux.

## Standard CAMSS result

KD captured these ordinary camera blocks:

- CSID wrapper: `0x0acb6000`, 4 KiB
- CSID0: `0x0acb7000`, 8 KiB
- CSID1: `0x0acb9000`, 8 KiB
- CSID2: `0x0acbb000`, 8 KiB
- VFE0: `0x0ac62000`, 16 KiB sampled
- VFE1: `0x0ac71000`, 16 KiB sampled

LIVE1 (reader started) and LIVE2 (12 actual frames acquired) are byte-identical across every captured standard block.

The wrapper values are:

- CSID0 IO_PATH_CFG0 = `0x00000001`
- CSID1 IO_PATH_CFG0 = `0x00000001`
- CSID2 IO_PATH_CFG0 = `0x00000001`

No instance sets bit 8 `OUTPUT_IFE_EN`.

Each IR CSID has exactly the same full 8 KiB image as the already-known Windows **inactive/default** CSID0 image from E003g:

`f4cdd9594c9e63600c087a6bc653ebce05468e1d6ce0f9a20b7d10cd81afc60a`

VFE0 and VFE1 are completely zero while those real IR frames are being delivered.

After each clean stop, every captured standard block becomes the powered-off/inaccessible `0x80000000` sentinel image.

Therefore the earlier Linux idea `CSIPHY0 -> CSID0 RDI0` is **not a Windows parity route**. It could still be useful later as a deliberately labeled diagnostic Linux transport path, but it cannot be accepted as 1:1 Windows behavior.

## SecureISP finding

Windows identifies another camera device:

- service: `CameraSecureISP`
- driver: `qccamsecureisp8380.sys`
- ACPI instance: `ACPI\QCOM0CCC\19`
- description: `Qualcomm(R) Spectra(TM) 395 SecureISP Device`
- status: Started
- IRQs: 392 and 391
- physical memory: `0x0acca000..0x0accdfff` (16 KiB)

During the real-frame LIVE2 state, `qccamsecureisp8380.sys` and `surfacecamavs8380.sys` were loaded.

KD could not read `0x0acca000` either normally or with explicit uncached `[uc]` physical access while the 12 real IR frames were flowing. That protected aperture is consistent with a secure camera path, but the exact internal SecureISP route is **not** inferred from that fact.

## What this proves — and what it does not

Proved:

1. real Surface IR frames are delivered under Windows;
2. normal observable CSID0/1/2 remain in their exact inactive/default state;
3. normal VFE0/1 remain completely inactive;
4. the Spectra 395 SecureISP device is Started and its driver is live;
5. its physical aperture is protected from KD reads;
6. teardown is clean and reproducible.

Not proved:

- exact SecureISP register state;
- its internal CSI/ISP routing;
- secure-world firmware behavior;
- the host↔secure command ABI;
- whether Linux can reproduce the protected route.

Those are the next static reverse-engineering gates.

## Safety state

The Windows boot was one-shot. Current Linux is back on Golden:

- kernel `7.1.5-sp11-render-parity-v4+`
- saved GRUB entry `sp11-audio-fullio-v19c`
- empty `next_entry`
- no camera/CAMSS modules
- no `/dev/media*` or `/dev/video*`

No Linux CSID or SecureISP runtime was attempted in E004y.
