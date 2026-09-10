# E003i CQ — native AEC output → IMX681 control adapter

Status: **PASS (Windows oracle + static/offline native differential)**.

CQ closes the last ordinary-preview arithmetic seam between the self-contained native AEC loop and the already-live-proven Linux IMX681 control cluster.  The public input is CH/CP's ordinary T681 result for the canonical **Short** lane; the output is the exact request-local sensor tuple needed by the Linux driver plus Windows' residual ISP gain:

`{frameLengthLines, VBLANK, coarse exposure lines, analogue code, global-digital code, ISP gain}`.

No Linux camera module load, STREAMON, sensor write, MMIO or new Linux camera runtime is performed by CQ.  Three bounded Windows oracle runs were used to remove the remaining SensorNode timing/FLL ambiguity, and SP11 was returned to the unchanged Golden Linux boot afterward.

The files under `windows-oracle/` are deliberately preserved as their original Windows bytes (including CRLF/UTF-16 and debugger-log spacing).  CQ's local `.gitattributes` marks only that evidence directory as non-text so Git does not rewrite it or apply source whitespace rules to captured bytes.

## Single-exposure lane

BC proves the active ordinary front path has `activeExposureCount == 1`.  `ConvergeSensorExposures` seeds its first internal sensor slot from **Short**, skips the multi-exposure loop, and copies that first slot through S1..S4.  The final seven convergence lanes are therefore:

`Short, Long, Safe, Short, Short, Short, Short`.

CQ consequently consumes CP's `short_arbitration` as the canonical single-sensor T681 result.  This is not an assumption that all AEC history lanes are generally aliases; it is scoped to the proven ordinary count-1 path.

## Exposure time → line count

Windows `CamX::ImageSensorData::GetLineReadoutTime` (`0x18071a208`) computes the selected mode's VT timing from:

- line length = `6752`,
- frame length = `3554`,
- max FPS = `30.0`,
- integer VT clock = **719,898,240 Hz**.

The resulting line-readout time is `9379.103357719003 ns`, exact double bits `0x40c2518d3ad36374`.  The separate `548.57 MHz` firmware field is the output pixel-clock value and is **not** the clock Windows uses for this exposure conversion.

SensorNode divides T681 exposure time by that line-readout time.  Its common conversion helper reaches `0x1800014c0`, which is `FRINTA d0,d0`: nearest integer, halfway cases away from zero.  For this positive-only domain that is round-half-up, not truncation.

## Ordinary FLL policy

CQ2/CQ3/CQ4 are same-machine bounded Windows oracle captures.  Together they prove:

- `vertOffset = 8`,
- ordinary policy code = `8`,
- `extraOffset = 0`,
- nominal FLL = `3554`,
- containment threshold = `3554 - 8 = 3546` lines,
- policy 8 extends FLL rather than clipping coarse integration when the threshold is exceeded.

The live CQ4 sample supplied gain `1.0f` and exposure time `33,312,452 ns`; Windows finalized `linecount=3552, FLL=3560`.  Thus CQ implements:

- `FLL = 3554` when rounded linecount `<= 3546`,
- `FLL = linecount + 8` otherwise.

Only after SensorNode finalizes that pair does the active IMX681 `FillExposureSettings` callback clear linecount bit 0.  CQ therefore exposes both the pre-even Windows linecount and the actual even sensor coarse-integration value.  At the **cold bootstrap** time (`33,333,332 ns`) the result is linecount `3554`, FLL `3562`, VBLANK `1402`, exposure `3554`. AQ's later same-machine range recapture pins the actual active preview maximum to `66,666,664 ns`; at gain 1 this maps to linecount `7108`, FLL `7116`, VBLANK `4956`, exposure `7108`.

## Gain conversion and corrected active T681 domain

AJ already mechanically closes the active IMX681 custom `CalculateExposure` and `FillExposureSettings` callbacks. CQ reuses that exact ordinary path:

- analogue code = truncation of `1024 - 1024/gain`, with the active `0x3c0` cap,
- analogue real gain reconstructed from that code,
- remaining gain assigned to Q8.8 global digital gain and capped at 15x,
- residual ISP gain retained exactly as float32.

AQ's 2026-09-10 read-only controller recapture corrects the old CQ integration assumption. The active preview range is **gain 1..92 and time 37,516..66,666,664 ns**. The earlier apparent 184x post-fit domain was created only because CH was fitting the 66.7 ms table knees against a stale 33.333 ms maximum and compensating with gain. With the address-proven active range, CH never needs that artificial compensation and CQ rejects gain above 92 or time above 66,666,664 ns.

## Verification

`verify-cq.py` pins the DeviceMFT and IMX681 firmware hashes, all CQ2/3/4 oracle hashes and clean holder exits, fresh-runs CP and AJ, checks AP's retained readable live-control evidence, and disassembles only the bounded Windows functions needed by CQ.  It then compiles CQ with strict floating-point settings and compares against AJ's independent Python oracle.

The deterministic corpus contains line-transition neighborhoods, T681 limits, the CQ4 live pair, and the AQ observed-pair gain.  It adds **65,536 seeded random valid `{gain,time}` cases** and **16,384 actual CH T681 outputs**.  Line/FLL/VBLANK/exposure/analogue/digital values match exactly, and ISP-gain float bits match exactly.

The next checkpoint should integrate `CP short_arbitration -> CQ controls` into a bounded Linux request/control producer while preserving the already-proven AP request scheduling and group-held driver transaction.  Continuous unrestricted AEC remains intentionally unclaimed until that bounded integration gate passes.
