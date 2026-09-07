# E003i BD — Windows AEC target-analyzer SI producer

Status: **PASS (static/offline + prior live measured-luma evidence)** — closes the Windows target-analyzer boundary that turns metering outputs plus a selected source exposure into the analyzer SI scalar consumed by the existing convergence chain.

## What is closed

The pinned IMX681 tuning contains a fixed `analyzers` array of 52 records × `0x8c`. The ordinary/default analyzer sequence includes `FrameSA` (ID 2) and ends with `SafeAggSA` (3), `ShortAggSA` (4), and `LongAggSA` (5).

The two exposure fields that had previously been ambiguous are now separated by native code, not by compact-file offset guessing:

- **`exposureType`** is copied into `CAnalyzer+0x28`. `CAnalyzer::RunAnalyzer` returns `this+0x8`, so this becomes result `+0x20`; `CAnalyzerManager::RunAnalyzer` reads result `+0x20` and passes it directly to `UtilExposureTypeTuning2Enum`.
- **`sourceType`** is copied into `CAnalyzer+0x2c`; `CAnalyzer::RunAnalyzer` passes that field to `UtilExposureTypeTuning2Enum` and uses the converted value to index the current seven-exposure source vector before calculating SI.

This distinction is also independently consistent across the tuning families. Ordinary Frame/Safe/Short/Long analyzers all use source type `S1`, while the dedicated HDR Safe/Short/Long analyzers source from Safe/Short/Long respectively.

## Exact type map

`UtilExposureTypeTuning2Enum` is at `0x180388630`. Its eight tuning IDs map to internal lanes:

| tuning ID | tuning name | internal lane |
| ---: | --- | ---: |
| 0 | Short | 0 |
| 1 | Safe | 2 |
| 2 | Long | 1 |
| 3 | S1 | 3 |
| 4 | S2 | 4 |
| 5 | S3 | 5 |
| 6 | S4 | 6 |
| 7 | S1 alias | 3 |

The internal enum-to-string helper independently names internal lanes `Short, Long, Safe, S1, S2, S3, S4`.

For the ordinary analyzers in the pinned front tuning:

- FrameSA: `Safe <- S1`
- SafeAggSA: `Safe <- S1`
- ShortAggSA: `Short <- S1`
- LongAggSA: `Long <- S1`

## Exact SI arithmetic

`CAnalyzer::RunAnalyzer` is at `0x1803f0ef8`. On the normal scalar path its result object contains:

- `+0x08` measured luma
- `+0x0c` confidence
- `+0x10/+0x14` target low/high
- `+0x18` computed SI
- `+0x20` tuning `exposureType`

The native computation is:

`SI = FCVTZU(double(sourceExposure[sourceType]) * double(float32(targetLow / max(measuredLuma, epsilon))))`

with exact float32 epsilon bits `0x33d6bf95` (`1.0000000116860974e-7`). The ratio is rounded to float32 *before* promotion to double and multiplication; the final positive finite result is converted with ARM64 `FCVTZU`.

`windows-target-si.py` is a clean offline model of this scalar arithmetic.

## Live measured-luma join

No new camera mutation was needed. The existing AB checkpoint already proved the normal front `AEC_BE -> FrameSA analyzer ID 2` measured-luma producer bit-exactly against live Windows inputs, including AB23, AB26 and eight correctly paired AB8 generations. BD rechecks that committed evidence.

The resulting upstream boundary is therefore:

`request-local AEC_BE -> bit-exact FrameSA measured luma -> target analyzer -> sourceType-selected exposure -> SI`

BC and the prior AX/AQ/AV/AW/AP chain already close the ordinary single-exposure convergence/arbitration/sensor side. BD runs BC's verifier fresh to retain that downstream join.

## Scope

This checkpoint does **not** claim that the conditional antibanding postprocess is an identity. Antibanding is a separate stage after target analysis and is intentionally left for the next checkpoint. It also does not claim AutoHDR/multi-exposure parity.

No proprietary DLL, tuning blob or live raw fixture is committed. Verification expects the SHA-pinned read-only evidence under `/tmp/sp11-aec-oracle/`.

## Reproduce

```sh
./verify-bd.py | tee VERIFY-RESULT.txt
```
