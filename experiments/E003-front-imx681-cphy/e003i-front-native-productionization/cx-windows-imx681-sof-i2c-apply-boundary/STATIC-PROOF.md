# CX static proof

Pinned `surfacecamfrontsensor8380.sys` SHA-256: `80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`.

## SOF coordinate and selection

`CameraSensorDriver_NotifySOF` stores request/subrequest/HDR state at driver `+0x430/+0x438/+0x440`.

At `0x140008360..0x1400083a8`, `CameraSensorDriver_ProcessExposureUpdate` loads current SOF request from `+0x430`, queued request/subrequest from queue-record `+0x0c/+0x10`, computes `queuedReq-currentSOF`, requires `==1`, then requires `hdrMode==1` for the ordinary branch.

## Selected packet reaches transport synchronously

`0x140008480..0x140008488` passes the selected queue record to `0x140009860`.

Inside `0x140009860`, `0x140009998..0x1400099cc` walks the register list. At `0x1400099b4/0x1400099b8` it loads 16-bit data/register fields and calls `0x14000abc8` for each pair.

`0x14000abc8` constructs the low-level transaction and calls `0x14000b7a8`; that wrapper calls `0x140003aa0`, which invokes its backend callbacks and returns synchronously. The exact KMD strings name both `CameraSensorDriver_SubmitI2CCmd()` and the post-apply `SensorLastConsumedReqId` bookkeeping.

Thus packet `F` is not left in another request-numbered software queue after the `F-1` SOF selection: the selected record is walked into the I²C transport in that handler before consumed bookkeeping.

## Bounded claim

CX does **not** assert `optical frame = F`, `F+1`, or `F+2`. Sensor-side shadow-register/group-hold release timing relative to the physical frame boundary remains the one open edge. AV's `maxPipeline=2` must not be blindly added after the KMD apply point because AW already warned that doing so can double-count scheduling.
