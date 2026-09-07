# E003i AV — Windows IMX681 sensor-delay closure

Status: **PASS (static/offline) — the exact SP11 IMX681 sensor blob and the SHA-pinned Windows CamX parser agree on a common two-frame sensor pipeline delay: linecount=2, gain=2, frameLengthLines=2, maxPipeline=2; frameSkip=0.**

AU established `AEC FrameID F = CamX request ID P`. AV closes the sensor-delay configuration and the software-history alignment immediately downstream of the AEC frame-control path.

## Pinned oracles

Windows CamX/MFT DLL:

`/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll`

SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

SP11 IMX681 sensor module:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin`

SHA-256: `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`

## Exact serialized delay record

The blob is a `QTI Chromatix Header` / `Parameter Parser V3.4.0` binary. Its generated `delayType` record is 52 bytes and, as 13 little-endian dwords, is:

`1, 0xb94, 1, 0xb95, 1, 0xb96, 1, 0xb97, 2, 0, 0, 0, 0xb98`.

The Windows DLL's generated parser for each 0x48-byte runtime delay record is at `0x18087ff50`. It maps the four optional child values to runtime offsets `+0x08`, `+0x14`, `+0x20`, and `+0x2c`, then consumes the next two dwords directly into `+0x30` and `+0x34`.

Decoding the exact blob with that exact parser layout gives:

- selector / delay type value: `0`,
- linecount delay (`+0x14`): `2`,
- gain delay (`+0x20`): `2`,
- frameLengthLines/FLL delay (`+0x2c`): `2`,
- maxPipeline (`+0x30`): `2`,
- frameSkip (`+0x34`): `0`.

The `maxPipeline=2` value is therefore not borrowed from a generic Qualcomm XML example; it is present in the exact SP11 serialized `delayType` payload and is loaded by the exact-build generated parser.

## SensorNode alignment law

`CamX::SensorNode::HandleDelayInfo` loads `maxPipeline` from runtime `delayInfo+0x30` and conditionally substitutes historical control values only when an individual field delay is non-zero **and less than** `maxPipeline`.

For the three exposure controls it implements the same law:

`history lookback = maxPipeline - fieldDelay`.

The equality branches are explicit:

- FLL compares `+0x2c` with `+0x30` and skips history lookup on `fieldDelay >= maxPipeline`,
- linecount compares `+0x14` with `+0x30` and skips on `>=`,
- gain compares `+0x20` with `+0x30` and skips on `>=`.

For IMX681, all three are exactly `2 == maxPipeline`. Therefore **HandleDelayInfo performs zero request-history realignment** for FLL, linecount, or gain on this configuration.

## Kernel handoff corroboration

The same DLL has the diagnostic:

`Sensor Delay Info sent to Kernel: linecount = %d, gain = %d, maxPipeline = %d, frameSkip = %d.`

Its call site reads those values from the same runtime record at `+0x14`, `+0x20`, `+0x30`, and `+0x34`, confirming the field identities used above.

## Closed result

For the normal IMX681 exposure-control path on this exact SP11 Windows build:

**sensor application pipeline depth = 2 frame intervals, and CamX adds no extra per-field historical request shift because linecount=gain=FLL=maxPipeline=2.**

Combined with AU, the software coordinate is now `AEC FrameID F = CamX request F`, followed by the IMX681 two-frame sensor application pipeline. The final optical-frame label/latch statement is intentionally kept separate until the group-hold transaction is joined to frame-boundary semantics.
