# Static / differential proof

CC inherits the Windows semantics by fresh-running committed checkpoint CB (`CB_VERIFY=PASS`). CB mechanically closes:

- the method-2 operand topology and recursive trigger interpolation;
- the `low*(1-t) + high*t` float32 blend order;
- the default ADRC Lux cap curve;
- Short `AdjRatioShort`, `ADRCGain` and final Short AdjRatio equations;
- Long `DRCGainRemainder`, `AdjRatioLong`, `DarkBoostGain` and final Long AdjRatio equations;
- the default-domain dominance of the Long remainder branch.

The native implementation does **not** use algebraic forms such as `clamp(ratio, 1, 1000)` for the Short method-2 ramp, nor does it collapse interpolation between equal child values. `lerp_win()` uses explicit float32 subtraction, multiplication and addition helpers, and the verifier builds with contraction disabled.

The public-output traps are:

- Short ramp input bits `0x3fbe7879` -> Windows/native `ADRCGain` bits `0x3fbe787a` while the direct input remains `0x3fbe7879`;
- Long Lux `260.9975f`, ratio `1.1f` -> child bits `0x3f8ccccd`, Windows/native `DarkBoostGain` bits `0x3f8ccccc`.

Differential scope is finite positive Safe/Short/Long target/ratio inputs plus finite Lux. The API rejects non-finite values and non-positive target/ratio inputs. This is intentionally narrower than every Windows special mode; it matches the ordinary/default production path being closed.
