# Real-hardware evidence — Oaklee v15 OV13858 + DW9800K shared rail

**Date:** 2026-11-21 UTC. **Hardware:** Surface Pro 11 OLED, X1E80100.
**OS:** isolated Ubuntu 26.04.1, NVMe p6,
UUID 50088238-e31a-43c9-ad75-0ebe70ebfbb2.
**Kernel:** 7.3.0-jg-1sp11v15-qcom-x1e (Oaklee v15).
**One-shot entry:** sp11-oaklee-v15-vddio-rfc1.

## Boot and source

- Source anchor: Oaklee commit 52812090bd341a2a1e609f32afa4595b51a97127.
- Old rear-camera handover 0001 was successfully replayed against the
  original exact board blob. The three incremental vddio patches
  were generated from exact source and pass strict checkpatch.
- dw9719.c with optional-vddio patch built against actual Oaklee v15
  headers, correct full vermagic. An isolated updates/dw9719.ko
  was selected by depmod; the original compressed module was untouched.
- Only the embedded OLED DTB payload in the previously tested rear-camera
  EFI image was changed; all other PE bytes are identical to the input.
  Original Oaklee EFI image and initrd preserved.
- The booted Device Tree contained actuator@c (dw9800k), separate
  vdd-supply to PM8550 L16B, vddio-supply to PM8010 L6M and sensor
  lens-focus phandle 0x2f3.
- Both sensor 1-0010 and actuator 1-000c bound. The actuator appeared
  as /dev/v4l-subdev28; rear sensor as /dev/v4l-subdev27.

## Native actuator and camera power test

Five sequential focus_absolute control writes (128,512,896,256,0)
returned matching readback while the actuator was open.
The lens was closed, permitted to autosuspend and reopened; 512
also passed. During a separate 240-frame V4L2 capture, focus
positions 896 and 128 passed with the sensor still streaming.

| State | L6M 1.8V votes | L16B 2.912V votes | L5M 2.8V votes |
|---|---:|---:|---:|
| Both idle | 0 | 0 | 0 |
| Sensor streaming alone | 1 | 0 | 1 |
| Sensor + VCM open | 2 | 1 | 1 |
| VCM closed; capture continues | 1 | 0 | 1 |
| Both idle after completion | 0 | 0 | 0 |

This demonstrates independent Linux regulator consumer lifetimes,
not a direct oscilloscope measurement of voltage or platform sleep draw.
The 240-frame capture produced exactly 240 V4L2 output frame markers
and exit status 0, despite lens open/close and focus commands.

## Other camera regression tests

- Rear OV13858: 120 consecutive 4224x3136 SGRBG10 RAW10 frames,
  16,558,080 bytes per frame, 29.95 fps, exit 0.
- Front IMX681: 30 consecutive 3840x2640 RAW10 frames,
  12,672,000 bytes per frame, approximately 29.99 fps, exit 0.
- IR VD55G0: 60 consecutive 644x604 RAW10 frames,
  492,864 bytes per frame, ~49.78 fps, exit 0.
- OV13858 subdevice v4l2-compliance: 46 succeeded / 0 failed /
  0 warnings.
- DW9719 subdevice v4l2-compliance: 45 succeeded / 1 failed /
  0 warnings; the failure is the preexisting control event
  subscribe ioctl, not the power/focus implementation.

These three camera captures were sequential. IR illumination
was not enabled, and no Windows Hello/biometric claims are made.

## PM device callback tests

Three successful pm_test=devices / echo mem > /sys/power/state
roundtrips, followed by focus-control position 160,320,480
respectively and 30 valid rear RAW frames after each cycle.
Both devices runtime-suspended afterward, L6M and L16B both zero.
Kernel suspend_stats incremented from success=0/fail=0 to
success=3/fail=0. This exercises device PM callbacks, not
true platform deep suspend.

## Original artifacts and SHA integrity

- Original verified rear-oriented EFI image from Oaklee's p6:
  SHA256 3b77cea73b3a1913423b8c0f41e94abe33bd380142387555674d57670877877e
- Isolated test EFI with DW9800K node:
  SHA256 e98040f81021a29a0ca253daf450c9bc157a095ce91021ca44945ca8789a5ee4
- Extracted, patched OLED DTB:
  SHA256 51d89a13a6524b7a8fd6a6fa9c8effcc3f5a91bbd26da65590f03520eb76019c
- Original Oaklee compressed DW9719 module:
  SHA256 b5a0ab394a24a98595675f661996cb30b8522056eaa010962763ee96dc29fe07
- New isolated DW9719 module compiled for Oaklee's ABI
  on the separate Ubuntu 26.10 host with GCC 15.3:
  SHA256 39a48296a45441149ec43b03abf99e7f26743f506f1bb2ee1ea3bff4ebbe753d
- Also rebuilt same patched source against Oaklee's own headers
  and GCC 15.2, matching its original compiler version.

Accepted unified13 default remained configured, GRUB next_entry was
cleared automatically after the one-shot boot, and Golden v19c was
not overwritten. The test p6 filesystem is a separate installation.

## Open limitations (not hidden)

There is no optical focus movement/sharpness evidence in darkness.
Full platform deep-sleep resume, idle electrical input parent of
L6M, camera IPA/ISP calibration, three-camera simultaneous use,
and the VD55G0 illuminator remain outside this qualification.
The source DTS change still needs normal production EFI DTB packaging,
not binary section replacement, when Oaklee integrates it.

Logs accompanying this report:
- focus-and-runtime-pm.log
- concurrent-stream-lens-rail-v15.log
- concurrent-stream-240-v4l2.log
- rear-4224x3136-120-oaklee-v15-vddio.log
- front-imx681-3840x2640-30.log
- ir-vd55g0-644x604-60.log
- v4l2-compliance-sensor-v15.log
- v4l2-compliance-lens-v15.log
- pm-device-callback-three-cycles-v15.log
- pm-postcycle-rear-30-1.log, -2.log, -3.log
- module-exact-source-build.log
