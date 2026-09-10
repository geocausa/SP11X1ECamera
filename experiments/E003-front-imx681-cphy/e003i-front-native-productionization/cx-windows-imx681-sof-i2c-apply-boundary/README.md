# E003i CX — Windows IMX681 SOF → synchronous I²C apply boundary

Status: **PASS (static/offline)** — the exact SP11 front-sensor KMD selects ordinary exposure packet `F` when its current SOF request coordinate is `F-1`, then synchronously walks the selected packet's register/data list into the low-level I²C submit path before consumed-request bookkeeping.

This closes the remaining **software scheduling** ambiguity downstream of AW. It does **not** claim which optical image frame first contains the released IMX681 group-held settings.

The exact Windows front-sensor driver is SHA-256 `80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`.

For `hdrMode == 1`, `CameraSensorDriver_ProcessExposureUpdate` compares queued request ID with the request ID stored by `CameraSensorDriver_NotifySOF` and enters the ordinary apply path when `queuedReq - currentSOF == 1`. The selected record is passed at `0x140008488` to `0x140009860`; that routine iterates its register/data pairs and calls `0x14000abc8`, which constructs the low-level write request and synchronously descends through `0x14000b7a8 -> 0x140003aa0` before returning.

CW independently closes the Linux side as one four-control, group-held transaction using IMX681 `0x0104`. AV's configured `maxPipeline=2` remains a sensor-pipeline fact and is deliberately not added again after this KMD apply point.

Two independent locally retained linux-surface IMX681 implementations (`pr164`, `pr176`) corroborate `0x0104` as group parameter hold with ON → exposure fields → OFF ordering. They do not document first-frame visibility, so CX does not use them to invent an optical-frame label.

Next gate: a single bounded mid-stream exposure step with paired generation-tagged 3A/BHist evidence, issued immediately after a completed frame during VBLANK, to identify the first affected generation. No continuous AEC should be enabled by this checkpoint alone.
