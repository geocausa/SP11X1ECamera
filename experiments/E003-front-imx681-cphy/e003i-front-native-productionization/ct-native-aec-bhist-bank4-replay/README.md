# E003i CT — native AEC BHist → Bank4 replay

Status: **PASS candidate; full inherited verifier running**.

CT closes the ordinary front-camera BHist adapter left open by CS. The native replay now maps raw 1024-bin `BhistY`, LuxIndex, and the already-retained F-3 AEC history fields `{Safe, S1, PredGain}` to the four Bank4 values required by the accepted effective-analyzer path:

| Bank4 | Windows calculator | API | Result |
|---:|---|---:|---|
| 6 | BrightRatio | 5 | normalized CDF mass for value interval `[255,256]` |
| 7 | SatPrevHighPCTLLuma | 6 | percentile-weighted BhistY luma |
| 8 | DarkPrevLowPCTLLuma | 6 | percentile-weighted BhistY luma |
| 19 | ShortSatPrevHighPCTLLuma | 6 | percentile-weighted BhistY luma |

## Value-axis closure

The retained Windows oracle captured all 1024 float32 entries installed through stats-record `+0x40`. The axis is non-linear and uses eight raw-width regimes (`1,2,8,32,128,256,512,1024`, with one raw unit = `1/1024`), midpoint transitions, decimal quantization to five places, and a final clamp at `255.5f`.

`e003i_bhist_build_value_axis()` reconstructs all 4096 bytes exactly. SHA-256 of both the Windows axis bytes and native output is:

`f552e96271ad0737af14ab0272aa31c628dbf6b9d8b11d7ddcb8dd0d510e39f9`.

The producer chain is also closed statically: config `+0xb8` → internal `+0x1e0` → stats-output axis pointer → calculator stats record `+0x40` → common histogram kernel.

## Runtime source and cap semantics

A retained KDNET oracle proves ordinary 1024-bin BhistY records carry source tag `3`; the accepted source-vector proof maps lane 3 to **S1**.

A second, read-only Windows oracle scanned FrameServer process memory and identified the actual expanded front `BhistY` runtime descriptors by ID/API/name/channel/output range. It proved the runtime `+0x38` flags are:

- BrightRatio: `1`
- SatPrevHighPCTLLuma: `1`
- DarkPrevLowPCTLLuma: `1`
- ShortSatPrevHighPCTLLuma: `0`

Runtime `outputStart/outputEnd` are separate fields at `+0x3c/+0x40`. This distinction matters: `+0x38` is the argument controlling the Windows histogram cap helper.

For flag `1` and source tag S1, Windows computes, in float32 arithmetic:

`ratio = float(Safe) / float(S1) / PredGain`

`scale = ratio > 1 ? 0.98f / ratio : 0.98f`

and caps weighted luma at `(2^8 - 1) * scale = 255 * scale`. Flag `0` uses fixed `0.98f`.

Consequently:

- Bank4:7 and Bank4:8 require the retained F-3 `{Safe,S1,PredGain}` history-normalized cap;
- Bank4:19 uses the fixed `0.98f` cap;
- BrightRatio itself has flag `1`, but Bank4:6 is its **CDF-mass** output lane, so Bank4:6 is invariant to this weighted-luma cap. The history scale only changes BrightRatio's unused average-luma lane.

The native request loop already carries exactly these F-3 fields, so CT adds no new temporal state model.

## Native replay

`native-bhist-bank4.c` mirrors the pinned Windows path:

- raw parser mask `0x01ffffff` on each BHist word;
- exact 1024-entry value axis;
- serial float32 cumulative CDF;
- ARM `FRECPE` plus two `FRECPS`/Newton refinements for the 1024-bin normalization body;
- Windows-style epsilon/boundary search and fractional endpoint arithmetic;
- tuning-defined LuxIndex→percentile interpolation;
- exact S1-history cap helper for Bank4:7/:8 and fixed cap for :19.

Public API:

```c
int e003i_bhist_replay_bank4(
    const uint32_t raw_words[1024],
    float lux_index,
    const struct e003i_bhist_history_input *history,
    struct e003i_bhist_bank4_output *out);
```

The history input contains `safe_exposure`, `s1_exposure`, and `pred_gain` and corresponds directly to the ordinary retained F-3 history already maintained by the native request loop. The helper intentionally accepts the synthetic cold-start `PredGain=+0.0f`: ARM float division produces `+inf`, so the flag1 scale becomes exact `+0.0f`; Bank4:7/:8 therefore replay as zero on that startup state while Bank4:6 and :19 remain defined.

## Verification

The CT-local verifier passes with:

- pinned DLL and IMX681 tuning hashes;
- exact tuning descriptor and trigger checks;
- static runtime-layout/helper instruction anchors;
- retained S1-source oracle;
- retained runtime-descriptor-flags oracle;
- byte-exact full-axis comparison;
- native ARM build with warnings-as-errors;
- synthetic neutral and history-limited cap cases;
- parser-mask equivalence;
- three real Golden-safe generation-tagged AP `STATS3A` producer captures.

For the explicit history-limited synthetic case `Safe=200, S1=100, PredGain=1`, a single last-bin sample produces Bank4:7/8 near `124.95`, while Bank4:6 remains `1.0` and Bank4:19 remains `249.9`. Setting `PredGain=2` cancels the ratio and restores the neutral `0.98f` cap, matching the Windows helper law.

The AP real-stat fixtures are replayed using **neutral history** (`Safe=S1`, `PredGain=1`) solely to prove the raw STATS3A adapter; they are not same-frame Windows output oracles.

## Safety

The second Windows oracle used only `OpenProcess(PROCESS_VM_READ|PROCESS_QUERY_INFORMATION)`, `VirtualQueryEx`, and `ReadProcessMemory`; it performed no process writes or breakpoint patching. The earlier KDNET source-tag breakpoint had already been cleared. Camera was closed and SP11 returned to Golden Linux afterward.

Current Golden state was re-verified: kernel `7.1.5-sp11-render-parity-v4+`, GRUB saved entry `sp11-audio-fullio-v19c`, empty `next_entry`, and no camera modules loaded. No new Linux camera runtime, STREAMON, sensor write, or camera MMIO was performed by CT.
