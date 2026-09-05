# E003i-AB — clean Lux reconstruction

Status: **intermediate PASS**. The active Titan680 AEC_BE raw parser and the final Windows Lux adjustment are both reproduced exactly. The remaining open bridge is the clean derivation of the Algorithm001 `measuredLuma` input from parsed AEC_BE statistics.

## Closed in AB

`CamX::TitanStatsParser::ParseAECBEStats` uses the active single-IFE parser `FUN_1805f6600`. For the accepted front stream the raw payload is 1024 regions × `0x50` bytes. The parsed object begins with `flags=3, regions=1024`; each active parsed region is exactly `0x70` bytes. The active plane therefore occupies `0x1c008` bytes including the header. The full Windows allocation is `0x70008`, and the other three `0x1c000` planes are zero in the AA fixture.

`replay-aecbe-parser.py` reproduces all `0x70008` captured Windows bytes from the SHA-pinned AA raw fixture. Generated and captured SHA-256 are both `e3e4bdf0bf804eedf1870e895951692564737c43a760278660a94e476737dcc8`. `CAECXProcessISPGridHWStats::SetStats` independently requires a `0x70` region size, confirming the active ABI.

The live `(bank=9, data=8)` Lux writer was identified from its return address as `CAnalyzerAlgorithm001::RunAlgorithm` (`RVA 0x3fb7f0`). The current front tuning uses tuning exposure type `3`; `UtilExposureTypeTuning2Enum` maps that to table index `3`. The selected `0x28`-byte table record has baseline Lux at `+0x20`, bits `0x4365acdd` = `229.6752472`.

The adjustment path computes the target/measured ratio in float32, promotes it to double for `log10`, multiplies by float32 constant bits `0x429bcc0c` promoted to double, converts the delta back to float32, and adds the baseline in float32. The current front smoothing coefficient is zero. `replay-lux-adjustment.py` reproduces the two AB2 live outputs bit-exactly: `0x4392d14d` and `0x4392d09e`.

The compact AB2 KD log is SHA-256 `dd28cfef64fa46e67577617857b1209c8d7dd6293513ff43e682fdfacdfbf5ad`. Proprietary/oracle raw fixtures remain local-only and are SHA-pinned in `FIXTURE-MANIFEST.json`.

## Still open

A production Linux Lux producer cannot use the Windows `measuredLuma` as an oracle input. Static analysis identifies the upstream path as `CAECXCoreGridStatsOut::ComputeLuma` followed by `CAECXStatsGridProcessor::GetWeightedROIInterpLuma`. The per-region RGB/Bayer luma calculation is understood structurally, but the active normalized coefficient triplet plus ROI/interpolation/history scaling must still be recovered and replayed from the AA AEC_BE fixture. Only then can the AA request-3653 Lux value `363.6280518` be considered cleanly reproduced end-to-end.

Dynamic R5/R6 LSC substitution remains **unauthorized** until clean Lux and CCT reconstruction both pass.

## Reproduce

```sh
./replay-aecbe-parser.py fixtures/E003I-AA-AECBE2.raw --expected fixtures/E003I-AA-AECBE2.parsed
./replay-lux-adjustment.py
```
