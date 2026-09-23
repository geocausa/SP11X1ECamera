# Upstream OV13858 and Surface camera research — 2026-09-23

This source-only, text-only research used public upstream documents,
GitHub issues and Linux community reports. No private photo,
sensor pixel, RAW frame, thumbnail or image hash was exported,
and no camera, IR or Golden default was changed.

## Source-supported facts and limitations

1. Mainline OV13858 sensor driver:
https://codebrowser.dev/linux/linux/drivers/media/i2c/ov13858.c.html
It declares only MEDIA_BUS_FMT_SGRBG10_1X10 (GRBG).
The actual full-resolution mode sets 0x3811=0x04, 0x3813=0x05,
0x3820=0xa8 and 0x3821=0x00; other modes have different
orientation/cropping registers despite reporting only GRBG.
Our currently maintained Qualcomm SP11 rear driver contains
these same values. Driver-declared GRBG alone does NOT prove
the actual first-pixel CFA order emerging from our physical
CAMSS crop, flip, mount and RAW10 buffer. The sensor driver
also defines blue/green/red MWB register addresses 0x5100,
0x5102 and 0x5104. Do NOT blindly write them.

2. libcamera developer discussion of Bayer flips/cropping:
https://patchwork.libcamera.org/patch/24092/
https://lists.libcamera.org/pipermail/libcamera-devel/2022-November/035362.html
https://github.com/raspberrypi/libcamera/blob/main/Documentation/sensor_driver_requirements.rst
A sensor flip, transformation or crop parity can alter
the effective Bayer order. V4L2 layout-modifying flips
must be represented in format/metadata. Our E004nh
isolated opt-in BGGR colour shift is a diagnostic
hypothesis, not hardware proof or a reason to change
kernel Bayer format, sensor orientation or Golden default.

3. Other Surface models using OV13858:
https://github.com/linux-surface/linux-surface/issues/2153
https://github.com/linux-surface/linux-surface/discussions/1354
https://github.com/linux-surface/linux-surface/discussions/2198
Intel SP8/SP9/SP10 and Intel SP11 have real rear OV13858
Linux sensor driver/streaming reports. Intel IPU6/IPU7,
ACPI bridge and INT3472 power patches are NOT portable
directly to Qualcomm CAMSS. A real libcamera rear camera
diagnostic in IPU6 discussion #1354 shows missing
ov13858.yaml IPA tuning file and fallback to
ipa/simple/uncalibrated.yaml. This points to separate
possible auto exposure, AWB, colour correction and
lens-shading gaps AFTER physical Bayer site alignment.

4. Public Qualcomm SP11 camera work:
https://github.com/rjindael/fedora-surface-pro-11/blob/main/CAMERA.md
https://github.com/ooaklee/linux-surface-pro-11-oe
The former confirms OVTID858/OV13858 rear and
SONY0681/IMX681 front from Windows ACPI/DriverStore
but reports its OWN Qualcomm rear camera not working.
The latter documents experimental X1E front-camera
progress while rear issue #41 remains open. Neither
provides a verified drop-in OEM rear 4K30 solution
for our distinct SP11 camera stack as researched
2026-09-23. Do not infer nobody else has success.

5. ISP pipeline and software processing reference:
https://libcamera.org/faq.html
https://docs.libcamera.org/master/public-api/camera-model.html
https://libcamera.org/entries/2025-08-25.html
Correct RAW sensor streaming is insufficient for OEM
photo quality. Black level, per-channel gain, AWB, Bayer
interpolation, CCM, gamma, temporal noise and lens shading
need independent validation. Optional libcamera SoftISP
is a comparison/reference, NOT proven automatically
capable of current SP11 rear4K>=29fps and each front/rear
30frame high-gain interval. Keep Golden protected.

## Concrete next SP11 project step

Respect user's known thick broken SP7 LOWER LCD band:
ONLY unaffected upper60% known static RGB/gray patches,
independently register their actual optical positions
and take interior ROIs with margin. E004ng full-screen
old target may be contaminated by broken LCD; E004nh
upper-only opt-in BGGR changed WHOLE bright-region
RGB from magenta to green, but BOTH trials failed
separate original front high-gain interval fps and
did not establish true individual patch colour order.
E004ne remains most recent fully accepted 4K30
native front/rear original one-shot.

Before another physical change compare SAME actual
source-locked native RAW10 frame's four CFA site
responses against known patch identity and actual
full-resolution crop origin, driver fmt and orientation.
Only on SP11 process transient private native RAW10
with both GRBG and opt-in BGGR converters, no optical
pixel export/storage in repo or cross-machine traffic.
Report scalar per-patch channel dominance, neutral
balance, black reference, highlight headroom and native
source cadence. Distinguish source CFA order and
software ISP colour tuning separately; do not promote
a cosmetic matrix, hardware flip, guessed gain or
the BGGR opt-in to everyday camera defaults.
Every fresh physical trial requires unique source-pinned
one-shot, strict >=29fps each gain 30frame window on
BOTH cameras, exact supported controls restore, final
119-edge native neutral and automatic Golden return.
