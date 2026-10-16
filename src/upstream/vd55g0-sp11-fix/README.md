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
| line 1200, 0x0329 still written to 0 | no frames |
| line 1128, 0x0329 not written | no frames |
| **line 1200, 0x0329 not written** | **frames, 61.6 fps, test pattern correct, clean stop** |

The sensor patch makes no difference: ST 2.11 and the Windows patch behave the same.
ST's reference vd55g0 driver already uses a 1200-pixel line below 900 Mbps and never
writes 0x0329.

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
