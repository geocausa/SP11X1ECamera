# E007k — rear TMC141 GTM-facing producer static closure

Parent: E007j rear GTM/TMC Windows oracle PASS.

Status: **STATIC PRODUCER CONTRACT PASS**.

## Result

The rear GTM DMI path consumes one specific TMC141 anchor family:

- source knots: TMC request state offset `0x5104`, 7 float32 values;
- destination knots: offset `0x5120`, 7 float32 values;
- cubic coefficients: offset `0x51B0`, 15 float32 values;
- GTM domain: offset `0x6228`, 257 float32 entries / 0x400 bytes used by the clean GTM backend.

The pinned same-SP11 `QcDeviceMFT8380.dll` decompile establishes:

- `0x180923B90`: TMC interpolation/request-state assembler;
- `0x1809255F0`: TMC141 anchor/knee-point solver;
- `0x180926570`: seven-point anchor generator;
- `0x1809267A0`: histogram/statistics-informed anchor refinement;
- `0x1809276E8`: 7-knot source/destination -> 15-coefficient monotone cubic helper.

The output descriptor in `0x180923B90` maps three TMC anchor families into the request state. The clean GTM backend's `0x5104/0x5120/0x51B0` triplet is **family #2**.

## Coefficient closure

`tmc141-coeff.py` is a clean float32 port of `0x1809276E8`.

The pinned Windows helper proves `TMC_COEF` is **not an independent dynamic producer**: it is calculated from the 7-float source and destination knot vectors.

A later E007o revalidation corrected the clean-port exactness claim. The current `tmc141-coeff.py` is byte-exact for **12/15** accepted E007j request states; R4/R7/R8 differ only at coefficient index 8. This is a clean-port float/operation-order discrepancy, not evidence of additional dynamic coefficient state.

No raw Windows values are committed.

## Remaining TMC parity boundary

The unresolved live producer has now collapsed to the two 7-knot vectors at `0x5104` and `0x5120`, plus their upstream TMC141 runtime inputs.

E007j already showed that only two floats in each 7-float vector evolve during R4..R10 and the vectors are exactly stable from R10 onward. This checkpoint does **not** replace that evolution with request-number replay or captured constants.

Next work should source-lock/capture the upstream inputs to `0x1809255F0` / `0x1809267A0` needed to reproduce those two moving knots cleanly.

No Linux camera runtime, DMI submission or RT-CDM submission occurred.
