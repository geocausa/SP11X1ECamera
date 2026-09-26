# E007p — rear TMC141 clean family-2 producer

Parent Git: f5116b6e (E007o TMC141 post-return discriminator PASS).

Status: **USERSPACE ALGORITHM PASS — 20/20 COMPLETE SRC/DST/COEF TRIPLETS BYTE-EXACT**.

## Goal

Close the remaining rear GTM/TMC dynamic producer without replaying captured Windows knots.

E007o proved that the final GTM-facing state already exists immediately after `TMC141Interpolation::CalculateAnchorKneePoints`; no downstream publication/marshalling rewrite is involved. E007p therefore ports the exercised rear solver path itself.

## Source-locked path

Pinned same-SP11 `QcDeviceMFT8380.dll`:

- `0x1809255f0` — TMC141 anchor/knee solver;
- `0x180926570` — seven-point generator;
- `0x1809276e8` — monotone cubic coefficient helper;
- rear mode `0x60800`;
- scale index: `log(runtime_0c) / log(1.03)`, ARM64 `FRINTA`, clamp to 235;
- family-2 publication weights are zero in the validated path.

The exercised rear path contains two source-only stages omitted by the earlier partial port:

1. global-TMC source scaling using TUNE indices 0x29..0x2d, RUNTIME +0x480/+0x48c and TUNE exponents 2/3;
2. when CTRL 0x8244 is enabled, the rear-mode post-generator scale/clamp on SRC knots 1/2 using RUNTIME +0x488 and TUNE index 0x28.

DST remains the seven-point-generator output in this path.

## Math fidelity

The pinned binary's positive-finite ARM64 `powf` path is measurably bit-different from the host Linux `libm` for values used by TMC141. E007p contains a clean translation of that bounded math path using its lookup and polynomial constants. These are generic math implementation constants; no camera capture or request payload bytes are embedded.

This closes two prior byte-order/rounding gaps:

- E007o SRC/DST: now 20/20 exact;
- E007k coefficient helper: literal ARM float operation order now gives 20/20 exact in E007o and 15/15 exact against the accepted E007j request states.

## Fail-closed domain

`e007p_tmc141_solve()` accepts only the source-proven rear path:

- mode `0x60800`;
- curve order 5;
- CTRL 0x8234 = 0;
- CTRL 0x8238 = 0;
- CTRL 0x8254 = 0;
- CTRL 0x8244 in {0,1};
- face count 0;
- family-2 publication weights all zero.

Other modes/control combinations return `-EOPNOTSUPP` rather than being guessed.

## Private validation

`validate-private.py` compiles the clean C producer independently and uses E007o's private H01..H20 semantic input buffers. Captured POST knots and coefficients are used only as final validation oracles.

Result:

- SRC: 20/20 byte-exact;
- DST: 20/20 byte-exact;
- COEF: 20/20 byte-exact;
- complete triplets: 20/20 byte-exact;
- captured PRE/POST knots used as producer inputs: **no**;
- raw captured float values committed/emitted: **no**.

The Windows evidence volume was mounted read-only for validation and unmounted immediately afterward.

## Build

`tmc141-clean.c` compiles on SP11 ARM64 with both GCC and Clang using strict warnings and `-fno-fast-math -ffp-contract=off`.

## Boundary

This closes the clean rear TMC141 family-2 algorithm for the exercised rear 4K domain. The next step is binding its SRC/DST/COEF output into the already-clean GTM producer/DMI materializer, then auditing the remaining first-native-frame blockers.

No Linux camera stream, DMI submission or RT-CDM submission occurred.
