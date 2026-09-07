# BD static proof anchors

Pinned hashes:

- `QcDeviceMFT8380.dll`: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- `com.surface.tuned.ffc_imx681.bin`: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Native field identity

`CAnalyzer::SetAnalyzerTuning` at `0x1803f18d8`:

- `0x1803f192c`: expanded tuning `+0x18`
- `0x1803f1930`: store to `CAnalyzer+0x28`
- `0x1803f1934`: expanded tuning `+0x1c`
- `0x1803f1938`: store to `CAnalyzer+0x2c`

`CAnalyzer::RunAnalyzer` returns `CAnalyzer+0x8` at `0x1803f18a8`. Therefore object `+0x28` is returned result `+0x20`.

`CAnalyzerManager::RunAnalyzer` at `0x1803b21f0` consumes that returned field:

- `0x1803b2684`: load result `+0x20`
- `0x1803b26b0`: load result `+0x20`
- `0x1803b26b4`: call `UtilExposureTypeTuning2Enum`

This proves object `+0x28` is tuning **exposureType**.

Inside `CAnalyzer::RunAnalyzer`:

- `0x1803f15e0`: load object `+0x2c`
- `0x1803f15f0`: call `UtilExposureTypeTuning2Enum`
- `0x1803f15f4`: add converted type × 8 to the source-vector pointer
- `0x1803f15fc`: load selected source exposure as double

This proves object `+0x2c` is **sourceType** for the SI calculation.

## SI scalar

Key instructions:

- measured: `0x1803f1694` load `s17` from `+0x10`
- epsilon: `0x1803f1698` load float literal at `0x1803f18d0` (`0x33d6bf95`)
- clamp: `0x1803f169c..16a0`
- target low: `0x1803f16a4` load `s16` from `+0x18`
- float32 ratio: `0x1803f16a8 fdiv s16,s16,s17`
- promote: `0x1803f16ac fcvt d16,s16`
- multiply selected source exposure: `0x1803f16b4 fmul d16,d16,d8`
- integer conversion: `0x1803f16b8 fcvtzu x8,d16`
- SI store: `0x1803f16bc str x8,[x19,#0x20]`

The preceding analyzer aggregations place measured luma at object `+0x10`, target low/high at `+0x18/+0x1c`, and confidence at `+0x14`. Because the function returns `this+8`, these are result `+0x08`, `+0x10/+0x14`, and `+0x0c` respectively.

## Compact tuning cross-check

The compact Parameter Bin stores 32-bit descriptor references while the expanded runtime struct contains native pointers. Compact and native byte offsets must therefore not be equated directly.

After the analyzer description/name length+reference pairs, the next two compact scalar fields show:

- ordinary Frame/Safe/Short/Long: `(exposureType, sourceType)` = `(1,3), (1,3), (0,3), (2,3)`
- HDR Safe/Short/Long: `(1,1), (0,0), (2,2)`

The native consumers above establish the field names; the cross-family tuning pattern independently confirms them.
