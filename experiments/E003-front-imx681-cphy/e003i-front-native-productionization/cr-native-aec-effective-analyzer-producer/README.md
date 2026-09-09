# E003i CR — native effective default-analyzer producer

Status: **PASS (static/offline + same-machine Windows oracle + native differential)**.

CR removes the final opaque analyzer-candidate seam from the ordinary front-camera AEC recurrence.  The caller no longer supplies seven precomputed SceneAnalyzer candidates.  For uninterrupted ordinary `DefaultSequence`, CR accepts only the state/statistics that Windows actually consumes and produces CE's complete eight-candidate input:

`{Lux, Frame luma/target, delayed Short exposure, Bank4:6,7,8,19} -> CE analyzer candidates`.

The four non-Frame StatsCalculator values are:

- `4:6` SaturateStatsRatio,
- `4:7` SatPrevHighPCTLLuma,
- `4:8` DarkPrevLowPCTLLuma,
- `4:19` ShortSatPrevHighPCTLLuma.

`FrameSA` is reproduced in the same adapter because its target/luma pair is already present at this boundary.  `SatPrevSA`, `DarkPrevSA`, `ShortSatPrevSA`, and `IlluminanceSA` are evaluated with the exact Windows tuning trees and float32 arithmetic order.  `BrightenImgSA`, `ExtremeColorSA`, and `LongDarkPrevSA` are canonicalized to zero because their ordinary DefaultSequence confidence trees are exact `+0.0f`; Windows method-11 therefore ignores their values.

No Linux camera module load, STREAMON, sensor write, MMIO or new Linux camera runtime is performed by CR.  A bounded same-machine Windows oracle was used only to close the otherwise data-driven ordinary value of trigger `9:63`; SP11 returned to the unchanged Golden Linux boot afterward.

## Trigger-state reductions

### Trigger 9:28

The AnalyzerManager history materialization path publishes the selected retained-history **Short exposure qword** into trigger slot `9:28` using ARM64 `UCVTF` to float32.  CR therefore takes delayed Short exposure directly from the already-owned AEC history state; this is not a new sensor statistic.

### Trigger 9:63

Static analysis proves `9:63` is an external/table-driven trigger input used only by `IlluminanceSA` in the 52-analyzer default AEC program; no analyzer arithmetic writes it and there is no literal-ID writer in the AEC text region.

The bounded Windows CR63 oracle therefore observed the actual ordinary front-preview slot directly.  On the live read, `9:63` was exact `0x00000000` (`+0.0f`) while Lux `9:8` was live.  A hardware write watchpoint on the exact 4-byte `9:63` slot observed no subsequent write through stream stop/dispose.  CR binds that ordinary DefaultSequence input to `+0.0f` only; special/non-default modes remain out of scope.

## Component/calculator grammar

The common `CTargetAnalyzerComponent` evaluator was reduced mechanically:

- calculator-unit method `0`: direct databank read,
- calculator-unit method `1`: evaluate the common two-coordinate interpolation tree,
- component aggregation method `3`: lane-wise minimum.

The 72-byte calculator record is two 36-byte units.  For method 1, the serialized outer/inner bank-data descriptors feed the already-proven interpolation engine.  Arithmetic target operands for SatPrev/DarkPrev/ShortSatPrev use selector `2`, i.e. the target-high member.

## Effective ordinary analyzers

CR evaluates the following live candidates:

- **SatPrevSA**: target-high/Lux program, normalized against FrameSA and Bank4:7, method-2 mapping, then denormalization.  Confidence is its Lux curve.
- **DarkPrevSA**: Bank4:8 first passes through its luma floor/interpolation, then target-high/Lux normalization, method-2 mapping and denormalization.  Confidence is its Lux curve.
- **ShortSatPrevSA**: target-high/Lux normalization against Bank4:19, method-2 mapping and denormalization.  Confidence is exact 1.0 across its configured ordinary regions.
- **IlluminanceSA**: uses delayed Short (`9:28`), the ordinary `9:63=0` branch, FrameSA AdjRatio, and Bank4:6.  Its two confidence calculators are aggregated with exact method-3 minimum.

The three dead-by-weight analyzers are:

- `BrightenImgSA`,
- `ExtremeColorSA`,
- `LongDarkPrevSA`.

Their configured ordinary confidence value trees contain only exact `+0.0f` leaves, so representing each as `{value=0, confidence=0}` is method-11 equivalent and removes unnecessary live-stat dependencies.

## Verification

`verify-cr.py` pins the exact DeviceMFT and IMX681 tuning hashes, fresh-runs the existing CE/CM/CJ/CK/BW/BZ proof chain, parses the seven analyzer records and their tuning trees, checks bounded Windows disassembly anchors for the calculator grammar and trigger publications, and validates the preserved CR63 oracle hashes.

It then compiles `native-effective-analyzers.c` with strict floating-point settings and compares every output float bit against an independent Python float32 model.  The deterministic corpus contains **28 boundary cases** and **8,192 seeded random cases**.  All candidate values/confidences match bit-exactly.

After CR, the ordinary front AEC boundary is reduced to the actual live-stat/state plane.  The next checkpoint can join these four Bank4 statistics to the existing generation-tagged Linux 3A/TL_BG producer, then feed `CR -> CP -> CQ` inside a bounded request loop before allowing a new sensor-control write.
