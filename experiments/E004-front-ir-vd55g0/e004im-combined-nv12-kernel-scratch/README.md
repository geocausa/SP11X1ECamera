# E004im — one combined, non-runnable front-NV12 kernel build

2026-09-20. Parent: `7d65880`. SP11 Linux under protected Golden.
**Offline combined ARM64 module build PASS, no module installed, no physical
camera access, no real NV12 frames.**

## Actual progress

The earlier stages were independent: E004ik compiled an isolated kernel-native
NV12 Y/UV DMA planner; E004il compiled an alternate X1E80100 IFE1 PIX
NV12 V4L2 format-negotiation overlay. This stage merges both overlays
into **one** disposable copy of the accepted CAMSS driver, with strict source
hash checks and the same proposed 2560x1440, stride 2560, allocation
5529600-byte contract.

`make_combined.py` pins the preexisting QC10C source digests and the exact
E004ik planner hash, runs E004il and E004ik independent audits, enforces
both alternate NV12 queue geometry and E004ik DMA geometry, then appends
the unreferenced planner to the isolated VFE680 source file. The accepted
QC10C source files, nine-client compressed BUS path, R27 control path,
front/rear routing, IR worker and Golden boot are **unchanged**.

`build-offline.sh` compiled a complete ARM64 `qcom-camss.ko` against the
actual Golden v4 kernel build workspace from that *combined* scratch tree,
verified both kernel-native planner/authorization symbols and deleted
the temporary module. SHA-256 of the uninstalled combined binary:

`0fc39ecf60fa4bda99a68eff1f8431e7de1ba99784e0523e8a4b955eb1a1420b`.

`test_combined.py`: seven unit/negative tests PASS, including deliberate
tampering of the production default, NV12 geometry, separate planner
call sites, inserted VFE680 register writes, early pre-power STREAMON
rejection and second pipeline-start rejection.

**The NV12 source cannot stream:** the alternate is rejected before pipeline
PM and independently before pipeline start with `-EOPNOTSUPP`; the
kernel-native planner has no runtime caller and its private hardware
authorization returns `-EOPNOTSUPP` unconditionally. Compilation is
*not* evidence of a working video device. No ioctl was made against
the resulting uninstalled module.

## Specific ISP/BUS boundary still open

The Windows SP11 oracle proves VFE1 WM0/1 QC10C 2560x1440 with compressed
TP10 packer 11, 3584-byte stride, Y/C metadata and `MODE_CFG` values
0x23/0x33. Qualcomm's published BUS ver3 NV12 case uses uncompressed
packer 3, halves the C-client row count and uses per-plane
`stride * height` without compressed metadata. These are *different
physical output configurations*, not two labels for the same buffer.

Before enabling a combined candidate, prove **on exact SP11 silicon**:

1. The RAW10-to-8-bit NV12 processing/scaler output is supported, including
   the required RT-CDM/IFE image-processing state, Y/UV ordering and
   colourimetry. Windows application NV12 1920x1080 may instead be
   produced in a later conversion stage; it does not prove uncompressed
   VFE1 FULL output ever occurred.
2. A coherent, version-matched set of WM0/1 image stride, frame increment,
   format/packer, meta-address, bandwidth and compression-mode registers.
   The public BUS driver does not itself clear preexisting compression
   settings when switching to NV12; both FULL clients must have an
   independently validated clean initial state and stop/reset semantics.
3. Separate buffered Y/C DMA + nine-client auxiliary/3A ownership, frame
   completion, short/failed-frame cleanup and bounded non-default
   lifecycle. Do not reuse compressed QC10C offsets or free DMA while
   hardware may still be writing.
4. Only then authorize an independent *one-shot* candidate with Golden
   rollback. Validate actual pixel content before feeding the existing
   E004ij 2560x1440-linear-NV12 -> 1920x1080 desktop bridge.

Neither a different fourcc nor a GStreamer `videoscale` pipeline can
decompress QC10C. Do not arm a new candidate with unproven register values
simply because the two isolated software components now compile together.

## Reproduction on protected Golden (no module installed)

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004im-combined-nv12-kernel-scratch \
  -p 'test_combined.py' -v
bash experiments/E004-front-ir-vd55g0/e004im-combined-nv12-kernel-scratch/build-offline.sh
```

The build uses an exclusive scratch lock, one `mktemp` directory with
automatic deletion, exact parent source digests, and overlap/Golden guards.
It never writes /boot, the installed module directory or camera devices.
