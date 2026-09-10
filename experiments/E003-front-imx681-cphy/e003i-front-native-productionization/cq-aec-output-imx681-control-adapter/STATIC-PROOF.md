# CQ static / oracle proof anchors

## Pinned artifacts

- `QcDeviceMFT8380.dll` SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- `com.surface.sensormodule.ffc_imx681.bin` SHA-256: `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`
- selected sensor mode: 3840×2160 @ 30 fps, line length 6752, nominal FLL 3554.

## Count-1 convergence → sensor lane

`CAECXConvergence::ConvergeSensorExposures @ 0x1803d13f0`:

- `0x1803d141c`: load Short log from `+0xa0`.
- `0x1803d1448`: seed internal sensor slot `+0x100` with Short.
- `0x1803d144c..1474`: active count 1 skips the multi-exposure loop.
- `0x1803d1574..159c`: fill remaining internal slots from the first slot.
- `0x1803d1788..17d8`: copy those internal slots to S1..S4.

Therefore the ordinary count-1 sensor lane is Short; final S1..S4 equal Short for this path.

## Line-readout time

`CamX::ImageSensorData::GetLineReadoutTime @ 0x18071a208`:

- `0x18071a254`: load line/frame timing words.
- `0x18071a260`: 32-bit multiply.
- `0x18071a264..26c`: widen to double, multiply maxFPS, `FCVTZU` integer VT clock.
- `0x18071a27c..28c`: `(lineLength & 0xffff) * 1e9 / VTclock`.

Mode2 yields:

- pixels/frame = 23,996,608,
- VT clock = 719,898,240 Hz,
- line time = 9379.103357719003 ns,
- double bits = `0x40c2518d3ad36374`.

## Line-count rounding

SensorNode around `0x1803591f8..288` converts exposure time to double, divides by line-readout time, applies the minimum-line constraint, then calls the common double→integer helper before storing `x20+0x10`.

The helper reaches `0x1800014c0`:

`FRINTA d0,d0`

followed later by integer conversion.  CQ therefore uses nearest/ties-away semantics, not floor/truncation.

## FLL policy

SensorNode `0x180359830..8b8` computes the containment limit and distinguishes special policy codes 7/8.  The bounded live captures prove the ordinary values rather than inferring them:

### CQ2

At the unconditional selected-sensor `vertOffset` load:

- `w27 = 8`,
- selected object `+0x178 = 8`.

### CQ3

At `0x180359838`:

- nominal `w24/FLL = 0x0de2 = 3554`,
- `w27/vertOffset = 8`,
- pre-policy linecount = `0x0de0 = 3552`,
- policy object `+0xb888 = 8`,
- extra offset `+0xb948 = 0`.

### CQ4

Immediately before the finalized exposure record is submitted toward the custom sensor callback:

- linecount = `0x0de0 = 3552`,
- FLL = `0x0de8 = 3560`,
- gain bits = `0x3f800000`,
- exposure time = `0x01fc4ec4 = 33,312,452 ns`.

Thus ordinary policy 8 extends FLL to `linecount + 8` once linecount exceeds 3546.

## IMX681 callback

AJ proves the active custom callback RVAs and register contract:

- CalculateExposure RVA `0x870ee0`,
- FillExposureSettings RVA `0x871000`,
- FLL register `0x033d`,
- coarse integration `0x0229`,
- analogue gain `0x0204`,
- global digital gain `0x020e`.

FillExposureSettings clears coarse-integration bit 0 before emitting the three exposure bytes.  CQ mirrors this after the SensorNode FLL decision.

## Live Linux transport retained

AP's retained result is `PASS_LIVE_CONTROLS_AND_PAIRED_AUDIT` and contains the already-executed exact group-held transaction:

`AM request controls: FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0`

CQ does not rerun AP or modify permissions on AP's root-owned capture binaries.

## Active T681 range correction

AQ's 2026-09-10 same-machine read-only FrameServer recapture pins the active T5 header at controller `+0x190` and, in the same controller object, min gain `1.0`, min time `37,516 ns`, max gain `92.0`, max time `66,666,664 ns`, and policy `+0x1a0=0`. The recapture ZIP SHA-256 is `809e7d58ba5605cbd5f98bcc2e2b41c12843dcc79e91cf2fd86e43647a9e8c67`. CQ therefore accepts CH's corrected active range directly; it no longer accepts the artificial 184x gain domain produced by the superseded 33.333 ms cap.
