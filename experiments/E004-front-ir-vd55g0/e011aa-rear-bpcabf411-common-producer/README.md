# E011AA — rear BPCABF411 independent common producer

Parent: `9908619df544e565d05aef5f50067a7822ff46b9` (E011Z).

Status: **OFFLINE COMMON ARITHMETIC PASS; REQUEST-SIDE INPUT BINDING OPEN.**

E007a could pack seven calculated BPC/ABF411 outputs but did not produce them.
E007u independently closed the selector-1 DMI table. E011AA adds an independent
semantic-input producer for E007a's seven register words. No captured register
or DMI value is a producer input.

## Source boundary

Pinned same-SP11 DeviceMFT SHA-256:
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

Common calculation: RVA 0x9C16B0. Titan680 packer: RVA 0xB41090.
Rounding helper RVA 0x14D0 is FRINTA.

The independently written producer accepts:

- two level terms: common-region indices 0x52/0x53;
- two two-point preserve curves: indices 0x54..0x57;
- two five-point curves: indices 0x58..0x61;
- five normalized reserve anchors.

The four non-LUT preserve terms and ten curve terms lie beyond the common
calculation's request-dependent scaling block. That block changes region
offsets 0x1C..0x11C and 0x188, not the selected 0x148..0x184 fields.

The producer calculates Q8 preservation levels, signed inverse slopes, byte
curve values, inverse curve slopes and their shifts, then packs the existing
0x49B8/BC, 0x49D0/D4, 0x49D8/DC and 0x49E0 boundary.

Important exact details:

- preserve coefficients clamp to 256; byte curve coefficients clamp to 255;
- equal level endpoints are separated by one before denominator calculation;
- zero/unusable denominators fail closed in the independent code;
- flat and increasing byte curves use the source-defined minimum delta of one;
- normalized reserve anchors are squared, scaled by 4095, then truncated;
- inverse curve quotient uses the original logarithmic shift BEFORE the
  stored nibble is clamped to 15;
- preserve slopes use the source's descending shift search, signed division,
  FRINTA rounding and final -256..256 clamp.

The ordinary Python producer runs offline. There is no kernel integration,
module build/install/load, request caller or hardware submission in E011AA.

## Installed tuning finding

The rear tuning has four BPCABF4.1 roots, not one universal Default authority.
Sensor-specific roots contain different low-gain preservation/curve terms,
and their high-gain regions change again. Default-only seven-register replay
would therefore be wrong even though E007u's stable DMI LUT can still match.

The old front-container selector decoder rejects this rear file's richer
selector table. E011AA does not relax that decoder or guess its mode ancestry.
Runtime module selection, interpolation-trigger binding and exact
serialized-to-runtime reserve-field mapping remain explicit next gates.

## Validation

`verify-private.py` pins both originals and keeps their bytes on SP11.
It executes only the original arithmetic slices inside Unicorn:

- 0x9C1D34..0x9C223C: two five-point curves and inverse slopes;
- 0x9C2474..0x9C26F8: preserve levels and signed slopes.

Original math helpers execute in the emulator as well. PAC prologue/return
instructions are handled only inside the isolated arithmetic emulator; no
Windows or Linux runtime code is patched. No device is mapped.

Results:

- 24 installed leaf cases;
- 120 deterministic synthetic cases;
- five precision/clamp/equal-endpoint boundary cases;
- **149 exact native-source differential cases**;
- six invalid semantic inputs rejected;
- all **22/22 retained seven-register records match clean-produced leaf
  candidates**, including **3/3 startup records**, or 154 register matches.

This last comparison proves candidate output coverage, NOT which leaf the
live request selected. Captured output matching is never used to choose
runtime policy. Phase 3 has no complete seven-register block in this corpus.

Only aggregate counts are emitted in `VALIDATION-SAFE.json`; tuning leaves,
original register words, command bytes and process addresses remain private.

## Next

Use a fresh bounded Windows identity to observe the actual BPC common input,
interpolated region and reserve arguments at pre-request/request boundaries.
Bind those observed input identities to tuning/module/trigger source, then
feed the clean-produced states into four independent E008o packet objects.

Complete E008o composition and the separate VFE1 WM16 same-generation
IRQ/DMA/IOMMU stop/retirement gate remain open. Native rear hardware ISP
runtime remains denied. Golden, front camera and RAW/software fallback are
unchanged.

Run on SP11:
`python3 experiments/E004-front-ir-vd55g0/e011aa-rear-bpcabf411-common-producer/verify-private.py`.
