# E003i CT static/runtime proof — BhistY value axis and Bank4 replay

## Pinned evidence

- `QcDeviceMFT8380.dll` SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.
- `com.surface.tuned.ffc_imx681.bin` SHA-256 `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`.
- full value-axis capture: `windows-oracle/E003I-CT-VALUE-AXIS.log`.
- BhistY source-tag oracle: `windows-oracle/E003I-CT-BHIST-S1-ORACLE_20260909.txt`, SHA-256 `21f4cd87bf24333aa717dfdbeea0e57bf49b29aa949adf7dc9dd45814decbf46`.
- expanded runtime-descriptor oracle: `windows-oracle/E003I-CT-RUNTIME-DESCRIPTOR-FLAGS_20260909.txt`, SHA-256 `04addcfd69a3ef2b2a37016c3cb63bf33c14d4d8fb61157a05b02fd6786a8e40`.

## `record+0x40` producer chain

The value-axis producer is now closed:

1. `0x1803a6388..6394` obtains the stats configuration and copies `config+0xb8` to internal state `+0x1e0`.
2. `0x1803a6f4c` consumes internal `+0x1e0` during histogram preprocessing/resampling.
3. `0x1803a70f8` publishes the raw-count pointer at stats output `+0x20`; `0x1803a7100` publishes the axis pointer at stats output `+0x28`.
4. `0x1803ce37c/380` copies upstream stats `+0x50` to calculator record `+0x38`; `0x1803ce384/388` copies upstream `+0x58` to calculator record `+0x40`.
5. `0x1803ea570` consumes the pair with `ldp x22,x23,[record,#0x38]`.

Thus calculator stats-record `+0x38/+0x40` is the raw-count/value-axis pair, and the value axis is configuration-owned upstream state rather than a guessed raw-bin conversion.

## Exact value axis

The retained oracle contains 1024 consecutive float32 words. Representative anchors include index 0 `0x3a807358 = 0.00098f`, index 127 `0.125f`, index 255 `0.37451f`, index 399 approximately `1.49658f`, index 479 `3.98486f`, index 575 `15.93799f`, index 767 `63.87549f`, index 895 approximately `127.750488f`, and index 1023 `0x437f8000 = 255.5f`.

The native generator reproduces all 4096 captured bytes exactly. SHA-256 is `f552e96271ad0737af14ab0272aa31c628dbf6b9d8b11d7ddcb8dd0d510e39f9`.

## Calculator/tuning ownership

The pinned 23-u32 serialized calculator descriptors identify:

- ID4 `BrightRatio`, API5, `BhistY`, outputs 5..6, trigger 7118 = `[0,1000] -> [255,256]`;
- ID11 `SatPrevHighPCTLLuma`, API6, output 7, trigger 7126;
- ID12 `DarkPrevLowPCTLLuma`, API6, output 8, trigger 7133;
- ID23 `ShortSatPrevHighPCTLLuma`, API6, output 19, trigger 7196.

Serialized word 12 is the flag later present at expanded runtime `+0x38`; serialized words 13/14 become runtime `+0x3c/+0x40` outputStart/outputEnd. The exact LuxIndex/percentile trigger tables and float32 gap interpolation are checked mechanically by `verify-ct.py`.

## Expanded runtime descriptor proof

Static code distinguishes the fields:

- `0x1803f4d50`: `ldr w26,[x8,#0x38]` reads the runtime flag;
- `0x1803f4dc4`: passes that flag as helper argument `w1`;
- `0x1803f4dd0`: reads the current stats record source tag as `w2`;
- `0x1803f4dd4`: calls the cap helper `0x1803eac78`;
- `0x1803f63dc`: `ldp w9,w8,[x8,#0x3c]` separately reads outputStart/outputEnd.

The API5/API6 histogram wrapper independently reads runtime `+0x38` at `0x1803f6860`, passes it as common-kernel `w5` at `0x1803f6880`, and calls `0x1803ea478` at `0x1803f689c`.

A read-only live FrameServer process-memory oracle then pins the front ordinary `BhistY` descriptors directly. The matching block was identified by exact runtime IDs/APIs, dereferenced calculator names, exact channel string `BhistY`, output ranges, and BrightRatio's referenced `[255,256]` trigger. This also disambiguated a separate `BhistY_short` profile.

In the same front ordinary block:

- BrightRatio: runtime flag `1`, output `5..6`;
- SatPrevHighPCTLLuma: flag `1`, output `7..7`;
- DarkPrevLowPCTLLuma: flag `1`, output `8..8`;
- ShortSatPrevHighPCTLLuma: flag `0`, output `19..19`.

The oracle used only process-memory reads; there were no target-process writes.

## Source-tag / history law

At `0x1803ea514`, the common kernel loads stats-record `+0x30` into `w26`. The retained KDNET one-shot captured many ordinary 1024-bin BhistY records and all observed tags were `3`. Accepted CJ establishes source-vector lane 3 = S1 and retained S1 at history `+0xa0`.

The cap helper `0x1803eac78` starts from exact float32 literal `0x3f7ae148 = 0.98f`:

- `0x1803eac98`: compare runtime flag `w1` with 1;
- `0x1803eac9c`: flag != 1 returns fixed scale;
- flag == 1 selects retained history;
- `0x1803eacd4/0x1803eacd8`: load/convert retained Safe exposure from `history+0x78`;
- `0x1803eace0..0x1803eacf0`: select/convert the source-tagged exposure lane; tag 3 selects S1 at `history+0xa0`;
- `0x1803eacfc`: form Safe/S1;
- for S1-class tag 3, `0x1803ead04/0x1803ead08` divides by `history+0x178` predictive/DRC gain;
- `0x1803ead10/14`: compare the ratio with 1;
- `0x1803ead18`: when ratio > 1, scale becomes `0.98f / ratio`.

For ordinary BhistY tag S1 the exact replay law is therefore:

`ratio = float(Safe) / float(S1) / PredGain`

`scale = (ratio > 1.0f) ? 0.98f / ratio : 0.98f`

The common kernel obtains bit depth/exponent from stats record `+0x18`; the retained BhistY record pins it to 8. Weighted-axis cap is `(2^8 - 1) * scale = 255 * scale`.

## Which Bank4 outputs need history

The runtime flags do not imply every published output depends on the cap:

- Bank4:7 and Bank4:8 are API6 weighted-luma outputs, so the flag1 S1-history cap is part of their value.
- Bank4:19 is API6 weighted luma but its flag is 0, so it uses fixed `255 * 0.98f`.
- BrightRatio has flag1, but Bank4:6 is API5 lane 1, the normalized-CDF interval mass. The cap is used only by API5's lane-0 weighted average, which publishes Bank4:5 and is outside CT's required set. Therefore Bank4:6 is history-cap invariant.

The accepted native request loop already stores ordinary F-3 `safe_exposure`, `s1_exposure`, and `pred_gain`, so CT consumes existing temporal state rather than introducing a parallel history model. CN/CP additionally prove the synthetic cold-start record has `PredGain=+0.0f`. The Windows helper has no zero guard: after `Safe/S1`, `FDIV` by +0 yields +inf, `FCMPE` takes the >1 path, and `0.98f/+inf` yields exact +0.0f. CT preserves this IEEE behavior instead of rejecting startup history.

## CDF/range arithmetic

The native implementation preserves the accepted Windows path:

- mask each raw word with `0x01ffffff`;
- serial float32 cumulative construction;
- denominator `max(1.0f, final cumulative)`;
- ARM `FRECPE` plus two `FRECPS`/Newton refinements for the 1024-entry SIMD normalization body;
- API5 value-domain search and API6 normalized-CDF-domain search;
- Windows epsilon and fractional endpoint arithmetic;
- weighted luma accumulation with selected `255 * scale` cap;
- API5 normalized-CDF mass publication for Bank4:6.

## Deterministic branch tests

For one count in bin 1023 at LuxIndex 500:

- neutral history `Safe=1000,S1=1000,PredGain=1`: B6 `0x3f800000`, B7 `0x4379e667`, B8 `0x4379e668`, B19 `0x4379e667`;
- history-limited `Safe=200,S1=100,PredGain=1`: B6 remains `0x3f800000`, B7 becomes `0x42f9e667`, B8 `0x42f9e668`, B19 remains `0x4379e667`;
- `Safe=200,S1=100,PredGain=2` cancels the ratio and returns exactly to the neutral output bits.

These fixtures directly exercise the Windows flag1 formula and its output-specific effect.

## Golden-safe real fixture replay

Three readable generation-tagged AP `STATS3A` producer captures are replayed offline. Their Bhist slices all sum to `2,073,600` masked pixels. For adapter verification they use neutral history (`Safe=S1`, `PredGain=1`) and LuxIndex `358.141845703125f`; these are not same-frame Windows output claims.

No new Linux camera runtime was started. After the Windows runtime-descriptor oracle, Camera was closed and SP11 returned to Golden Linux with kernel `7.1.5-sp11-render-parity-v4+`, saved entry `sp11-audio-fullio-v19c`, empty `next_entry`, and no camera modules loaded.
