# E004ik — kernel-native, strictly non-runnable alternate NV12 buffer planner

Date: 2026-09-20. Parent: `158d49a`. SP11 Linux protected Golden.
This is a **separate offline source-overlay experiment, not a deployed
kernel candidate, V4L2 mode, hardware test or QC10C replacement**.

## Implementation

`nv12-kernel-sidecar.cfrag` is appended exclusively to a disposable copy
of the original `camss-vfe-680.c` when running `build-offline.sh`.
It uses actual kernel `vfe_device`, `camss_buffer`, `vb2` and DMA
types, unlike the earlier standalone E004ii planning model.

The planner explicitly rejects:

- any machine/IFE path other than the proven SP11 IFE1 target;
- the current production QC10C format even when its DMA allocation is large
  enough to hold the hypothetical smaller NV12 payload;
- an incorrect width, height, stride, `sizeimage`, memory-plane count or
  video queue;
- inactive, undersized or misaligned buffers, absent DMA addresses, and
  either FULL Y or chroma DMA crossing the 32-bit device-address window.

It produces Y at buffer base and interleaved UV at base+3,686,400,
each with the proposed 2,560-byte stride. The 5,529,600-byte allocation,
packer value 3 and proposed layout are *not* SP11 pixel-output acceptance.
Actual colourimetry, sample packing and ISP scaler remain unvalidated.

**Hardware authority is deliberately absent:** the separate authorization
function unconditionally returns `-EOPNOTSUPP`; there are no hardware
register reads/writes, streaming call sites or format advertisements in the
sidecar. Existing production PIX still exposes QC10C only. Merely
compiling the planning code does **not** authorize linking it into live
capture or booting the scratch module.

## Exact offline kernel build result

On SP11, `build-offline.sh` made a private /tmp CAMSS source copy, verified
the original VFE680 hash `5af25a42cd15aa5b4c0721da1929b3e50b7bac43e40bdb0962ba996f189632ec`,
checked Golden and current v4 Kbuild release and compiled a complete
**uninstalled qcom-camss.ko**. The ELF symbol table confirms that both
standalone planner and fail-closed authorization symbols are compiled.

- Compiled sidecar SHA-256:
  `feed2857eef7b14b1df5a8569885815493f3ad0ac17c73296072b979e2a684af`
- Disposable module SHA-256:
  `e8815de0f1332dd8bafa4fcf0ec362009f4b12634372f14f80c9bf2090df2209`
- `test_stage.py`: six static/negative tests PASS, including rejecting
  removed NV12 format/queue/DMA checks, any MMIO write and bypass of
  unconditional `-EOPNOTSUPP`.

The build and result describe a *compiled offline implementation only*.
The disposable module is deleted after build; no /boot, module tree, camera,
Windows, KD, PMIC, native IR, login or Golden state was modified.

## Reproduce

```sh
bash experiments/E004-front-ir-vd55g0/e004ik-kernel-nv12-plan/build-offline.sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004ik-kernel-nv12-plan \
  -p 'test_stage.py' -v
```

## Actual next engineering gate

The public Qualcomm BUS ver3 driver documents uncompressed FULL NV12, but
its NV12 selection alone does not reset prior UBWC MODE_CFG on this SP11.
Before any new runnable module, separately establish the exact X1E80100
FULL-client linear ISP/bus register recipe, image stride and a safe
compression-state initialization/restoration path. Then build an isolated
mode-specific V4L2 queue and capture/IRQ lifecycle with explicit failure
rollback. The tested E004ij GStreamer 1920x1080 bridge can consume the
result only after verifying genuine linear-NV12 pixel data. The already
archived Windows WinRT 1920x1080 NV12 holder proof makes a repeat resolution
oracle unnecessary.
