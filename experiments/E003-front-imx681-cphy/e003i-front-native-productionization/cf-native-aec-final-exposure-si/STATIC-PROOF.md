# Static proof

Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd9de785509c1fbebc975facc5286f12865cf675f1d`

Pinned tuning SHA256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Source lane

The pinned analyzer table records:

- SafeAggSA analyzer 3: `exposureType=Safe`, `sourceType=3`;
- ShortAggSA analyzer 4: `exposureType=Short`, `sourceType=3`;
- LongAggSA analyzer 5: `exposureType=Long`, `sourceType=3`.

BD already proves tuning source type 3 maps through `UtilExposureTypeTuning2Enum` to internal lane S1. At `0x1803f15e0..0x1803f15fc`, `CAnalyzer::RunAnalyzer` converts `sourceType`, indexes the seven-lane source vector, and loads the selected source exposure as double.

## Positive phase-2 AdjRatio publication

At `0x1803f1608..0x1803f168c`, Windows scans arithmetic records for enabled phase 2, reads the configured bank/data scalar, and if the value is positive moves that float32 value directly into `s16` as AdjRatio. BZ closes the final publications as Safe `3:9`, Short `3:11`, Long `3:13`; CE reproduces those values natively.

## Qword conversion

The final instruction sequence is:

- `0x1803f16ac fcvt d16,s16` — promote float32 AdjRatio to double;
- `0x1803f16b4 fmul d16,d16,d8` — multiply by selected S1 double;
- `0x1803f16b8 fcvtzu x8,d16` — truncate positive finite double to unsigned qword;
- `0x1803f16bc str x8,[x19,#0x20]` — store result SI.

CF restricts itself to positive finite in-range products, exactly the ordinary path used here. The native C conversion `(uint64_t)product` is checked against an independent IEEE-binary64/truncate reference for 17,216 cases, including 256 source values at the `2^53` integer precision boundary.
