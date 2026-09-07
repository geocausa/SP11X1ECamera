# E003i-AB — clean Lux reconstruction

Status: **PASS — live request-local raw AEC_BE → measured luma → Algorithm001 Lux → publication association is bit-exact. Stage AC subsequently closes request-local CCT.**

## What is closed

The Titan680 front AEC_BE parser remains byte-exact: 1024 raw regions × `0x50` bytes become active parsed records of `0x70` bytes. The historical AA raw/parser fixture still reproduces the complete captured Windows parser allocation SHA-256 `e3e4bdf0bf804eedf1870e895951692564737c43a760278660a94e476737dcc8`.

AB23 then proved the live producer consumes that parser output directly: its first source-cell pointer was exactly `parsed + 8`, and an independent comparison of all 1024 raw→parsed region semantics found zero mismatches. In the same run, source[1] and the subsequent `CAnalyzerAlgorithm001::RunAlgorithm` measured input were both `0x3f5d179f`.

## Correct live measured-luma path

The earlier all-1024-cell reconstruction was incomplete. AB26 captured the missing live spatial-selection state.

The normal front path is:

`AEC_BE 32x32 → ComputeLuma → checkerboard selected cells → FrameLumaBE16x16 → FrameSA analyzer 2 → meter bank 1 (Equally Weighted)`.

Exact AB26 selection/configuration:

- 1024-entry cell-mask array: 512 entries `0xf000003c`, 512 entries `0x00000000`;
- selected layout is a checkerboard, selected iff `(row + column) % 2 == 0`;
- active FrameLuma descriptor mask is `0x10`, dimensions `16x16`, mode `0`;
- the other observed descriptor mask is `0x02`, which does **not** intersect `0xf000003c`;
- therefore each 2×2 source block contributes exactly two selected source cells to one 16×16 output bin;
- each bin uses the producer's float32 incremental-mean update;
- FrameSA then performs sequential float32 weighted accumulation of the 256 bins and divides by the float32 weight sum.

The per-source-cell luma arithmetic remains exactly as previously disassembled: coefficients `0x3e991687 / 0x3f1645a2 / 0x3de978d5` (`0.299f / 0.587f / 0.114f`), scale `0x3504655e = 1 / 2^(18-8) / 1980`, RGB combination in double using the promoted float32 constants, then one float32 round.

AB26's live source[1]/Algorithm input was `0x3f26a3f7`. The corrected replay returns **`0x3f26a3f7` bit-for-bit**. A direct mean of the selected 512 cells is three ULP lower, proving the 16×16 intermediate rounding is material.

AB23 independently closes the same path: corrected replay returns **`0x3f5d179f`**, exactly its live source[1]/Algorithm input. The opposite checkerboard phase returns `0x3f5bec6a` and is rejected.

## Eight correctly paired AB8 live generations

AB8 captured raw AEC_BE immediately before each Algorithm001 invocation. With the AB26 selection law, all eight raw fixtures replay to the live measured input exactly:

| raw | replay/live measured bits |
| --- | --- |
| R1 | `0x3f1e9ed8` |
| R2 | `0x3f1fc97f` |
| R3 | `0x3f1fbfcb` |
| R4 | `0x3f1a1d84` |
| R5 | `0x3f1a139b` |
| R6 | `0x3f83aab3` |
| R7 | `0x4023e477` |
| R8 | `0x3ffc32ff` |

Local AB6 fixtures provide a second reproducible check: S0/S1/S2 replay exactly to live inputs `0x3f83b78d / 0x3f8323e6 / 0x3f832191`.

## Algorithm001 and publication association

`CAnalyzerAlgorithm001::RunAlgorithm` is RVA `0x3fb7f0`. For the normal path it reads the selected history exposure record's dynamic Lux field at `+0x20` and computes:

`Lux = baseline + f32(log10(f32(target / measured)) * K)`

with `K = 0x429bcc0c = 77.89852905273438`, clamp at zero, followed by the optional previous-Lux blend. The relevant runs have target `0x42480000 = 50.0`; the observed blend coefficient is zero.

AB7 established the publication law over 233 Algorithm results: each result appears at the second subsequent publication. AB8 then gives a compact correctly paired end-to-end sequence:

| raw | measured | history baseline | Algorithm live/replay | first matching request |
| --- | --- | --- | --- | --- |
| R1 | `3f1e9ed8` | `4365acdd` | `43bd1baa` | `0x5` |
| R2 | `3f1fc97f` | `4365acdd` | `43bcfbee` | `0x6` |
| R3 | `3f1fbfcb` | `4365acdd` | `43bcfcf5` | `0x7` |
| R4 | `3f1a1d84` | `438a566e` | `43d5186f` | `0x8` |
| R5 | `3f1a139b` | `43a1d66f` | `43ec9986` | `0x9` |
| R6 | `3f83aab3` | `43b4966f` | `43f64894` | `0xa` |
| R7 | `4023e477` | `43cb0fac` | `43fd542c` | `0xb` |
| R8 | `3ffc32ff` | `43cb0fac` | `4400e1a9` | `0xc` |

All eight Algorithm outputs replay bit-exactly from their request-local measured input and live history baseline.

## Correction to the old AA request claim

The historical AA `E003I-AA-AECBE2.raw` + parsed pair remains a valid parser fixture, but its adjacency to publisher request `0xe45` is **not** a valid raw→request association. AB7/AB8 proved the pipeline latency law, so the former statement that this raw directly produced request 3653 Lux `363.6280518` is withdrawn.

With the now-correct checkerboard path, that raw fixture's measured-luma value is `0x41f486db` = `30.565847396850586`; it is recorded only as a property of that raw fixture, not as request-3653 evidence.

## Evidence

- AB8 paired sequence log SHA-256: `37fdc506953e8b5fc35a7da7d3c833b2673617b4b150c41a90f017382fe1078d`.
- AB23 chain log SHA-256: `30c59b83a9669396c4c7e438200394ec069edd2de6f24dbddde95db972bcb6a3`.
- AB26 mask/config log SHA-256: `c0585690eea2f2d76c114318bca226c2821753710d3a304226d50a1b53783411`.
- AB26 mask dump SHA-256: `feefaa53176a9cc4a30c6adc917c3d0d6cded90cbe9f0bc1e71e9e970017d02c`.
- Compact source/request provenance is retained in `E003I-AB21-SOURCE-PROVENANCE.txt`, `E003I-AB22-REQUEST-ASSOCIATION.txt`, and `E003I-AB26-CLOSURE.txt`.

The Windows oracle was returned to protected Golden Linux. Verified kernel: `7.1.5-sp11-render-parity-v4+`; GRUB saved entry `sp11-audio-fullio-v19c`; `next_entry` empty; no candidate camera modules loaded.

## Remaining gate

Lux reconstruction for a correctly paired live sequence is closed. **Stage AC now closes the equivalent request-local AWB/CCT reconstruction.** The next authorized step is a bounded R5/R6 live producer→existing-IQ-FIFO integration proof; unrestricted continuous dynamic LSC is not yet claimed.

## Reproduce locally

```sh
./replay-aecbe-parser.py fixtures/E003I-AA-AECBE2.raw --expected fixtures/E003I-AA-AECBE2.parsed
./replay-measured-luma.py fixtures/E003I-AB6-S0.raw --expected-bits 0x3f83b78d
./replay-measured-luma.py fixtures/E003I-AB6-S1.raw --expected-bits 0x3f8323e6
./replay-measured-luma.py fixtures/E003I-AB6-S2.raw --expected-bits 0x3f832191
./replay-lux-adjustment.py
```

Proprietary/oracle raw fixtures remain local-only and SHA-pinned; they are not committed.
