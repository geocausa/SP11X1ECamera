# E003i AW — Windows sensor request submission boundary

Status: **PASS (static/offline) — CamX sensor programming preserves request ID `F` through `SensorNode::CreateSensorUpdatePacket`, packet commit and the low-level submit boundary; the exact front-sensor KMD then schedules queued exposure packets relative to its SOF coordinate.**

AW follows AV without performing a camera stream or reboot. It intentionally does **not** collapse the KMD scheduling rule into an optical `F+N` claim yet.

## Exact binaries

- `QcDeviceMFT8380.dll` SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- `surfacecamfrontsensor8380.sys` SHA-256 `80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`

## Current request remains current through SensorNode

`SensorNode::ExecuteProcessRequest` starts at `0x180350580`. The incoming request object is preserved, and at `0x1803506f8` CamX loads the qword at request-object `+0x8`; `0x180350700` saves that qword at `sp+0x78`.

Immediately before the AEC ApplyGains path, `0x180351bd8` reloads `x26 = [sp+0x78]`. The ApplyGains diagnostic receives `x26` as its `%llu RequestID`, and the sensor-update call at `0x180351ed8..0x180351f2c` passes that same value as argument `x1` to `CreateSensorUpdatePacket` (`0x18035a978`).

Inside `CreateSensorUpdatePacket`, `0x18035a9a8` preserves `x1` as `x24`. That request ID is used by the request-indexed packet path, retained in the `sending packet ... requestId:%llu` diagnostic, followed by `Packet::CommitPacket` and the common low-level packet submission wrapper. There is no user-space request renumbering between AEC/CamX request `F` and the sensor packet tagged `F`.

## Exact front-sensor KMD SOF coordinate

`CameraSensorDriver_NotifySOF` in the exact SP11 front-sensor driver stores:

- current SOF request ID at driver state `+0x430`,
- current SOF subrequest ID at `+0x438`,
- HDR mode at `+0x440`.

The adjacent exact diagnostic names those inputs `Req ID`, `SubRequest ID`, and `hdrMode`.

`CameraSensorDriver_ProcessExposureUpdate` identifies queued exposure-buffer fields `+0xc/+0x10` as `reqID/subRequestId` through its own dequeue diagnostics. In the selection branch at `0x140008368..0x1400083ac`, the driver subtracts current SOF request from queued request. For `hdrMode == 1`, the apply branch requires:

`queuedReq - currentSOF == 1`.

So a queued exposure packet tagged `F` is selected on that path while the KMD's current SOF request coordinate is `F-1`.

## Delay-info handoff remains exact

The MFT obtains the active sensor's 0x48-byte delay record from `sensorDriverData+0x318`, logs linecount/gain/maxPipeline/frameSkip, and passes the record through the sensor acquire wrapper. AV already proved the IMX681 record is `2/2/2`, `maxPipeline=2`, `frameSkip=0`.

AW does not yet assert how the KMD's `F-1` apply point combines with `maxPipeline=2` to label the optical exposure frame. That reconciliation is the next boundary; treating `maxPipeline=2` as an unconditional extra `F+2` after the user-space submit would double-count scheduling.
