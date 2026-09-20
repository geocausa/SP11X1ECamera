# E004ii — offline front RGB linear-NV12 buffer-planning code

Date: 2026-09-20. Parent: `7c9163a`. On protected SP11 Golden. This stage is
a separate **offline-only, non-runnable** source model. Nothing in it is wired
into the kernel, V4L2, the production launcher, GRUB or the physical camera.

## What is now independently source-backed

The exact public Qualcomm VFE BUS ver3 source used in E004ih is pinned by
SHA-256 `6834887a2e0afcc55c24a61d32f0996e44764dbdd6eaeccf3b52f3b712c231c8`.
Its FULL output format code treats uncompressed NV12 and UBWC NV12
separately, and the enum maps uncompressed NV12 to `PACKER_FMT_VER3_PLAIN_8_LSB_MSB_10`
(numeric 3), while both TP10 cases use numeric 11. This is public driver
format evidence, **not** same-machine X1E80100 NV12 runtime authority.

The accepted Windows OEM ISP output was FULL_Y/FULL_C TP10-UBWC with packer
11 and compression settings; Windows-selected IMX681 sensor input was
3840x2160 at 30 fps. The 2560x1440 geometry proposed here is the **existing
Windows-proven internal ISP FULL output size**, not a claim about the final
resolution offered by the Windows Camera application.

A crucial unresolved transition: the public start-WM function sets
compression when `en_ubwc` is true; simply using the noncompressed
format path does not prove that old compression/mode registers left by an
earlier QC10C session are reset. Therefore the actual Linux driver must
prove/handle a safe format transition, not just change packer 11 -> 3.

## Actual work completed

`nv12-buffer-plan.{c,h}` calculates and checks a *proposed* single-memory-
plane 2560x1440 NV12 surface at 2560-byte Y/UV stride, two FULL ISP client
DMA addresses, and 5,529,600 allocated bytes. The only proposed packer is
3 (source-backed). The module explicitly refuses other resolutions and
strides, short allocations, misaligned/zero/overflowing/out-of-32-bit-span
DMA addresses, stale/mismatched format plans and accidental compression
enable. It resets DMA addresses on any failed rebinding. It cannot perform
MMIO or access a device.

This **does not** prove that SP11 VFE1 accepts the proposed linear output,
or establish ISP scaler/colorimetry, bus mode/static registers, IRQ
completion, production controls or the application-facing resolution.
There is no hardware candidate package or Windows/KD boot in E004ii.

## Reproduce safely on SP11 Golden

Obtain the published Qualcomm source into a *disposable* file (never commit
that third-party raw source) and verify its hash before interpreting it:

```sh
python3 - <<'PY'
import urllib.request, base64, pathlib
url = 'https://android.googlesource.com/kernel/msm/+/cf55e2491a3f1915760221075433d234b18fbe83/drivers/media/platform/msm/camera/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c?format=TEXT'
pathlib.Path('/tmp/sp11-camera-e004ii-public-cam-vfe-bus-ver3.c').write_bytes(
    base64.b64decode(urllib.request.urlopen(url, timeout=20).read()))
PY
python3 experiments/E004-front-ir-vd55g0/e004ii-nv12-buffer-plan/verify-vendor.py \
  /tmp/sp11-camera-e004ii-public-cam-vfe-bus-ver3.c
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004ii-nv12-buffer-plan -p 'test_vendor.py' -v
d=$(mktemp -d /tmp/sp11-nv12-e004ii.XXXXXX)
clang -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
  -fno-omit-frame-pointer \
  experiments/E004-front-ir-vd55g0/e004ii-nv12-buffer-plan/nv12-buffer-plan.c \
  experiments/E004-front-ir-vd55g0/e004ii-nv12-buffer-plan/test-nv12-buffer-plan.c \
  -o "$d/test"
"$d/test"
rm -rf "$d"
```

Expected: SHA-pinned upstream result PASS; three Python tests PASS;
26 offline C test checkpoints PASS with ASan+UBSan on actual SP11 ARM64.

## Next gate

Complete the **SP11-specific** NV12 bus-register/disable-compression and
ISP/scaler authority before any hardware write or V4L2 exposure.
Explicitly isolate the candidate from QC10C, preserve clean same-boot
repeated-use semantics, then create a fresh bounded one-shot Linux
experiment with Golden rollback. A Windows one-shot should answer a
specific missing app-resolution/ISP-policy question rather than
repeating the known compressed-output capture.

Native IR illumination remains disabled; SecurePD worker admission,
Windows Hello and independent physical LED-off safety remain separate
blocked tracks. Existing Golden and QC10C remain unchanged.
