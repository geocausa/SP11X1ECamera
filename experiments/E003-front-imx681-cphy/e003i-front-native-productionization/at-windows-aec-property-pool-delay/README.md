# E003i AT — Windows AEC property-pool request boundary

Status: **PASS (static/offline) — `PropertyIDAECFrameControl` is fetched by SensorNode with zero explicit request offset; AEC publication and SensorNode execution use the same CamX request-ID convention. Physical sensor apply/latch latency remains separate.**

AS closed the internal AEC history rule (`F-1` in contiguous steady state). AT closes the next software boundary between AEC output publication and SensorNode's AEC-frame-control fetch.

## Pinned Windows oracle

`/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll`

SHA-256:

`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

## Property identity

CamX's property-name table maps numeric property `0x30000000` to `PropertyIDAECFrameControl`. The same table maps `0x3000001d` to `PropertyIDSensorCurrentMode`; this corrects an earlier transient interpretation made while following a different SensorNode stack-slot reuse.

## SensorNode fetch

Inside `CamX::SensorNode::ExecuteProcessRequest`, the AEC dependency/property list inserts literal `0x30000000`. The later six-item generic resolver call uses:

- property/tag array: data rooted at `0x18169d960`, whose first element is `0x30000000`
- result array: `sp+0x300`
- request-offset array: `sp+0x330`
- item count: `6`

Before that call, `sp+0x330` is zero-initialized. Therefore the first property's explicit offset is exactly zero.

The generic resolver's direct-offset path reads each requested offset and forms the target request as:

`targetRequest = currentRequestContext - requestedOffset`

For `PropertyIDAECFrameControl`, `requestedOffset == 0`, hence:

`targetRequest = currentRequestContext`.

The first returned pointer at `sp+0x300` is carried into the AEC/sensor-control path and ultimately consumed by the gain/exposure application block. Failure text independently names this property: `Failed to get PropertyIDAECFrameControl, RequestID=...`.

## Publisher request key

The AEC stats processor entry receives its request object in `x1`. It reads the request ID from that object's `+0x8` field and stores the exact qword at `CAECStatsProcessor+0x6008`. `CAECStatsProcessor::PublishPropertyPoolFrameControl` later reads `+0x6008` for its publication/log request key.

SensorNode's execute path independently extracts its active request ID from the inner execute-request record's `+0x8` field. Thus both sides use the same CamX request-ID convention, while the property resolver adds no explicit frame subtraction for `PropertyIDAECFrameControl`.

## Closed software-boundary law

For CamX request `P` on the normal SensorNode AEC path:

1. AEC processing records request key `P` at processor `+0x6008`.
2. `PublishPropertyPoolFrameControl` publishes/logs using that request key.
3. SensorNode asks for `PropertyIDAECFrameControl` with explicit offset `0`.
4. The resolver therefore targets the current request context rather than `P-1`, `P-2`, etc.

So **the AECFrameControl property-pool lookup itself adds zero request frames of delay**.

This is deliberately not a claim that sensor exposure computed for request `P` is optically visible in image frame `P`. The downstream `ApplyGains` → sensor command → IMX681 register/group-hold/latch boundary is the next checkpoint.
