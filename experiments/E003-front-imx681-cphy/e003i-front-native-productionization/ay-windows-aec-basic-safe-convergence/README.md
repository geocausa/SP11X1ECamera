# E003i AY — Windows AEC BasicSafe convergence kernel

Status: **PASS (static/offline) — the non-null steady-state `CAECXConvergence::ComputeBasicSafeConvergence` arithmetic is reconstructed as a clean-room request-local kernel.**

Pinned Windows DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

Pinned front IMX681 tuning SHA-256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`.

AY is deliberately narrower than the complete Windows convergence pipeline. It closes **BasicSafe only**. Dynamic ConvStretch selection, `AggregateStretchOutput`, DRC exposure-info construction, `DRCStretchAggregator`, settle/smooth behavior, and `ConvergeSensorExposures` remain the next boundary.

## Inputs and temporal meaning

AX established that `RunConvProcesss` seeds the convergence object with seven target log exposures and seven previous-history log exposures. BasicSafe operates on the safe lane.

On the normal non-null path, `ComputeBasicSafeConvergence` uses:

- `targetSafeLog`: current request safe target, internal convergence `+0x30`;
- `previousSafeLog`: `GetInternalFrameHistory(1)` safe exposure (`history +0x78`) converted into the shared log1.03 coordinate;
- `previous2SafeLog`: `GetInternalFrameHistory(2)` safe exposure;
- `delayedSafeLog`: `GetInternalFrameHistory(cameraContext+0x8ec)` safe exposure;
- `previousDelta`: float at history(1) `+0x17c`;
- request-local `BankIDConvBase` / type-11 record at controller ring `+0xdef0`;
- interpolated ConvBase core tuple `baseSpeed`, `baseCapping`, `drcSpeed`;
- request-local capping type at ConvBase `+0x18` and integer tolerance at `+0x14`;
- runtime minimum-step threshold from convergence config/context `+0x2c`.

The logarithmic coordinate is the same `1.03f` coordinate already proven in AR/AQ.

## Core recurrence

Define:

```text
T = targetSafeLog - previousSafeLog
D = targetSafeLog - delayedSafeLog
M = previousSafeLog - previous2SafeLog
candidate = baseSpeed * T
```

The three capping modes are mechanically visible in the DeviceMFT:

```text
cappingType == 0: cap = baseCapping * D
cappingType == 1: cap = sign(T) * baseCapping
otherwise:        cap = D / pipelineDelay
```

Windows computes `fabs(candidate)` and `fabs(cap)` and retains the signed operand with smaller magnitude.

Before/after that selection Windows applies three guards that AY preserves explicitly:

1. **intolerance skip** — when the target delta is inside the request-local tolerance, the runtime intolerance gate is active and the retained previous-delta float is exactly zero, convergence returns the previous safe log unchanged;
2. **residual snap** — when the selected step changed from the retained delta and would leave a residual inside tolerance, Windows can snap exactly to the target; the inline `0x3f800001` guard restricts this to integer tolerance 0/1;
3. **minimum-step clamp** — while still outside the runtime minimum threshold, a too-small selected step is raised to `+/-minimumStep` unless the runtime small-delta exemption and retained-delta match both hold.

Finally Windows applies the temporal direction gate:

```text
if M * T >= 0:
    applied = selectedStep
else:
    applied = 0

newSafeLog = previousSafeLog + applied
```

The resulting `newSafeLog` is broadcast to all seven internal output lanes at `+0xa0,+0xa8,...,+0xd0` before later stretch/DRC processing.

## Front tuning corroboration

The pinned front tuning contains four independently decoded ConvBase core tuples at unique byte locations, each with capping type 0:

| profile evidence | baseSpeed | baseCapping | drcSpeed |
|---|---:|---:|---:|
| FastConv | 0.80 | 0.33 | 0.15 |
| Touch reduce-by-0.8 | 0.64 | 0.33 | 0.15 |
| FastConv + FastDRC | 0.80 | 0.33 | 0.63 |
| crop-window slow | 0.10 | 0.33 | 0.10 |

`verify-ay.py` checks the exact serialized float32 tuples and their unique offsets in the pinned tuning binary.

## Safety / scope

This checkpoint is static/offline only. It does not load `imx681`, `qcom_camss` or `ov13858`, does not mount Windows, and does not mutate the camera. It also does **not** authorize using BasicSafe alone as the Linux continuous-AEC output because the front tuning contains both `DarkBrightStretch` and `DisableStretch` profiles and Windows selects stretch/DRC behavior dynamically.

Next: reconstruct the request-local `BankIDConvStretch` selection and `ComputeTargetStretchOutput -> AggregateStretchOutput -> GetExposureInfo -> DRCStretchAggregator` boundary, then join that exact output to `ConvergeSensorExposures` and the AX/AQ recurrence.
