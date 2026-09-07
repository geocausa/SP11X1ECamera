# E003i-AC — clean request-local AWB/CCT reconstruction

Status: **PASS — request-local AWB_BG + explicit Lux → AGW → temporal CCT publication is reconstructed and regresses on Golden Linux.**

This checkpoint closes the CCT gate that remained after AB. It does not infer request IDs from source generation and it does not treat fitted historical Lux values as observations.

## Clean request-local path

The front path used by `cct_model.py` is:

`Titan680 AWB_BG (3072 × 0x50) → CStatParserV1 candidate → P01 StatScr → P03 CCT/distance → P04 DistWV + P05 IlluWV → P09 reject → AGW weighted XY → temporal AWB → P03 final CCT → integer publication`.

The active AWB stats half is subrecord 0; subrecord 1 is empty in the AC2 fixtures. The raw parser was previously validated byte-for-byte against the Windows parsed allocation with zero mismatches over all 3072 records.

P01 (`CSFStatScrV1`) requires all three channel means `> 1.0` and bad-pixel percentage `< 80.0`. P09 rejects a candidate when either P04 `w40` or P05 `w44` is zero. For the observed front profile the later MLC gates are inactive and the surviving AGW weight is exactly `float32(w40 * w44)`.

## Independently proven model stages

- P03 CCT engine replay is bit-exact on its retained oracle fixtures and on live request candidate XY/state diagnostics.
- P04 (`CSFDistWVV1`) is **168/168 bit-exact** on the AC60 live survivor set, including CCT-gap signed-distance rescaling.
- P05 (`CSFIlluWVV1`) is **259/259 bit-exact** on AC41 and **168/168 bit-exact** on the AC60 high-Lux branch.
- The shared P04/P05 request trigger was read live as float32 `0x4406bb30 = 538.9248046875`; static consumers identify the field as request Lux.
- AC60 final AGW weights are **168/168 bit-exact** as `float32(w40*w44)`.
- Startup temporal AWB is componentwise float32 `0.6 * fresh + 0.4 * previous`.
- Windows publishes the final float CCT with `FCVTZU`, i.e. truncation toward zero.

These live component proofs are why the CCT algorithm does not depend solely on the historical AC2 fitted-Lux regression.

## AC2 publication regression

The historical AC2 log proves the source/publication latency `raw n → publication n+3` and the four golden published values:

| raw | published request | expected CCT |
| --- | ---: | ---: |
| R1 | 4 | 5652 K |
| R2 | 5 | 5915 K |
| R3 | 6 | 6019 K |
| R4 | 7 | 5733 K |

AC2 did **not** record the exact request-local Lux samples. `regress-ac2.py` therefore uses four explicitly named **fitted consistency values** only for the historical sequence regression. They must not be cited as observed oracle metadata.

On Golden Linux, `regress-ac2.py` returns `ALL_PUBLISHED_MATCH True` and publishes exactly `5652 / 5915 / 6019 / 5733`.

## Linux API

`replay-cct.py` requires Lux explicitly. For a temporal publication it also requires the previous final XY bits; `--fresh-only` stops at the fresh AGW target.

```sh
./replay-cct.py fixtures/AC2-R1.raw \
  --lux 238.6585693359375 \
  --prev-x-bits 0x3f1129ca --prev-y-bits 0x3f00e486

./regress-ac2.py
```

The example Lux above is from the fitted AC2 regression, not an observation. In the live Linux pipeline Lux must come from the already-closed AB AEC_BE reconstruction.

## Fixture policy

Oracle raw/tuning fixtures under `fixtures/` are local-only and SHA-pinned by `FIXTURE-SHA256.txt`; they are not required to be committed as proprietary blobs. The clean scripts and closure metadata are the portable project artifacts.

## Gate decision

The request-local CCT reconstruction gate is closed. A **bounded** R5/R6 producer-to-existing-V4L2-IQ-FIFO integration proof is now authorized, using live Linux AEC-derived Lux and AWB_BG-derived CCT with the already-proven source/request association rule. This does not yet claim unrestricted continuous dynamic LSC production.
