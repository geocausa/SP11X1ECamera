# E003i BV — Windows AEC final target aggregation

Status: **PASS (static/offline)**.

BV closes the identity and ordering of the three ordinary current-target producers that remain public inputs to BU. The final default analyzers do not consume opaque unnamed scalars: their target components use aggregation method 11 over earlier analyzer SI publications and confidence publications in bank 3, then each final analyzer emits the SI that `RunMeteringPostprocess` places in the Short/Long/Safe target tuple consumed by convergence.

## Default tail

The pinned IMX681 default sequence ends:

`... ADRCCapSA -> SafeAggSA -> ShortAggSA -> LongAggSA`.

The final analyzers are all sourced from S1 and publish, through their arithmetic programs:

- SafeAggSA: target data `3:8`, final SI data `3:9`, exposure type Safe;
- ShortAggSA: target data `3:10`, final SI data `3:11`, exposure type Short;
- LongAggSA: target data `3:12`, final SI data `3:13`, exposure type Long.

## Safe aggregation inputs

SafeAggSA target aggregation method 11 has eleven value/weight calculator pairs. Their bank-3 data IDs mechanically match earlier analyzer SI and confidence publications:

| analyzer | SI value | confidence weight |
| --- | ---: | ---: |
| FrameSA | 7 | 6 |
| SatPrevSA | 18 | 16 |
| DarkPrevSA | 24 | 21 |
| BrightenImgSA | 28 | 27 |
| FaceSA | 37 | 36 |
| TouchSA | 48 | 47 |
| DepthSA | 138 | 137 |
| TrackerSA | 156 | 148 |
| ExtremeColorSA | 185 | 182 |
| SaliencySA | 189 | 188 |
| IlluminanceSA | 229 | 227 |

The SI identities are not inferred from numbering. `verify-bv.py` parses each source analyzer's arithmetic-operator records and requires an explicit bank-3 write to the stated SI ID.

## Short/Long aggregation inputs

ShortAggSA method 11 has two target calculators:

- SafeAgg SI `3:9` with FrameSA confidence `3:6` through the pinned Lux-triggered weight program;
- ShortSatPrevSA SI `3:59` with confidence `3:58`.

LongAggSA likewise has:

- SafeAgg SI `3:9` with FrameSA confidence `3:6` through the same pinned Lux-triggered weight program;
- LongDarkPrevSA SI `3:65` with confidence `3:63`.

The shared SafeAgg candidate's terminal weight leaf is exact float32 `0.001f` (`0x3a83126f`) in both ShortAggSA and LongAggSA.

## Runtime aggregation identity

`CTargetAnalyzerComponent::AggregateValuesAndWeights` is `0x1803f0518`. Its method switch accepts 0..12; tuning method 11 dispatches to the path at `0x1803f0978`. That path collects only positive-weight target pairs, appends `0` and `256`, sorts the boundaries, evaluates adjacent intervals against the original weighted pairs, and finally writes one selected scalar to both target-low and target-high at `0x1803f0b70..0x1803f0b74`.

`CAnalyzer::RunAnalyzer` then performs the already-closed BD SI calculation from that target and the S1 source exposure. The final Safe/Short/Long result SIs are copied by the already-closed BD/BF metering path into the convergence target tuple.

This checkpoint closes the final aggregation topology and method identity. It does **not** yet implement the eleven upstream semantic analyzers on Linux; that is the next producer boundary.

No camera stream, module load, sensor write, MMIO, Windows boot, or reboot is used.
