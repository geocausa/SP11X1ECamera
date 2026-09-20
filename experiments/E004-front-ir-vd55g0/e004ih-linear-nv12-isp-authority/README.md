# E004ih — separate front-RGB linear NV12 ISP-output authority (offline)

Date: 2026-09-20. Parent: `555f086`. SP11 Linux, Golden. This is a
**non-runnable, fail-closed candidate specification**, not an approved hardware
mode, capture result, decompressor, or accepted Windows-parity replacement.

## Newly identified support and precise limit

Qualcomm's public VFE BUS ver3 source has distinct `CAM_FORMAT_NV12` and
`CAM_FORMAT_UBWC_TP10` cases for FULL write clients, and maps NV12 to
`PACKER_FMT_VER3_PLAIN_8_LSB_MSB_10`. The public enum orders that
symbol separately from `PACKER_FMT_VER3_TP_10`. This supports investigating
a *separate uncompressed* Y/C BUS output; it does **not** prove that the same
version or a complete, correct register recipe applies to SP11's VFE1.

Public source reference (vendor format semantics, not same-machine authority):
https://android.googlesource.com/kernel/msm/+/cf55e2491a3f1915760221075433d234b18fbe83/drivers/media/platform/msm/camera/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c

Same-machine authority: original E003h VFE1 FULL QC10C Y/C recipe and Windows
observations in
`experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/vfe1-full-layout/`.
The currently accepted VFE1 implementation programs Y/C packer 0x0b and
compression/meta controls, derives four QC10C subaddresses, requires a
0x76b000-byte video allocation and waits for its independent image/statistics
completion groups. Changing only the fourcc or packer would corrupt the
contract. The current X1E PIX format table advertises **only QC10C**.
Do not change that table or its accepted source in this offline stage.

## Proposed *memory* contract, not yet an ISP register contract

An ordinary, tightly packed NV12 desktop candidate at 2560x1440 with
proposed 2560-byte Y and interleaved UV strides would have:

- Y: offset 0, 1440 rows, 3,686,400 bytes.
- UV: offset 3,686,400, 720 rows, 1,843,200 bytes.
- Total: 5,529,600 bytes, one contiguous V4L2 memory plane, two independent
  ISP FULL write clients; no UBWC metadata allocations.
- These dimensions are **proposed and computed**, not SP11 hardware readback.
  Actual supported alignment/stride and chroma arrangement must be proven
  before changing the queue or generating any ISP writes.

The generic Linux CAMSS V4L2 code already has single-memory-plane NV12 address
arithmetic, but its SP11 PIX format table, bespoke runtime ownership, bus
programming, capture helper, colourimetry and streaming lifecycle are QC10C
specific. There is no verified new-mode driver today.

## Required gates before a one-shot SP11 hardware candidate

1. Establish the exact X1E80100 VFE1 bus-ver3 FULL Y/C NV12 format recipe
   from version-matched public register authority or bounded same-machine
   OEM Windows static/dynamic evidence. Prove packer, image config, stride,
   frame increment, compression disable, metadata/ctrl/bw behaviour, and
   client enable/stop/recovery. Never derive it by substituting 0x0b with a
   guessed value.
2. Isolate the format decision, buffer size, Y and C DMA addresses, 32-bit
   IOVA checks, group completion, controls and failure rollback. Verify a
   clean QC10C default/regression before enabling any alternate path.
3. Define source-to-output chroma order, colour matrix/range, scaler,
   orientation, V4L2 advertised format/plane semantics and buffer lifetime.
4. Build/test offline with a fresh experiment identity; then, if gated,
   prepare and push a separate one-shot camera package. Run one bounded
   capture, independently verify pixel/image content and fault-free stop,
   return to protected Golden, retire the experiment, commit/push.
5. Only after accepted physical frames, tackle continuous output, app capture,
   switching and suspend/resume. Protected IR and illumination remain OFF.

## Repeatable offline check

```sh
python3 -m unittest discover -s experiments/E004-front-ir-vd55g0/e004ih-linear-nv12-isp-authority -p 'test_*.py' -v
python3 experiments/E004-front-ir-vd55g0/e004ih-linear-nv12-isp-authority/verify_candidate.py
```

`verify_candidate.py` verifies five accepted source hashes and the existing
QC10C/PIX/V4L2 contracts before printing a proposal. The script intentionally
has no code path to produce a candidate boot, device write, or approved mode.
No original QC10C source, kernel, GPU, camera, PMIC, IR emitter, Windows
installation, login or Golden state was changed in this experiment.
