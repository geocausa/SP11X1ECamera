# E003i CD — Windows final aggregator effective weights

Status: **PASS (static/offline)**.

CD closes the remaining ambiguity in the Short/Long final method-11 inputs. The serialized calculators retain a direct Frame confidence descriptor `3:6` inside the shared Safe candidate's weight half, but the runtime method selector is **1**, not direct method 0.

The Windows method-1 weight path does not read that `3:6` descriptor. It reads only the two trigger descriptors, evaluates the common trigger interpolator, and stores the interpolated scalar directly as the candidate weight. For both ShortAggSA and LongAggSA those trigger descriptors are Lux/Lux (`9:8`, `9:8`) and the nested program has a single region/leaf whose exact float32 value is `0.001f` (`0x3a83126f`). Therefore the effective shared Safe-candidate weight is exactly `0.001f` for every finite Lux input.

This corrects the earlier shorthand that described the Safe candidate as using Frame confidence “through” the weight program. The `3:6` descriptor is serialized but not consumed on the method-1 runtime branch.

The dedicated candidates remain direct weights:

- ShortSatPrevSA: confidence `3:58`;
- LongDarkPrevSA: confidence `3:63`.

No runtime camera activity is used.
