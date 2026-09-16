# E004fa: native selection metadata

Only driver change: implement the standard read-only V4L2 selection API for this
fixed full-array mode. Native size, bounds, default and current crop are all
(0, 0)/644x604, including border pixels. This matches the verified board readout
and the frozen ST reference driver's selection convention. No new crop mode,
optical active-area characterization, orientation or register writes are added.

One fresh boot: stock libcamera discovery must no longer log failing rectangle
queries. Query all four targets directly through v4l2-ctl and check dimensions.
Then repeat the successful E004ez stock cam capture: exactly 16 full consecutive
R10_CSI2P frames, applied 1000-line exposure/unity gains, clean kernel, stop and
autosuspend. Golden return and retirement are required. No same-boot retry.
Missing sensor helper/properties and monochrome processing remain separate work.

Reference: src/front-ir-vd55g0/st-vd55g0/vd55g0.c, vd55g0_get_selection(),
and the E004a-derived full-array ROI in native/vd55g0-mode.h.

## Result and evidence recovery

All four selection queries passed; libcamera no longer logs failed rectangle
queries. Stock cam captured 16 consecutive full buffers and the sensor suspended.
The original runtime gate returned FAIL_HEALTH_OR_POWER because its line-count
slice of dmesg was empty. Preserve that JSON and KERNEL.txt without rewriting them.
The boot had been idle for over six hours before capture; ring-buffer rollover
is a plausible explanation for why line-count offsets failed.

The persistent journal for the exact consumed boot and bounded capture time
recovers initialization, start, applied 1000-line/unity controls, stop and physical
power-off, with no kernel fault/warning. JOURNAL-RECOVERY.json records the query
and independent checks. Golden returned and the candidate was retired. Thus the
hardware/selection gate passed with recovered evidence; the live collector failed.
Do not reuse this identity. Replace the unsafe slicing in the next candidate.
