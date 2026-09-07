# E003i BB — Windows AEC `GetExposureInfo`

Status: **PASS (static/offline) — the normal non-null type-0/type-1 `CAECXConvergence::GetExposureInfo` recurrence is reconstructed from target lanes, temporal history, `drcSpeed`, and the DRC Safe baseline.**

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

Function: `CAECXConvergence::GetExposureInfo` at `0x1803d18a0`.

## Normal types and output

`RunConvProcesss` calls `GetExposureInfo(0)` then `(1)` using the request-local ConvBase `drcSpeed` (`core +0x08`). The function writes:

- type 0 -> convergence `+0xe8` = DRC Short;
- type 1 -> convergence `+0xf0` = DRC Long.

The output address law is exact: `+0xe8 + 8*type`.

## Target and history relative exposure

The entry helper's mode 4 is:

```text
targetRelative(type) = targetSafeLog(+0x30) - targetLaneLog(+0x20 + 8*type)
```

For history snapshot 1:

```text
historyLaneLog = log_1.03(history lane qword)
if type == 0 and historyDRCGain(+0x178) > 1:
    historyLaneLog += log_1.03(historyDRCGain)

historyRelative = log_1.03(history safe qword +0x78) - historyLaneLog
relativeError   = targetRelative - historyRelative
```

Type 1 does not apply the history DRC-gain adjustment.

Windows compares `abs(relativeError)` against the exact inline double `0x3e7ad7f2a0000000` (`1.0000000116860974e-7`) to decide whether the relative target actually changed.

## Temporal direction and smoothing

History snapshots 1 and 2 establish:

```text
historyMotion = adjustedHistory1LaneLog - adjustedHistory2LaneLog
targetMotion  = targetLaneLog - adjustedHistory1LaneLog
directionSame = historyMotion * targetMotion >= 0
```

The convergence object contains a word state array beginning at `+0x2ac`; `GetExposureInfo(type)` reads `state[type]`. Constructor initialization is mechanically visible as state words 0..2 = 0 and state word 3 = 1. BB keeps the current type's state word explicit rather than inventing a higher-level name for it.

The default carry candidate preserves the previous history relative separation while rebasing it onto the current DRC Safe baseline (`+0xf8`):

```text
candidate = drcSafeLog - historyRelative
```

Unless the in-tolerance/state condition forces that carry path, Windows smooths when temporal direction agrees and `relativeError` is non-zero:

```text
step = drcSpeed * relativeError
if abs(step) < minimumStep:
    step = sign(step) * minimumStep

newRelative = historyRelative + step
candidate   = drcSafeLog - newRelative
```

The minimum step is runtime config `+0x2c`. Tolerance is the request-local ConvBase integer at `+0x14`.

If the candidate is inside the integer tolerance of the current target lane and tolerance is below float `0x3f800001`, Windows snaps to the target lane.

## Final guards

Windows then compares the candidate against the adjusted history lane and current target:

1. if candidate motion from history opposes target motion, retain the history lane;
2. do not overshoot the current target lane;
3. cap distance from DRC Safe to:

```text
max(abs(targetRelative), abs(historyRelative))
```

The resulting log value is stored at `+0xe8 + 8*type` and consumed by BA `DRCStretchAggregator`.

## Boundary

With BB, the ordinary chain is now:

`AX history -> AY BasicSafe -> AZ ConvStretch -> BB GetExposureInfo(0/1) -> BA DRCStretchAggregator -> ConvergeSensorExposures`.

Next: close normal single-exposure `ConvergeSensorExposures` and `PopulateOutput`, then join its final seven linear qwords to AX/AQ table681 arbitration and the already-proven IMX681 sensor-control path.

Safety: static/offline only; Windows remains unmounted and camera modules remain unloaded.
