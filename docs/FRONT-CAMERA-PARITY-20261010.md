# Front camera (imx681) native pipeline: driver proof and Windows parity, 2026-10-10

Scope: the SP11 front camera on the native Linux path (imx681 RAW10 -> CSIPHY2 ->
CSID1 -> VFE1 pix -> 2560x1440 NV12, libcamera pipeline/IPA `camss-x1e`). All
tuning below was measured on this machine against the Windows camera stack
showing the same SP7 test patterns; no OEM tuning data is used or stored here.
Pixels and raw captures stay on the lab machine; only scalar results are recorded.

## Driver proof

One-shot candidate boots today (ae-03 .. ae-18), each a full capture of two phases
(up to 2700 frames each):

| Check | Result |
|---|---|
| Capture completed, exit 0 | ae-11 .. ae-18: 8/8 consecutive (earlier failures fixed: ae-04 frame limit, ae-06 CCM command count, ae-10 media-graph race) |
| Kernel oops/BUG/WARN | 0 |
| Sensors runtime-suspended after stop | yes, every run |
| Private startup profile removed after capture | yes, every run |
| Frame rate | 29.9 fps (30 fps mode); 26 fps average when low-light frame time is enabled |
| Automatic exposure | converges from bright daylight to an unlit room |
| Return to the default (Golden) boot entry | every run |

ISP programming exercised: per-frame 257-point RGB tone LUT through the VFE1 parameter
queue, colour-correction matrix (module parameter `native_front_ccm_q7`, packing
verified with an order probe), BT.601 full-range CST.

## Image processing implemented (IPA, `front-ae/camss-x1e-ipa.cpp`)

* **Tone and colour**: shared smooth tone curve + white-balance gains + linear CCM, fitted
  from a linear (identity LUT/CCM) capture against Windows on the whole scene plus
  display patches (`front-pattern/fit-front-param.py`).
* **Automatic exposure, displayed-brightness metering**: exposure is chosen so the mean
  *displayed* green of the 1024 BE regions reaches a target, instead of the raw mean
  (a bright window no longer darkens the room). Target rises from 400 (bright scenes) to
  540 (dim scenes, 10-bit), interpolated on a scene-level estimate, as measured for Windows.
* **Highlight guard**: exposure is limited so the 95th-percentile region stays at or below
  display level 900/1023 (a large bright area such as a screen at night is not clipped).
* **Low-light frame time**: after 16x analogue gain the frame time is lengthened up to
  4600 lines (~23 fps, as Windows does) before digital gain (max 6x).
* **Automatic white balance**: frame R/G and B/G statistics are compared with the
  calibration scene; red and blue LUTs are rescaled by the smoothed ratio (grey world
  anchored to the calibrated look).

Tuning used for the final run: `front-ae/tuning/imx681-front-v9.yaml`.

## Parity with Windows (same scene, back-to-back runs)

Y in 8-bit levels, dC = chroma distance in 8-bit U/V units. Display patches are read
from the screen region (rows 7-8, cols 6-10 of a 16x9 grid).

| Condition | Measure | Linux | Windows |
|---|---|---|---|
| Daylight (model on linear capture ae-11) | scene mean Y | 96 | 98 |
| Daylight (model) | grey patches mean abs dY / dC | 2.6 / 4.5 | reference |
| Daylight (model) | colour patches mean abs dY / dC | 3.6 / 7.6 | reference |
| Evening, room lamp (ae-13) | grey mean abs dY / dC | 12.3 / 6.0 | reference |
| Unlit room, before AWB (ae-16) | grey dC | 30.4 | reference |
| Unlit room, AWB (ae-17) | grey dC | 15.4 | reference |
| Unlit room, AWB + low-light frame time (ae-18) | grey dY / dC; colour dY / dC | 14.9 / 15.5; 19.9 / 43.1 | reference |
| Unlit room (ae-18) | scene mean Y | 22 | 33 |

Windows' own brightness is not stable in low light with a large flashing screen in view:
two consecutive evening runs of the same scene gave scene means 137 and 83.

## Known remaining differences

1. **Local tone mapping**: Windows lifts dark areas and boosts dim regions locally (a dim
   screen in a bright room is rendered ~2.2x brighter than a global curve predicts). The
   native path has one global tone curve.
2. **Low-light colour**: Windows desaturates strongly near white and at high gain; the CCM
   here is static (module parameter), so saturation cannot yet follow gain.
3. **Highlights**: Windows rolls screen whites off near 228-231; ours reach ~243.

All three need dynamic matrix / local tone control from the IPA, i.e. extending the VFE1
parameter queue beyond the gamma block.

## Tools (`src/native-rgb/front-pattern/`)

`install-front-run.py` (one-shot candidate boot), `run-front-pattern.py` (capture runner),
`analyze-front-pattern.py` / `analyze-front-windows.py` (pattern-aligned ROI means;
`FRONT_ROI=rows:cols` override), `rebuild-play-log.py` (SP7 player log from per-loop times),
`compare-front.py`, `scene-check.py`, `compare-session.sh`, fit scripts.
