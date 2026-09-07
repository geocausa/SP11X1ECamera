# E003i BG — Windows FrameSA target/Lux trigger

Status: **PASS (static/offline + prior live Lux evidence)** — closes the ordinary FrameSA target-low tuning identity and its Lux trigger key without changing the camera or sensor.

The key correction is that `0.001f` is part of `FrameSA_Confidence`, not `FrameSA_Target`. The actual target component is calculators entry 3601, labeled by `FrameSA_Target`, and uses trigger `(9,8)`.

For the pinned IMX681 tuning, targetLow == targetHigh and follows the six-region curve `55, 50, 46, 40, 40, 30` over Lux-trigger regions `0..140, 160..270, 300..360, 370..410, 420..460, 500..1000`, with the native TwoFloats interpolator bridging the gaps.

This joins directly to BD's already-proven normal SI equation:

`SI = FCVTZU(double(sourceExposure[S1]) * double(f32(targetLow / max(measuredLuma, epsilon))))`

The trigger identity is mechanical: startup code seeds `(9,8)` from its Lux field, and normal `runConvergence` plus independent consumers read the same packed `(9,8)` key through the trigger DB. AB remains the live authority for the dynamic Algorithm001 Lux computation and its second-subsequent-publication timing.

Scope: BG does **not** claim that the startup direct-write helper is the normal steady-state Lux writer. That writer may be indirect through analyzer/result publication. The target calculator's `(9,8)` read identity is closed; the exact steady-state write implementation is left distinct rather than guessed.

Reproduce:

```sh
./verify-bg.py | tee VERIFY-RESULT.txt
```
