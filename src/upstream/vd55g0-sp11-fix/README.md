# VD55G0 IR camera on SP11 with Peter Marshall's vd55g1 series

Peter Marshall's v2 series ("media: i2c: st-vd55g1: Genericize driver and add VD55G0 support",
18 Sep 2026) plus Jizhou Tong's register-width fix (v2) probes the SP11 IR sensor
(VD55G0 cut 1, revision 0x1111) and applies the built-in ST 2.11 patch. The sensor then
reports STREAMING but sends no frames, and the stop command times out (-110).

We traced it on the old CAMSS stack (camss 50, CSIPHY0 -> CSID0 -> VFE0 RDI0) with a
test-only debug build. The build traces regmap writes and has module parameters for the
patch file, the OIF_CTRL write, the ISL write, and extra register writes.

| Setup (840 Mbps, 1 lane) | Result |
|---|---|
| as posted (line 1128, writes 0x0329=0) | no frames, stop hangs |
| OIF_CTRL forced to ST's one-lane value 0x81 | no frames |
| Windows 552-byte patch instead of ST 2.11 | no frames |
| line 1200, 0x0329 still written to 0 | no frames (one run; see correction below) |
| line 1128, 0x0329 not written | no frames |
| **line 1200, 0x0329 not written** | **frames, 61.6 fps, test pattern correct, clean stop** |

The sensor patch makes no difference: ST 2.11 and the Windows patch behave the same.
ST's reference vd55g0 driver already uses a 1200-pixel line below 900 Mbps and never
writes 0x0329.

### Correction (16 Oct 2026): 0x0329 is harmless, only the line length matters

Sergey Lebedev reported that on the Intel SP11 his driver writes ISL_ENABLE=0 once per
power-on and streams fine. Retest on the sp11-imx681-lab boot with the line-length fix
in the driver and 0x0329 handled three ways (`lab/vd-isl.py`, `lab/isl-test.sh`):

| 0x0329 handling (line 1200, 840 Mbps, 644x604 Y10) | Captures |
|---|---|
| written 0 at every stream start (Peter's v2) | 6/6, incl. first capture after load; test pattern correct |
| written 0 once per power-on, after boot | 2/2 |
| never written | 2/2 |

The exact v2 tree (line length only, Peter's ISL write kept) also streams 4/4 with a
correct diagonal test pattern. The earlier "no frames" row came from a debug build where
the line length was forced by a late register write, not by the driver. v2 of the patch
drops the ISL change.

## Patch

`patches/0001-media-i2c-vd55g1-fix-vd55g0-streaming-below-900-mbps.eml` is the b4
output (draft, not sent yet). It is an incremental fix on top of Peter's v2 and
Jizhou's fix.

Context: Benjamin Mugnier (ST, vd55g1 maintainer) NAK'd the refactor approach on
21 Sep 2026. He prefers a separate vd55g0 driver, which Sergey Lebedev is preparing
from ST's downstream code. The patch is mainly a data point for whichever driver lands.

## Lab files

- `lab/vd-dbg.py`, `lab/vd-dbg2.py`: test-only debug edits applied to vd55g1.c
- `lab/vd55g0-sp11-fix.py`: the fix as an exact-match edit script
- `lab/ir-matrix.sh`: one module load, several sensor configurations per boot
- `lab/trace-ir.sh`: regmap trace around a capture
- `evidence/test-pattern.png`: diagonal grey-scale pattern captured with the fixed driver

The Windows-derived 552-byte patch was used only for the comparison test. It is not
included here.

## IR illuminator (16 Oct 2026)

The IR LED is PM8550 flash channels 1+4 (SID 1, 0xee00) in hardware strobe from sensor GPIO1, matching
the Windows PMIC trace (ee46=80, ee4e=09, ee4a/ee4d=05, ee67 bit 0 cleared). First lit frame:
`evidence/ir-lit-first-frame.png` (dark room, 1 ms pulses, 100 mA per channel, analogue gain 16).

What was needed on top of Peter's driver and mainline leds-qcom-flash (`illuminator/`):
- sensor: `v4l2_async_register_subdev_sensor()` so the `flash-leds` link binds the flash subdev;
- leds-qcom-flash: our external-strobe safety patches (current/timeout before arming, etc.), plus
  clearing ee67 bit 0 while hardware-armed as Windows does (without it the LED never fires);
- leds-qcom-flash remove/probe-error loops never release the V4L2 flash device (off-by-one, still in
  mainline/linux-next 2026-10-15): rmmod leaves a registered subdev on freed memory and the next
  control access oopses (`evidence/crash-20261016/`). Fixed by `flash-remove-fix.py`.
- the v4l2-flash core resets the strobe source on close, so `flash-hold.py` arms only while it holds
  the subdev open and disarms on exit or signal.

Safety limits used: DT caps 200 mA total and 10 ms per pulse; manual exposure ~1 ms (~6% duty).

### IR LED current: matches Windows exactly

Static read of the Windows PMIC driver's flash target-current callback: it accepts 5-1500 mA per
logical LED, converts to target steps (`I*1000/step - 1`), and for a paired LED writes **half** of
that step count (`>>1`) to each of the two channels. Windows' 700 mA request for the IR LED therefore
lands as 0x1b on both paired channels = 350 mA each, 700 mA total - byte-identical to what our
lab setting (flash intensity 700000 uA) writes to ee42/ee45. Pulse width also matches (Windows
sensor setup: manual exposure 100 lines, ~0.86 ms). A warm reboot from Windows clears the
registers, so the value cannot be read back after the fact.
