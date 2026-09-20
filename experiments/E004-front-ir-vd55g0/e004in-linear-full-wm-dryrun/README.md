# E004in — compiled, non-runnable FULL Y/C NV12 write-master plan

Date: 2026-09-20. Parent: `91177db`. Actual SP11 Linux Golden v4.
**OFFLINE KERNEL BUILD PASS; NO CAMERA MMIO/STREAMING, INSTALL OR BOOT.**

## What is established and what is proposed

The accepted same-machine Windows front camera mode is RAW10 sensor
3840x2160 -> ISP VFE1 FULL compressed 2560x1440 QC10C/TP10 UBWC,
with WM0/1 packer 11 and their separately observed Y/C metadata.
An archived successful Windows front Color/VideoRecord WinRT reader
selected 1920x1080 NV12, but the component producing that app-facing
format was not proven to be VFE1 FULL. Preserve the accepted QC10C
production implementation.

The SHA-pinned public Qualcomm BUS ver3 source explicitly treats NV12
as uncompressed, maps it to the 8-bit plain packer (numeric 3), and
computes non-UBWC WM frame increment as `plane_stride * slice_height`.
On FULL WM0/1, its start-WM function does not set image stride, so the
buffer-update path must set both IMAGE_CFG2 strides. Qualcomm's
`en_ubwc == 0` branch also does NOT clear a prior WM MODE_CFG:
**format negotiation/packer switching cannot by itself safely reset
an existing compressed-session hardware state**.

The active local VFE680 global-reset callback is a no-op completion
and its bus stop only disables WM CFG bit 0; neither proves a
compression-state reset. This is a *source-observed hazard*, not a
claim that hardware is irreversibly stuck or linear output impossible.

## Actual new code

`full-wm-dryrun.cfrag` compiles into a unique disposable SP11 CAMSS
source copy **after** the E004im combined NV12 V4L2 format and
kernel-native DMA planner overlays. It calls that independently
gated single-buffer DMA planner to obtain Y/UV addresses and derives
an isolated *data-only* candidate for WM0 and WM1:

| Field | Proposed Y / WM0 | Proposed UV / WM1 |
| --- | --- | --- |
| image_cfg0 | 0x05a00a00 (1440x2560) | 0x02d00a00 (720x2560) |
| image_cfg2 / stride | 2560 | 2560 |
| packer_cfg | 3, uncompressed NV12 | 3, uncompressed NV12 |
| frame_incr | 3,686,400 | 1,843,200 |
| image_addr | validated allocation base | base + 3,686,400 |

These values are a **proposal from existing known geometry and public
vendor format semantics**, not readback or approval of an X1E80100
physical VFE1 linear-output mode. The data type cannot execute
register writes; neither function has a live call site or external
export. `verified_ubwc_state_transition` and
`approved_for_hardware` are both false; authorization always
returns `-EOPNOTSUPP`. No speculative values are supplied for
WM MODE_CFG, META_CFG, CTRL_2, BW_LIMIT, common UBWC_STATIC_CTRL,
IFE TOP/RT-CDM ISP processing or 10-bit-to-8-bit colour conversion.
The already compiled E004im NV12 V4L2 STREAMON is independently
rejected **before media-pipeline power-up**, while QC10C remains
first/default in the accepted format table.

## Reproduce and actual result on SP11

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004in-linear-full-wm-dryrun \
  -p 'test_full_dryrun.py' -v
bash experiments/E004-front-ir-vd55g0/e004in-linear-full-wm-dryrun/build-offline.sh
```

Actual SP11: 7 positive/negative offline tests PASS and a complete
Golden-v4 ABI `qcom-camss.ko` **disposable build PASS**.
The compiled/uninstalled module SHA-256 was
`fe3108993b34b986d4fdb9a52a530cbff947c65dff66df57327ead1453bf6c26`.
The test suite rejects accidental hardware authorization, compressed
state being marked proven, changing the shared DMA planner, missing
chroma stride, added MMIO, and a newly added live caller.

The disposable .ko is removed after build; no installed kernel,
camera node, Windows boot/KD, GPU, IR illumination, PMIC, secure
worker, PAM, or Golden boot was touched.

## Next hardware-proof gate

Obtain exact SP11 VFE1 linear Y/C output semantics, explicit safe
UBWC mode/static-control clear-and-verify plus session transition
order, and the matching ISP TOP/RT-CDM RAW10-to-8-bit NV12 output
configuration, including chroma and colourimetry. Only then replace
the two *independent* stream blockers in a separate bounded
one-shot Linux candidate with Golden rollback and exact per-frame
failure cleanup. Once physical linear output is verified, feed
real frames to the already tested 1920x1080 NV12 desktop bridge.

Public source for generic BUS semantics (not same-machine live proof):
https://android.googlesource.com/kernel/msm/+/cf55e2491a3f1915760221075433d234b18fbe83/drivers/media/platform/msm/camera/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c
