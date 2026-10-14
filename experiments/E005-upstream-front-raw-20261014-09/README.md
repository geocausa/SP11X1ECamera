# Fresh standard RAW RDI qualification 09
Reuse 08 recovery/package/observer and hardware-qualified PHY31/DT29/kernel26.
Only CAMSS32 changes. Reuse E004kg matched CSID1/VFE1 route and v4l2-ctl
metadata grammar; current standard sensor mode is 3840x2640, distinct from
native 2160 timing. No repeat of consumed identities and no FPS assumption.
Three planned eight-frame MMAP sessions, stop/close/reopen, each bounded.
Exact full-plane/sequence/timestamp metadata, complete 18-signature kernel
guard and power/rail/clock/reset release required before advancing/unloading.
Any failure skips route mutation/unload and triggers automatic Golden return.
Pixels are discarded by standard v4l2-ctl on SP11; no pixel files/hashes/export.
One-use boot, separate immutable module tree, independent 180-second watchdog.
This cannot establish optical IQ, ISP/libcamera/IPA parity or full fault matrix.
