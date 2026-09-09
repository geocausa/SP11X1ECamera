# CP static/native proof

## Windows cold-start Lux path

`CAECXControl::QueryControlStartExposure` establishes the exact decision point:

- `0x180373828`: load startup-Lux valid flag from `sp+0x150`;
- valid path loads startup Lux from `sp+0x14c` and stores it to the local result at `x20+0x10`;
- fallback path loads startup exposure from `sp+0x120`, loads the controller input float from `+0x14ed0`, calls `CAECXControl::CalculateStartLuxIndex` at `0x180386510`, and stores `s0` to `x20+0x10`;
- common join is `0x18037385c`.

The bounded cold oracle hit the fallback path with valid flag 0 and direct startup Lux 0. It observed controller input `0x4365b24a`, startup exposure qword 33,333,333, and final published Lux `0x4365b24a`.

CP intentionally does not claim which internal `CalculateStartLuxIndex` tuning-reference branch caused the result to equal its input. Only the exact ordinary cold-profile result and selected outer path are promoted to the native constant.

## Algorithm001 alpha

`CAnalyzerAlgorithm001::RunAlgorithm`:

- `0x1803fba9c`: `ldr s18, [x19,#0x70]`;
- `0x1803fbaa0`: first consumer after that load.

The live breakpoint at `0x1803fbaa0` observed `[x19+0x70] = 0x00000000` and `s18 = +0.0f` exactly.

## Native reduction

CP changes CO's initializer from:

`init(state, initial_lux_trigger, algorithm001_alpha)`

to:

`init(state)`

and installs exact bit-pattern constants with the existing `f32bits()` helper:

- `E003I_WINDOWS_INITIAL_LUX_BITS = 0x4365b24a`;
- `E003I_WINDOWS_ALGORITHM001_ALPHA_BITS = 0x00000000`.

CN's 33,333,332 synthetic retained-history contract is unchanged. Sequential request guarding and commit-after-success semantics are unchanged.

## Differential

`verify-cp.py` fresh-runs CO, checks oracle provenance and static anchors, compiles the CP native chain with `-fno-fast-math -ffp-contract=off`, and uses the exact fixed cold initialization for every sequence. Across 192 sequences × 12 requests = 2,304 requests, the CP output matches the independently assembled CN lookup + FrameSA + CF + CG + CH reference byte-for-byte.
