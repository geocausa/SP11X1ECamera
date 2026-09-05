# E003i-AB — clean Lux reconstruction

Status: **intermediate PASS — AEC_BE parser and normal FrameSA measured-luma path closed; request-local Lux history/target association remains open.**

## Closed parser path

`CamX::TitanStatsParser::ParseAECBEStats` uses the active single-IFE parser `FUN_1805f6600`. The accepted front payload is 1024 regions × `0x50` bytes. The parsed object begins with `flags=3, regions=1024`; each active parsed region is `0x70` bytes. The active plane is therefore `0x1c008` bytes including the header inside the full `0x70008` Windows allocation.

`replay-aecbe-parser.py` reproduces the complete captured AA parsed allocation byte-for-byte from the SHA-pinned raw fixture. Generated and Windows SHA-256 are both `e3e4bdf0bf804eedf1870e895951692564737c43a760278660a94e476737dcc8`.

## Closed normal measured-luma path

Static code, front tuning, and AB3 live configuration now close the normal-preview path as:

`AEC_BE 32x32 -> CAECXCoreGridStatsOut::ComputeLuma -> LumaBE16x16 -> FrameSA analyzer ID 2 -> stats calculator ID 2 (FrameLumaBE16x16) -> 2-D meter bank ID 1 (Equally Weighted)`.

AB3 captured coefficient bits are `0x3e991687`, `0x3f1645a2`, `0x3de978d5`, exactly `0.299f / 0.587f / 0.114f`. `ConfigureSS` gives the active normalization `1 / 2^(18-8) / 1980`, float bits `0x3504655e`. The AA fixture reports 1980 valid samples for every R/B/Gr/Gb channel in all 1024 regions, so no saturation-fill branch is active.

ARM64 disassembly is important for exact rounding: `ComputeLuma` promotes coefficients and sums to double, combines them with separate operations, multiplies by the float32 scale promoted to double, then rounds once to float32. It then converts the 32×32 field to `LumaBE16x16` using a four-sample float32 running mean per 2×2 cell. The FrameLuma calculator performs separate float32 multiply/add accumulation; the active equal weight is exactly 1.0.

`replay-measured-luma.py` therefore reconstructs the AA request-3653 fixture's normal FrameSA measured input as **30.50203514099121**, bits **`0x41f4042b`**. The simpler direct average of all 1024 region lumas is `0x41f40433`; it is intentionally rejected because it skips the real 16×16 intermediate rounding.

## Corrected Algorithm001 baseline provenance

The live `(bank=9, data=8)` Lux writer is `CAnalyzerAlgorithm001::RunAlgorithm` at RVA `0x3fb7f0`. Its final arithmetic remains bit-exactly reproduced by `replay-lux-adjustment.py`:

`Lux = historyBaseline + f32(log10(f32(target/measured)) * K)`, clamped at zero, followed by the optional previous-Lux blend. Live `K` is bits `0x429bcc0c` = `77.89852905273438`; the observed blend coefficient is zero.

The earlier AB wording that treated `0x4365acdd = 229.6752472` as a fixed tuning-table Lux baseline was incorrect. `UtilExposureTypeTuning2Enum` chooses an exposure type; Algorithm001 then reads the selected exposure record's Lux field at `+0x20` from `CAECXHistory::GetInternalFrameHistory`. AB3 proves this state is dynamic: across 49 live points the baseline moves from about 229.675 through 245.675, 262.175, 270.175, and settles at about 281.675, while the target remains `0x42480000` = 50.0. The AB3 source log is SHA-256 `eabc4f77f04db2e079c6a9546655d9aa8ddc77484d164b9099047e2fe28a4367` on SP7.

Independent static analysis also closes the canonical exposure coordinate used by Qualcomm AEC: **Lux index = `K * log10((gain * exposureTime) / indexZeroExposure)`**, where `indexZeroExposure` is a sensor/runtime exposure-table reference, not the AEC tuning control records previously inspected.

## Still open

The stats side is no longer the blocker. To reproduce the AA request-3653 Windows Lux `363.6280518` end-to-end, the remaining operands must be request-associated truthfully:

- the FrameSA target selected for that exact request/scene; and
- the historical exposure-record Lux baseline (or equivalently the request-local exposure state plus the sensor `indexZeroExposure`) used by Algorithm001 for that request.

AB3's target=50 and history evolution are a separate live sequence and must not simply be transplanted onto AA request 3653 without request association. Dynamic R5/R6 LSC substitution remains unauthorized until clean Lux and CCT reconstruction both pass.

## Reproduce

```sh
./replay-aecbe-parser.py fixtures/E003I-AA-AECBE2.raw --expected fixtures/E003I-AA-AECBE2.parsed
./replay-measured-luma.py fixtures/E003I-AA-AECBE2.raw
./replay-lux-adjustment.py
```

Proprietary/oracle raw fixtures remain local-only and SHA-pinned in `FIXTURE-MANIFEST.json`.
