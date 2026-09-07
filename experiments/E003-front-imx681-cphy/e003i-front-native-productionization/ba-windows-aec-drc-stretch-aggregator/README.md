# E003i BA — Windows AEC DRC/stretch aggregator

Status: **PASS (static/offline) — `CAECXConvergence::DRCStretchAggregator` is reconstructed as a pure policy transform over the AZ stretch block and the DRC block produced by `GetExposureInfo`.**

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

BA deliberately treats `GetExposureInfo` as its input producer; that function remains the next kernel to close.

## Seven-lane block layout

Windows' own diagnostics and vararg ABI establish identical logical ordering for the two blocks:

```text
normal/stretch:  Short +a0, Long +a8, Safe +b0, s1 +b8, s2 +c0, s3 +c8, s4 +d0
DRC block:       Short +e8, Long +f0, Safe +f8, s1 +100, s2 +108, s3 +110, s4 +118
```

`GetExposureInfo(type)` writes its result at `+0xe8 + 8*type`; the normal caller invokes types 0 and 1. Immediately before the calls, the current Safe lane is retained at `+f8`, giving the logged DRC Short/Safe/Long triplet `e8/f8/f0`.

## Ratios

At aggregator entry:

```text
StretchRatio = 1.03 ^ (Safe - Short)
DRCRatio     = 1.03 ^ (Safe - DRCShort)
PredGain     = +d8
policy       = runtime/config +0x30
```

Windows unconditionally seeds normal Long (`+a8`) from DRC Long (`+f0`) before policy branching.

## Mechanically reconstructed policy

If `StretchRatio < 1`, Windows logs the branch invalid.

If `DRCRatio <= 1`, Windows uses the normal/predictive block (with the already-seeded DRC Long).

At the unity stretch boundary with `DRCRatio > 1`, Windows uses the full DRC block and forces predictive gain to unity.

When both ratios exceed unity:

- **policy 0:** if `DRCRatio >= StretchRatio`, copy the full DRC block and set predictive gain to 1. Otherwise retain the stretch Short/Safe block and consume overlapping DRC gain from predictive gain (`PredGain/DRCRatio`) when possible, or force predictive gain to 1 when DRC exceeds the available predictive gain.
- **policy 1:** cascade stretch and DRC. Copy the DRC block, then set `Short = DRCShort - log_1.03(StretchRatio)`; predictive gain remains the incoming value.
- **policy 2:** keep stretch/predictive Short and Safe while retaining the DRC Long seeded at function entry.
- other policy values follow the Windows invalid-policy path.

The clean-room verifier checks each branch against exact static copy/ratio/diagnostic anchors.

## Call order

The normal path is now mechanically bounded as:

`AY BasicSafe -> AZ ConvStretch -> GetExposureInfo(0/1) -> BA DRCStretchAggregator -> ConvergeSensorExposures`.

Next: reconstruct `GetExposureInfo` itself, including its history-relative DRC offsets and `drcSpeed`/minimum-step limiter. Then the convergence block can be joined to final `ConvergeSensorExposures`, AX history recurrence and AQ T681 arbitration.

Safety: static/offline only; Windows stays unmounted and camera modules stay unloaded.
