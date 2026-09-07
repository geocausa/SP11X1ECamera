# BG static proof anchors

Pinned evidence:

- `QcDeviceMFT8380.dll` SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- `com.surface.tuned.ffc_imx681.bin` SHA-256 `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

## FrameSA target component

The compact 0x8c FrameSA analyzer record groups calculator references with the description at the end of each component block. The three ordinary FrameSA blocks are:

- calculators 3595 / description 3600 `FrameSA_Luma`
- calculators 3601 / description 3606 `FrameSA_Target`
- calculators 3607 / description 3612 `FrameSA_Confidence`

Therefore the `0.001f` terminal leaf under calculators 3607 is confidence data, **not targetLow**.

Calculators 3601 carry trigger key `(9,8)` and the TwoFloats target terminal table 3603:

| trigger interval | targetLow | targetHigh |
| --- | ---: | ---: |
| 0..140 | 55 | 55 |
| 160..270 | 50 | 50 |
| 300..360 | 46 | 46 |
| 370..410 | 40 | 40 |
| 420..460 | 40 | 40 |
| 500..1000 | 30 | 30 |

`CAECXTwoFloatsXML::InterpCoreData` at `0x1803adac0` linearly interpolates both float members. FrameSA has one target calculator and aggregation mode zero, so this interval becomes the final analyzer target pair. `CAnalyzer::RunAnalyzer` commits it at object `+0x18/+0x1c`; the SI path uses `targetLow` from `+0x18`.

## Lux trigger identity

Startup-exposure code at `0x180378cec..0x18037904c` copies controller `+0x1671c` to local `+0x7c` when positive, then builds dataID 8 plus type/bank 9 and calls the trigger-DB write virtual slot `+0x70`. Its unique diagnostic is `Issue in setting luxindex to trigger DB`.

Normal `runConvergence` at `0x18037501c` constructs the packed key `9 | (8 << 32)` and calls trigger-DB read slot `+0x58`. Two later snapshot/control consumers independently read the same packed key and consume the returned float.

AB independently proved the request-local `CAnalyzerAlgorithm001::RunAlgorithm` Lux computation bit-exactly and established that each Algorithm001 result appears at the second subsequent publication. BG reuses that evidence but does **not** claim that the startup direct-write helper is the steady-state writer.
