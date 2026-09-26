# E007u — rear BPC/ABF411 clean DMI provider

Parent Git: `2d706a0e` (E007t Gamma151 clean provider PASS).

Status: **STAGED / COMPILE-ONLY**.

## Goal

Close the BPC/ABF411 first-native-frame DMI blocker without embedding a captured Windows payload.

The selected OV13858 BPCABF4.1 tuning exposes one 65-point semantic LUT shared by all six relevant regions. E007u derives the transformed points using the source-locked common-setting arithmetic and packs the Titan680 selector-1 table at DMI register `0x4908`.

## Clean authority

Pinned rear tuning:

- module: `com.surface.tuned.rfc_ov13858`;
- SHA-256: `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`;
- root: symbol `0x1a`, version 4.1;
- trigger: `0x228`;
- regions: `0x22c, 0x22e, 0x230, 0x232, 0x234, 0x236`;
- all six regions have identical LUT fields for this first-frame authority.

Source-locked common-setting behavior:

- clamp source sample to 0..511;
- scale = 3.0;
- transformed point = FRINTA(8192 / (sample * scale)), with the source-defined zero handling;
- 65 transformed points.

Titan680 packing:

- 64 little-endian words;
- low 9 bits: current point;
- next field: absolute next-minus-current delta, clamped to 9 bits and shifted by 9;
- 256 bytes total;
- DMI `0x4908`, selector 1.

## Private validation

The clean semantic derivation and packer reproduce **4/4 retained rear BPC/ABF payloads byte-for-byte**:

- startup0;
- startup1;
- startup2;
- steady_ac8.

No captured payload bytes are committed or used as runtime producer inputs.

## Integration

E007u extends the stable-DMI chain after E007t. It intercepts only `0x4908 / selector 1 / 256 bytes` and delegates everything else.

After this provider, **DSX101 is the only remaining first-frame payload generator blocker**. `PERIOD_CFG` remains the transport-state blocker.

## Safety

Compile-only. No module load, camera access, MMIO, DMI submission or RT-CDM submission.
