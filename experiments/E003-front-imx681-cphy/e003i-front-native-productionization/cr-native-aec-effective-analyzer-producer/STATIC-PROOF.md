# CR static / oracle proof anchors

## Pinned artifacts

- `QcDeviceMFT8380.dll` SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- `com.surface.tuned.ffc_imx681.bin` SHA-256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Default analyzer set and effective StatsCalculator inputs

The default analyzer sequence contains the relevant non-Frame analyzers:

`SatPrevSA, DarkPrevSA, BrightenImgSA, ExtremeColorSA, ShortSatPrevSA, LongDarkPrevSA, IlluminanceSA`.

The parsed calculator records reduce their effective ordinary non-Frame StatsCalculator dependencies to Bank4 IDs `{6,7,8,19}`.  BW independently proves these IDs are:

- 6 SaturateStatsRatio,
- 7 SatPrevHighPCTLLuma,
- 8 DarkPrevLowPCTLLuma,
- 19 ShortSatPrevHighPCTLLuma.

## Dead zero-confidence candidates

The confidence value trees for the following configured analyzers contain only exact zero leaves:

- BrightenImgSA: trigger tree 4013 -> leaf 4014,
- ExtremeColorSA: trigger tree 6001 -> leaf 6002,
- LongDarkPrevSA: trigger tree 4496 -> leaf 4497.

Their component weight is nonzero, but the produced confidence value itself is exact `+0.0f`.  BY's method-11 implementation ignores candidates whose effective weight is zero, so CR may canonicalize all three to `{0,0}` without changing aggregation.

## Calculator-unit grammar

`CTargetAnalyzerComponent` runtime around `0x1803f10b0..0x1803f1310`:

- `0x1803f10b4`: load calculator method.
- method 1 branch at `0x1803f1134`.
- `0x1803f1158/1160`: fetch first trigger coordinate through the generic databank getter.
- `0x1803f1188/1190`: fetch second trigger coordinate.
- `0x1803f11a8`: call common interpolation engine `0x1803acf40`.
- method 0 direct path at `0x1803f11c4/11cc`: fetch direct databank descriptor at unit `+0x4`.

The 72-byte serialized calculator therefore contains two 36-byte units with direct and interpolation descriptors matching the tuning parser used by CR.

## Component aggregation method 3

The aggregation jump table at `0x1803f0c94` maps method 3 to `0x1803f068c`.  The body compares the candidate lane against the current aggregate (`FCMPE`) and stores the smaller value.  CR therefore implements Illuminance confidence aggregation as lane-wise minimum.

## Trigger 9:28

AnalyzerManager update around `0x1803e3b90`:

- `0x1803e3b94`: load selected retained-history Short qword from `history+0x28`.
- `0x1803e3bb4`: `UCVTF s16,x8` converts it to float32.
- the following trigger publication records data ID `0x1c` (28) and calls `SetDataTriggers @ 0x1803d6700`.

Thus trigger `9:28` is selected retained-history Short exposure converted `uint64 -> float32`.

## Trigger bank scalar geometry

Bank9 getter branch around `0x1803d5f84` computes `base + dataID*16` and loads the float at record `+0x0c`.  Trigger `9:63` is therefore the unique 4-byte scalar at `bank9_base + 63*16 + 0x0c`.

## Same-machine CR63 oracle

The preserved Windows evidence is hash-pinned by `verify-cr.py`.  The bounded ordinary front-preview run hit the Bank9 read for data ID 63 and showed:

- `9:63` bits `0x00000000` (`+0.0f`),
- Lux `9:8` simultaneously live/nonzero.

A hardware write watchpoint was then placed on that exact 4-byte slot.  No write was observed from the first read through stream stop/dispose.  This is intentionally scoped to ordinary DefaultSequence preview; it is not a claim about special modes.

## Arithmetic topology

The parsed analyzer arithmetic confirms:

- SatPrev/DarkPrev/ShortSatPrev use target-high selector 2, Frame luma/target normalization and their method-2 trees before final AdjRatio publication.
- Illuminance uses `9:28`, a method-2 operand keyed by Lux and `9:63`, the fixed `1,000,000` divisor, FrameSA target/AdjRatio, its correction method-2 tree, and final multiplication by Frame AdjRatio.

CR preserves the Windows float32 arithmetic/interpolation order with `-fno-fast-math -ffp-contract=off` and volatile elementary operations.
