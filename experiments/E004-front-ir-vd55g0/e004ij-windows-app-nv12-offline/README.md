# E004ij — reconcile Windows application-format evidence and test offline RGB bridge

2026-09-20, parent `058661f`. SP11 Linux FullIO v19c Golden. No camera
runtime, Windows boot, KD, install, GPU driver mutation, IR illumination
or production-source modifications.

## Resolution: three distinct proven/observed stages

1. Same-machine Windows IMX681 sensor selected mode2:
   `3840x2160 RAW10 @30 fps` (E003h mode-selection oracle).
2. Same-machine Windows VFE1 FULL processed BUS image:
   `2560x1440 TP10-UBWC/QC10C` (E003h VFE1 FULL oracle).
3. **Previously overlooked same-machine Windows WinRT application holder:**
   `Surface Camera Front / Color / VideoRecord / NV12 / 1920x1080`.
   The holder initialized, selected this source, created the reader and
   received `E003H_START_STATUS=Success`.

The third result is already preserved in the original **Windows connector**
output `experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-vfe1-cgc-cold-path/HOLDER-SUCCESS.txt`, SHA-256
`c3482698b31668771a8ad531455cd03b31e26793063415a9df0444cae8707d02`.
It was a **custom WinRT VideoRecord reader**, not a proof of what resolution
the stock Windows Camera UI defaults to, and not a byte-exact comparison of
captured application pixels. Nevertheless it is an actual selected,
successful, app-facing Windows NV12 format — not an imagined resolution.

The supported model is sensor RAW10 -> compressed internal FULL -> Windows
app NV12. The precise Windows internal-to-app conversion/scaling owner
(DeviceMFT, GPU, etc.) is **not established by this output alone**.

## Native Linux design adjustment

Keep 2560x1440 as the independently known/accepted ISP FULL output geometry
for the separate proposed linear ISP mode. Target a distinct ordinary
Linux desktop output of **1920x1080 NV12** after a correctly produced,
verified uncompressed 2560x1440 frame. Do **not** silently substitute
1920x1080 for the proven internal hardware register dimensions, or claim
the Windows application would receive 2560x1440.

`nv12-desktop-bridge.py` is a fail-closed, **offline-only** userspace
prototype using installed GStreamer `rawvideoparse ! videoscale` and
a downstream 1920x1080/NV12 caps constraint. It requires exactly 1–27
*already-linear* 2560x1440 NV12 input frames and outputs the same count of
3,110,400-byte 1920x1080 NV12 frames into a private /tmp directory only.
It rejects partial/excess frames, invalid counts, input links, occupied
output, inaccessible destination and short GStreamer results without
publishing incomplete output; source file stays unchanged.

**Never feed QC10C compressed buffers into this bridge.** It cannot decode
QC10C or validate actual image colourimetry, range, frame cadence,
sensor optical quality or Windows postprocessing parity.

## Actual SP11 validation

An actual GStreamer 1.28.2 pipeline converted two independently generated
constant-luma, neutral-chroma 2560x1440 NV12 synthetic frames (Y 52 and
148, UV 128) into exactly two 1920x1080 NV12 frames. Each output frame
retained its expected constant luma and neutral UV, correctly separated.
Input SHA unchanged, frame sizes exact. Source/oracle SHA was rechecked.
Six Python regression tests PASS, including short/long input, wrong count,
existing-output preservation, input symlink rejection and path confinement.

This is **not** a camera-capture test and does not authorize an ISP register
write, a new candidate kernel, native emitter activation or SecurePD
workarounds. The remaining blocker is exact SP11 uncompressed FULL bus/
compression transition authority and a properly isolated kernel/V4L2 mode;
only then can the validated desktop bridge consume genuine camera frames.

## Reproduce safely

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004ij-windows-app-nv12-offline \
  -p 'test_bridge.py' -v
```

The tests use private temporary synthetic NV12 frames, and the original
Windows holder proof only as a SHA-pinned **read-only** reference. Golden,
accepted QC10C, host camera hardware and IR/login all remain unchanged.
