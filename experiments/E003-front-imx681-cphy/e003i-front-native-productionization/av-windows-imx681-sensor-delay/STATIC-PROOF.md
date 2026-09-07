# AV static proof ledger

## Oracle hashes

- `QcDeviceMFT8380.dll`: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- `com.surface.sensormodule.ffc_imx681.bin`: `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`

## Blob

Chromatix data segment: offset `0x298b4`, size `0xa464`.

Generated delay element: descriptor ID `0xb94`, name `delayType`, data offset `0x9fe2`, size `52`.

Payload dwords:

`[1, 0xb94, 1, 0xb95, 1, 0xb96, 1, 0xb97, 2, 0, 0, 0, 0xb98]`

Decoded through the exact generated parser:

`selector=0, linecount=2, gain=2, frameLengthLines=2, maxPipeline=2, frameSkip=0`.

## Generated Windows delay-record parser

Function: `0x18087ff50`.

Relevant runtime destinations:

- `0x1808801c8` / call `0x1808801cc`: child scalar -> record `+0x14` (linecount),
- `0x1808802bc` / call `0x1808802c0`: child scalar -> record `+0x20` (gain),
- `0x1808803b0` / call `0x1808803b4`: child scalar -> record `+0x2c` (FLL),
- `0x1808803dc..0x180880404`: direct dword -> record `+0x30` (maxPipeline),
- `0x180880414..0x180880448`: direct dword -> record `+0x34` (frameSkip).

## SensorNode::HandleDelayInfo

- `0x18035a2c0`: loads maxPipeline from `+0x30`.
- FLL: `0x18035a2ec` loads `+0x2c`; `0x18035a2f4..0x18035a2f8` skips when zero or `>= maxPipeline`; `0x18035a2fc` computes maxPipeline-FLL only for the strict-less case.
- linecount: `0x18035a348` loads `+0x14`; `0x18035a350` loads `+0x30`; `0x18035a354..0x18035a358` skips at `>=`; `0x18035a35c` computes the lookback only below max.
- gain: `0x18035a3c8` loads `+0x20`; `0x18035a3d0` loads `+0x30`; `0x18035a3d4..0x18035a3d8` skips at `>=`; `0x18035a3dc` computes the lookback only below max.

Since all three field delays are `2` and maxPipeline is `2`, none of the three strict-less branches executes.

## Scope

This proves the exact configured sensor pipeline delay and no extra SensorNode history substitution. It does not yet define which externally numbered optical frame first contains the newly latched group-held register values.
