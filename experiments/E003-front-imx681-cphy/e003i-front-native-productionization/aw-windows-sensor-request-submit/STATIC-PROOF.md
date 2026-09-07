# Static proof anchors

## MFT / CamX

- `0x180350580`: `SensorNode::ExecuteProcessRequest` entry.
- `0x1803506f8`: load request-object `+0x8`.
- `0x180350700`: save exact qword at `sp+0x78`.
- `0x180351bd8`: restore `x26 = [sp+0x78]` before ApplyGains.
- `0x180351d34`: ApplyGains diagnostic request argument = `x26`.
- `0x180351ed8`: `x1 = x26` for sensor update.
- `0x180351f2c`: call `CreateSensorUpdatePacket`.
- `0x18035a9a8`: helper preserves request argument in `x24`.
- `0x18035be78`: committed packet path.
- `0x18035c048`: low-level packet submit wrapper.
- `0x18035c8c0`: load delayInfo pointer from active sensor tree `+0x318`.
- `0x18035c8f8`: record size = `0x48`.
- `0x18035c910..0x18035c91c`: load `maxPipeline`, `frameSkip`, gain and linecount for exact diagnostic before acquire handoff.

## Exact `surfacecamfrontsensor8380.sys`

`NotifySOF`:

- `0x1400058b0`: load incoming SOF request ID.
- `0x1400058b4`: load subrequest/HDR mode.
- `0x1400058c8`: `stp x23,x22,[state+0x430]`.
- `0x1400058d4`: store HDR mode at `state+0x440`.

`ProcessExposureUpdate`:

- dequeue diagnostic uses queued record `+0xc/+0x10` as `reqID/subRequestId`.
- `0x140008368`: reload queued `reqID/subRequestId`.
- `0x14000836c`: `queuedReq - currentSOF + subrequest` special-case arithmetic.
- `0x140008394`: recompute `queuedReq - currentSOF`.
- `0x140008398`: compare result with `1`.
- `0x1400083a0..0x1400083a8`: require `hdrMode == 1` for that branch.
- `0x1400083ac`: enter dequeue/apply path.
- `0x140008484`: pass dequeued exposure record to the execution helper.
- `0x14000849c..0x1400084bc`: copy queued req/subreq to last-consumed state.
- `0x1400084cc`: exact post-apply diagnostic reports those last-consumed IDs.

Closed law for the `hdrMode == 1` branch:

`KMD apply packet(req=F) when currentSOF = F-1`.

This is a scheduling-coordinate proof only. Optical frame identity remains deliberately open.
