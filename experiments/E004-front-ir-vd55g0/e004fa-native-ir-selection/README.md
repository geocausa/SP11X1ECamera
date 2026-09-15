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
