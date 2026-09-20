# E004il — staged V4L2 NV12 negotiation, streaming forbidden until ISP proof

Date: 2026-09-20. Parent: `610a11f`. SP11 Linux, protected Golden.
Status: **OFFLINE ARM64 KERNEL BUILD PASS. NO LIVE NV12 CAMERA.**

## Engineering result

A separate, exact-source-locked overlay now adds an alternate
`V4L2_PIX_FMT_NV12` entry **after** the current default QC10C entry in
the X1E80100 IFE1 PIX V4L2 format table only. It gives the alternate
the specifically proposed 2560x1440, 2560-byte stride, single-memory-
plane, 5,529,600-byte geometry, including discrete frame-size
enumeration and exact `TRY_FMT`/`S_FMT` handling.

The established QC10C default, 3584-byte stride, 0x76b000-byte
compressed allocation, camera workflow and every existing production
source file are untouched. Other SoC and RDI/lite NV12 formats remain
separate. The existing video allocator's single-memory-plane NV12
chroma address arithmetic is retained without modification.

**The alternate cannot stream:** `video_prepare_streaming` returns
`-EOPNOTSUPP` on IFE1 PIX NV12 *before* V4L2 media-pipeline
power-up. A second check in `video_start_streaming` returns
`-EOPNOTSUPP` before allocating a media pipeline or calling the
accepted QC10C runner. The staged source does not add a register
write or change original VFE680 BUS code. The earlier kernel-native
Y/UV address planner (E004ik) remains separate and is not referenced
by this format-only overlay; no premature end-to-end activation is
claimed.

## Repeatable build and negative regressions

Run in the accepted repository on SP11 Golden:

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004il-nv12-v4l2-negotiation \
  -p 'test_source_contract.py' -v
bash experiments/E004-front-ir-vd55g0/e004il-nv12-v4l2-negotiation/build-offline.sh
```

The script verifies SHA-256 of three accepted source files, copies
CAMSS to a unique disposable /tmp directory and makes its exact
format-only changes *there*. An independently checked source audit
rejects default-format replacement, corrupted geometry, missing
pre-power or pre-pipeline stream rejection, changes to the accepted
VFE680 MMIO implementation, and newly inserted MMIO writes. Seven
test cases PASS on SP11. The full `qcom-camss.ko` builds successfully
for the actual running Golden v4 ABI:

`1a7f88953eb9f7c170993514d197e9dd2cfcda7036823fd9f20db2543c1b4590`

This is an **uninstalled build hash**, NOT a deployed or running
module, nor empirical proof of `VIDIOC_ENUM_FMT` on a real new
device. The disposable build is deleted automatically. Original
camera nodes are absent and Golden remains unchanged.

## Why hardware activation is still forbidden

Qualcomm's public BUS ver3 provides a separate NV12 FULL Y/C packer
configuration and uncompressed per-client frame increments, but its
normal NV12 path alone does not clear previous compression state.
The exact SP11-specific uncompressed VFE1 FULL Y/C configuration,
UBWC state initialization/reset, 10->8-bit format/colourimetry
semantics and full auxiliary/AEC/IRQ lifecycle are not yet verified.
The Windows-recorded internal 2560x1440 QC10C output is **not**
interchangeable with the 1920x1080 NV12 selected by an application;
the E004ij offline GStreamer bridge only accepts independently
verified linear NV12, never compressed QC10C.

Read-only static Ghidra inspection of the archived, SHA-pinned
`QcDeviceMFT8380.dll` (SHA-256
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`)
also found code references to both LINEAR_NV12 and UBWC_TP10
validation strings and to IPE application/video output checks.
Those references belong to validation/configuration paths; they
do **not** prove which Windows conversion route executed, nor
authorize importing the original proprietary binary into the
repository. No fresh Windows boot or KD trace was necessary for
this offline checkpoint.

## Next gated action

Derive the SP11-specific safe *fresh-state* linear ISP/BUS recipe
and explicit compression-clear/restore authority, then integrate
the E004ik DMA-planner, E004il V4L2 format negotiation and existing
bounded camera runner behind a **new non-default, one-shot**
experiment. Only after clean live pixels and lifecycle should the
1920x1080 E004ij bridge attach to real output. IR illumination,
protected signing/auth and PAM remain separate and disabled.
