# E004jp — uniquely bounded synthetic 4K standard V4L2 webcam gate

2026-09-20. Parent `2327ba4`. This experiment advances the E004jm/jn **offline** rear 4K NV12/application result. E004jg previously proved a **synthetic 1080p** standard /dev/video90 endpoint, and E004jh a separate **real-optical 1080p** temporary rear endpoint; neither verified the virtual device's 3840×2160 NV12 format, independent V4L2 capture or 4K application delivery.

## Strict scope and protected Golden state

The E004jp candidate is **synthetic-only**: uses original protected Golden kernel, initrd AND original noncamera DTB in a separately named one-use GRUB entry, loads only a locally rebuilt/gpl v4l2loopback module into the candidate boot and an NV12 3840×2160 GStreamer ball-pattern publisher, then requires a separate ordinary V4L2 reader to obtain eight complete 12,441,600-byte 4K NV12 frames and deliver them into the independently tested E004jn 4K GStreamer appsrc→I420 appsink application. **No camera sensors, IR illumination, protected front buffers, optical pixels, OEM camera module or camera-enabled DTB** are used. This does not prove a live rear 4K camera or any front camera pixel conversion.

Module source is uninstalled Ubuntu arm64 `v4l2loopback-source` **0.15.3-1ubuntu2**, .deb SHA-256 `007a2aa9a723976318407c871b2f1ecdbcd3dc065bf482b0b86f03b026ef40e0`, downloaded and extracted only to private `/tmp/sp11-e004jp-loopback-src.Yidxms` and built offline against the exact running SP11 custom Golden-v4 kernel ABI, without installing anything into `/lib/modules`. This fresh module's SHA-256 is `305faddd6082eb1f460fe78954abe5c2ede90b4d823f7cb21f56c76d6bd22b3c`, GPL and correct vermagic. The separate E004jn 4K application receiver SHA-256 is `813d6ad77f5b936955df178c4b426c3c3844d6d640f4377dd7196b5f1fba96a5`. Candidate refuses source drift, unpinned staged bytes, stale GRUB next_entry, active camera nodes/processes, overlapping drivers, previous consumed identity and failed GRUB writer sequencing.

The one-shot identifier `sp11-e004jp-virtual-rear-4k-one-shot` is NEW; neither E004jg nor E004jh consumed entries may be reused. Its systemd runner is conditional on E004jp's unique cmdline, bounded to 210s, and unconditionally requests reboot to saved Golden after exit or timeout. The runner removes the isolated module/device before reboot. The persistent saved entry remains `sp11-audio-fullio-v19c`; no default kernel/DTB/initrd is overwritten or camera/IR module installed. Evidence from a consumed candidate must be redacted and all its root-private staging/boot files retired after Golden return. No optical or synthetic NV12 output files may be retained.

## Pre-run status

A new candidate source set has six automated static/shell/GRUB format, safety, identity, module-hash and 4K format-contract tests PASS. This is **not** a real one-shot result. The source and boot files are intended for a new isolated synthetic-only candidate; do not mark 4K webcam capability PASS until the actual standard /dev/video90 4K capture/consumer returns eight frames and post-return Golden cleanup is independently verified.

## After hardware-free 4K endpoint verification

Only then prepare a separately NEW unique physical rear camera one-shot, with exact E004jd R4-complete package/guard provenance and automatic Golden return, to connect actual OV13858 normal-scene 4076×2806 packed Bayer→E004jm 3840×2160 NV12→standard 4K V4L2 virtual webcam→independent 4K application. Different real frames and sustained sensor/V4L2 cadence, thermal/latency, AE/AWB and Windows image-quality matching are not supplied by synthetic publisher tests. Front QC10C decoding and safe 1080p linear output remain independently blocked; IR/Hello can remain outside parity scope.
