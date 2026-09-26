# E007s — rear zero-stable DMI binding

Parent Git: 30f8a5a1 (E007r first-native-frame blocker audit PASS).

Status: **COMPILE-ONLY PASS**.

## Goal

Remove the two false stable-DMI gaps identified by E007r without making the
remaining startup request look complete.

The rear E006b corpus proves:

- PDPC 0x3D08 selector 1 is exactly 512 zero bytes;
- LSC 0x4308 selector 3 is exactly 884 zero bytes.

Both identities are stable across the rear corpus and byte-identical to the
accepted front path. Their SHA identities are reproduced by generating zeros;
no captured payload bytes are embedded.

## Binding

`camss-e007s-zero-stable.inc` extends E007q's stable callback.

It serves:

- 0x3D08/1 -> 512 zero bytes;
- 0x4308/3 -> 884 zero bytes.

Every other stable identity delegates to an explicit `stable_nonzero`
provider.

The complete-request validator deliberately returns `-EOPNOTSUPP` when that
nonzero provider is absent. Therefore closing PDPC/LSC3 cannot accidentally
hide the still-open BPC/ABF, Gamma and DSX tables.

## Build result — PASS

The full E006/E007 provider chain through E007s compiled in an isolated accepted CAMSS source copy.

- zero-authority hash checks: PASS for PDPC selector 1 and LSC selector 3;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,786,024 bytes;
- SHA-256: `7eb50ac26c11da016b86eb4d25dda87cc7757206649ae84e976309800994d099`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained symbols: `e007s_rear_stable`, `e007s_rear_validate_request`, `e007s_rear_prepare_dynamic`, `e007s_rear_fill_slot`, `e007s_rear_zero_stable_recipe`;
- install/load/camera/DMI/RT-CDM submission: none.

## Boundary

No IQ math is added. No Windows payload bytes are copied. No module install,
load, camera stream, DMI submission or RT-CDM submission is part of E007s.
