# Oaklee v15 / Surface Pro 11 OLED — rear DW9800K autofocus power fix

**HARDWARE TESTED 21 November 2026** on Surface Pro 11 OLED using the
isolated Oaklee Ubuntu 26.04.1 userspace and its actual kernel
**7.3.0-jg-1sp11v15-qcom-x1e**. This fixes actuator I/O power and
sensor/lens power sharing; optical lens sharpness is not yet verified.

## Exact source and prerequisites

- Oaklee source commit: 52812090bd341a2a1e609f32afa4595b51a97127.
- Existing prerequisite: OV13858-OAKLEE-V15-VERIFIED-HANDOFF-20261120.zip
  containing the original rear camera board source patch 0001, CAMSS
  lane-normalization patch 0002 and experimental D-PHY fix 0003.
  Do not reapply common CAMSS/PHY changes if already merged.
- These NEW patches apply after the previous rear board 0001:
  1. patches/0004-*: document optional DW9719-family vddio-supply
  2. patches/0005-*: implement optional I/O regulator lifecycle
  3. patches/0006-*: add OLED DW9800K/L16B and sensor lens-focus wiring

Original source blob SHA1s were checked against the exact source:
- drivers/media/i2c/dw9719.c:
  3b7ba88fd67c044ef9005a0aac6a5d26ab939a90
- Documentation/devicetree/bindings/media/i2c/dongwoon,dw9719.yaml:
  8e8d62436e0d0c4f9af9e52262b23881abd37cec
- arch/arm64/boot/dts/qcom/x1e80100-microsoft-denali-oled.dts:
  0e52c6f965117eeb73b43ea91c6fd3b8ffa7269d

This set targets the **pre-v4 DW9800K driver/binding in Oaklee v15**.
Griffin's separately reviewed DW9800K v4 series changes the binding.
Do not blindly stack the two variants.

## What the new code does

The rear OV13858 sensor on CCI0 master1 address 0x10 consumes PM8010
L6M 1.8 V as DOVDD. The DW9800K actuator on the same master at 0x0c
needs L6M for I/O, while its VDD uses PM8550 L16B 2.912 V.

- Bindings: optional vddio-supply property.
- DW9719 driver: enable VDDIO before VDD, disable it after VDD and
  unwind both on failure. Existing single-supply boards stay compatible.
- OLED DTS: add L16B ldo16 and the actuator node with separate supplies;
  connect the existing OV13858 to the VCM with lens-focus.
- The L6M INPUT electrical parent remains unverified, so the patch
  deliberately makes no extra claim about or change to that wiring.

## Application / build guidance

On the pinned v15 source WITH the earlier rear patch already applied,
run git apply --check on 0004, 0005 and 0006 in that order, then apply
each patch or use git am for their Signed-off-by commits.

Rebuild the kernel and DTBs with Oaklee's normal build system.

**Important EFI packaging caveat:** Oaklee's v15 EFI ZBOOT has 38
embedded .dtbauto DTBs. The Surface Pro 11 OLED DTB is the second
section (original PE file offset 0x47e00). On this hardware a new
external GRUB devicetree statement alone does NOT override that
embedded DTB. The updated OLED board DTB must be part of the rebuilt
EFI kernel image.

The lab experiment was a one-shot using the already-verified
rear-camera EFI copy with ONLY its embedded OLED DTB changed to
add the lens. This has been checked byte-for-byte outside that DTB
section. It is a valid lab test, NOT a production packaging method.

Keep original Oaklee kernel, modules and initrd untouched for recovery.
In the isolated test, the new DW9719 module was added as a separate
updates/dw9719.ko chosen by depmod; original compressed dw9719.ko.zst
remained unchanged. Default GRUB stayed accepted unified13.

## Actual Oaklee v15 hardware results

- Boot of the isolated Ubuntu p6 and original Oaklee kernel: PASS.
- OV13858 1-0010 and DW9800K 1-000c: BOUND.
- VCM focus_absolute positions 128, 512, 896, 256, 0 and reopen 512:
  successful ioctl writes and matching readback.
- Rear camera RAW10 4224x3136: 120/120 frames at ~29.95 fps
  (16,558,080 bytes per frame).
- V4L2 direct rear capture: 240 frame markers, exit code 0, with
  actuator opened, adjusted and closed DURING camera streaming.
- Actual shared L6M regulator enable counts: 0 -> 1 -> 2 -> 1 -> 0
  (idle; sensor; sensor+lens; sensor; idle). L16B returned to 0
  while the rear sensor continued capturing.
- Front IMX681 RAW10 3840x2640: 30/30 frames at ~30 fps.
- IR VD55G0 RAW10 644x604: 60/60 frames at ~49.8 fps,
  without IR illuminator.
- OV13858 V4L2 compliance: 46/46. DW9719 VCM: 45/46;
  the outstanding control event subscription test is unrelated
  to the optional I/O supply and does not prevent focus control.
- 3 successful Linux pm_test=devices callback roundtrips,
  zero reported failures; each followed by focus control and
  successful 30-frame rear capture. Both devices autosuspended.

## Limitations

- No measured optical sharpness or lens-motion test (room dark).
- PM callback tests are NOT full platform deep suspend/standby.
- No three-camera simultaneous test or IR illuminator/Hello test.
- L6M source supply electrical wiring is not schematic-proven.
- The libcamera 0.7.0 stack still warns about sensor crop metadata
  and missing software ISP/IPA; raw camera acquisition works.
- The published source patch application and driver build are verified,
  but Oaklee's entire production EFI kernel has NOT been rebuilt and
  qualified from that source package; the boot used the isolated
  binary DTB experiment described above.

Full recorded evidence and text-only logs are in evidence/.
No room imagery or proprietary Windows binaries are included.

This bundle EXTENDS the original rear-camera help already given
to Oaklee. It should not duplicate previously merged patches.
