# Static proof anchors

Pinned binary SHA-256:
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

## Property identity table

The property-name resolver for `0x30000000`-namespace IDs uses the pointer table rooted at VA `0x181147b20`.

- table index 0 pointer: `0x18141a250`
- string at `0x18141a250`: `PropertyIDAECFrameControl`
- table index 29 pointer: `0x18141a418`
- string at `0x18141a418`: `PropertyIDSensorCurrentMode`

Therefore `0x30000000 == PropertyIDAECFrameControl` and `0x3000001d == PropertyIDSensorCurrentMode`.

## SensorNode request and fetch

`CamX::SensorNode::ExecuteProcessRequest` entry region starts at `0x180350580`.

Active request-ID extraction:

- `0x1803505b8`: preserve incoming execute request (`x1`)
- `0x1803506e4..0x1803506f8`: follow request wrapper and load inner record qword `+0x8`
- `0x180350700`: save that active request ID at local `sp+0x78`

AEC property dependency/fetch:

- `0x180351380`: materialize literal `0x30000000`
- `0x180351384`: insert it into SensorNode dependency/property state
- `0x1803515ec`: set six-property array root to VA `0x18169d960`
- `0x18169d960`: first uint32 is `0x30000000`
- `0x180351600`: zero `sp+0x330..+0x33f`
- `0x18035160c`: zero `sp+0x340..+0x34f`
- `0x180351638`: item count = 6
- `0x180351640`: `x3 = sp+0x330` request-offset array
- `0x180351650`: `x2 = sp+0x300` result array
- `0x180351654`: `x1 = property/tag array`
- `0x180351660`: generic resolver call
- `0x180351664`: first returned pointer = `[sp+0x300]`

The first request offset is therefore zero.

## Generic request arithmetic

Generic resolver entry: `0x1805d4a40`.

On the no-auxiliary-array path used here:

- `0x1805d4c2c..0x1805d4c38`: load the current per-property requested offset (`x24`) from the offset array
- `0x1805d4c3c..0x1805d4c40`: load the current request-context value
- `0x1805d4c44`: `sub x19, x8, x24`

Thus `targetRequest = currentRequestContext - requestedOffset`. The first AECFrameControl offset is zero.

## AEC publisher request key

AEC stats-processing entry: `0x1808356e0`.

- `0x180835708`: `x20 = x1` incoming request object
- `0x180835820`: read request object's `+0x8` qword
- `0x1808358e8`: reload the same request object's `+0x8` qword
- `0x1808358f8`: store it at `CAECStatsProcessor+0x6008`

`CAECStatsProcessor::PublishPropertyPoolFrameControl` starts at `0x18083a0c0` and later reads processor `+0x6008` as the request key for the publication diagnostic/property flow.

Independent strings in the DLL include:

- `PropertyIDAECFrameControl`
- `CamX::CAECStatsProcessor::PublishPropertyPoolFrameControl`
- `AEC: Publish FrameControl for ReqId=%llu ...`
- `Sensor[%d]:Failed to get PropertyIDAECFrameControl, RequestID=%llu [%d]`

## Scope

AT proves the software property-pool request offset is zero. It does not yet assign optical-frame visibility to a request key. Sensor command queuing, group hold, register write timing, and the IMX681 latch boundary remain downstream work.
