# E007t — rear Gamma151 clean provider

Parent Git: a53f18c4 (E007s rear zero-stable DMI binding PASS).

Status: **COMPILE-ONLY PASS**.

## Goal

Close the Gamma151 first-frame DMI blocker without embedding a captured Windows LUT.

The rear selected tuning contains one semantic Gamma1.5 curve shared by all three channels. E007t derives that curve from the pinned OV13858 tuning file and packs it with the Titan680 Gamma151 12-bit wire rule.

## Source lock

Pinned rear tuning:

- module: com.surface.tuned.rfc_ov13858;
- SHA-256: 4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635;
- gamma15_ife_v2 root symbol: 0x24;
- version: 1.5;
- trigger symbol: 0x268;
- region symbol: 0x26e;
- region bytes: 3084 = 3 × 257 float32 samples.

The three channels are identical. All 257 samples are finite, integral, monotonic, and cover 0..4095.

Pinned Surface Gamma151 common-setting dispatch resolves to 0x1809F3A60 and supports the widened 12-bit path used here.

## Clean packing rule

For each of 256 output words:

- current sample: unsigned 12-bit value;
- next-minus-current: signed 12-bit delta, saturated to [-2048, 2047];
- packed word: value | ((delta & 0xFFF) << 12).

The committed authority is the semantic 257-sample tuning curve, not the 1024-byte Windows DMI payload.

## Private validation

The clean packer reproduces **9/9 retained rear Gamma payloads byte-for-byte**:

- startup0 selectors 1/2/3;
- startup1 selectors 1/2/3;
- steady_ac8 selectors 1/2/3.

All three selectors are identical, as predicted by the selected tuning authority.

No raw Windows Gamma words are emitted or committed.

## Integration

The E007t stable-DMI adapter intercepts:

- DMI register 0x5F08;
- selectors 1, 2 and 3;
- exactly 1024 bytes per selector.

Everything else delegates to the still-open stable provider. BPC/ABF and DSX therefore remain explicit first-frame dependencies and validation continues to fail closed until they are installed.

## Build result — PASS

The full E006/E007 provider chain through E007t compiled in an isolated accepted CAMSS source copy.

- semantic authority: 257 integral 12-bit samples;
- private Gamma DMI validation: 9/9 exact;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,804,856 bytes;
- SHA-256: `f4713c8455a35dfc6ecba5fc01d154a377cdfb53361c2cf7bb99ebf08374ed0f`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained symbols: `e007t_rear_stable_nonzero`, `e007t_rear_validate_request`, `e007t_rear_prepare_dynamic`, `e007t_rear_fill_slot`, `e007t_rear_gamma_recipe`;
- install/load/camera/DMI/RT-CDM submission: none.

## Safety

Compile-only. No module load, camera access, MMIO, DMI submission or RT-CDM submission.

## Next

After compile PASS, the remaining first-frame payload blockers are BPC/ABF and DSX; PERIOD_CFG remains the transport-state blocker.
