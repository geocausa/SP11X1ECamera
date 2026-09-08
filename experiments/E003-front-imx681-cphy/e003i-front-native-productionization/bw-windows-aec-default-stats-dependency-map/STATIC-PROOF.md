# BW static proof

Pinned tuning entry `3334` is the `BankIDStatsCalculator` data dictionary: 69 records x 16 bytes. Pinned entry `7120` is the metering `statsCalculators` array: 55 records x 92 bytes. In every record, word 0 is the calculator ID used by the active-calculator sequence; word 13 is its primary StatsCalculator-bank publication ID.

`DefaultActiveCalculatorSequence` is tuning entry 2621 and is exactly:

`11,12,15,16,23,24,45,46,52,53,47,54,55,56,57,58,60,81,83,85,61,62,63,64,65`.

The target-producing default analyzers have these exact bank-4 dependencies, extracted from their component calculators and four arithmetic-operator source descriptors:

- FrameSA: 2 FrameLumaBE16x16
- SatPrevSA: 7 SatPrevHighPCTLLuma
- DarkPrevSA: 8 DarkPrevLowPCTLLuma
- BrightenImgSA: 12 BrightenImgPCTLLuma, 11 BrightenImgSatPCTLLuma
- ExtremeColorSA: 42/48/49 green-zone ratios, 41 red ratio, 43 blue ratio
- ShortSatPrevSA: 19 ShortSatPrevHighPCTLLuma
- LongDarkPrevSA: 20 LongDarkPrevLowPCTLLuma
- IlluminanceSA: 6 SaturateStatsRatio
- SafeAggSA / ShortAggSA / LongAggSA luma: 1 AvgLumaBE16x16

The union is 14 named statistics IDs. FaceSA, TouchSA, DepthSA, TrackerSA and SaliencySA are configured SafeAgg candidates in BV but are absent from the normal `DefaultSequence`; their absent-publication semantics are deferred rather than assumed.
