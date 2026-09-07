# E003i AZ — Windows AEC ConvStretch aggregation

Status: **PASS (static/offline) — the request-local `BankIDConvStretch` record, per-entry runtime materialization, five aggregation modes, and the Short/Safe/Long lane update are reconstructed.**

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`  
Pinned front tuning SHA-256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

AZ begins at the BasicSafe output closed by AY and stops before `GetExposureInfo` / `DRCStretchAggregator`.

## Request-local ConvStretch

`RunConvProcesss` looks up controller ring `+0xdf50` (BankIDConvStretch/type 12) by the current request and saves the record pointer at convergence `+0x2f8`.

`CAECXConvergence::ComputeTargetStretchOutput` (`0x1803cecc8`) consumes:

- ConvStretch `+0x14`: active entry count;
- ConvStretch `+0x20`: pointer to an entry array;
- entry stride: `0x30`;
- entry trigger descriptors: `+0x04`, `+0x0c`, `+0x14`;
- entry `+0x18`: `stretchType`;
- ConvStretch `+0x10`: directional-filter mode used by aggregation;
- ConvStretch `+0x28`: aggregation type (`0..4`, `>=5` is logged invalid).

The trigger dispatcher covers target/previous delta, direction, lux, FPS, exposure time, gain, sensitivity, luma, gyro, distance, flash and external SCD inputs. The same three-trigger interpolator used by convergence produces a four-float stretch core.

## Per-entry runtime record

Windows diagnostic:

`Idx:%d Data: stretchType:%d Weight:%f StretchFctOff:%f Comp:%f tempWeight:%f FinalOff:%f`

Each current-request result is materialized into a `0x14` runtime record:

| offset | field |
|---:|---|
| `+0x00` | Weight |
| `+0x04` | FinalOff |
| `+0x08` | Comp |
| `+0x0c` | tempWeight |
| `+0x10` | FinalOff-is-negative flag |

For `stretchType == 0`, `StretchFctOff` is converted to `log_1.03(factor)` (with an approximately `1e-7` zero guard). Other stretch types retain the interpolated offset directly.

`ComputeTargetStretchOutput` explicitly zeros the 64-bit field at convergence `+0x128` before filling this request's runtime ring, so the batch starts at ring index zero. `+0x120` is the runtime-ring pointer and `+0x130` is the capacity used by Windows' unsigned remainder arithmetic.

## AggregateStretchOutput

`CAECXConvergence::AggregateStretchOutput` is at `0x1803cfa00`.

Its valid aggregation modes are reconstructed mechanically rather than assigned speculative enum names:

- **mode 0** — accepted records are weight-blended: `sum(weight*FinalOff)/sum(weight)`, and the same weighting is applied to `Comp` and `tempWeight`; ConvStretch `+0x10` can filter entries by the sign/direction flag;
- **modes 1/2** — bubble-sort complete `0x14` records by `FinalOff` ascending, then select a direction-compatible near-side (mode 1) or extreme-side (mode 2) record;
- **modes 3/4** — bubble-sort complete records by `Weight` ascending, then select the low-weight (mode 3) or high-weight (mode 4) endpoint, optionally subject to ConvStretch `+0x10` sign matching.

If no record is selected, Windows returns the exact fallback `FinalOff=0`, `Comp=1`, `tempWeight=0.5` (with the caller-zeroed weight retained).

The clean-room model preserves Windows' 32-bit wrapped relative-index arithmetic rather than silently replacing the ring with a Python list abstraction.

## Post-aggregate stretch filter

The selected/aggregated values feed:

```text
filtered = (1 - tempWeight) * history1.previousDelta
         + tempWeight * FinalOff
```

Windows suppresses values below one `log_1.03` step, otherwise quantizes with `FRINTA` to a runtime step (`config +0x2c` when `0 < step <= 1`, else `0.5`). The result is `shortStretch`.

For negative `shortStretch`:

```text
predGain = 1.03 ^ (abs(shortStretch) * Comp)
```

For non-negative stretch, `predGain=1`.

The Safe-lane stretch is:

```text
safeStretch = shortStretch + log_1.03(predGain)
```

## Correct Short/Safe/Long lane map

The final Windows log ABI establishes the displayed `Stretch Out Short, Safe, Long` order as:

- convergence `+0xa0` = **Short**;
- convergence `+0xb0` = **Safe**;
- convergence `+0xa8` = **Long**.

Starting from AY's BasicSafe broadcast:

```text
Short += shortStretch
Safe  += safeStretch
Long   unchanged
+0xd8 = predGain
+0xdc = shortStretch
```

This corrects a transient analysis note that had swapped the `+0xa8/+0xb0` labels; no committed earlier stage depended on that swapped label.

## Front tuning and boundary

The pinned front tuning contains both `DarkBrightStretch` and `DisableStretch` exactly once, so AZ does **not** assume one fixed preview profile. The next stage must close the bank/context selection and then reconstruct `GetExposureInfo -> DRCStretchAggregator` before the output can be joined to `ConvergeSensorExposures` and the AX/AQ sensor-control recurrence.

Safety: static/offline only; Windows remains unmounted and no camera modules are loaded.
