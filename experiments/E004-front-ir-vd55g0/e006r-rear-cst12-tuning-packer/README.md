# E006r — Titan680 CST12 rear-tuning packer

Parent Git: `8847baf0` (E006q rear MNDS23 compile PASS).

Status: **COMPILE-ONLY / OFFLINE**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Replace the 19 startup-only CST12 callback words with a semantic provider that follows the same producer chain as Windows:

selected rear CST12 tuning -> CST12 common-library unpacked state -> Titan680 register packing.

Captured Windows RT-CDM register words are validation only and are not embedded.

## Exact Titan680 command ownership

Pinned Surface `QcDeviceMFT8380.dll` identifies
`CamX::IFECST12Titan680::CreateCmdList` and
`CamX::IFECST12Titan680::PackIQRegisterSetting`.

CreateCmdList emits exactly:

- `0x6160`, count 1
- `0x6168`, count 18

The hardware gap at `0x6164` is not written. This exactly matches the 19-register E006l CST12 ownership set.

The packer consumes the 22-field CST12 unpacked state in the semantic order:

`enable, c00,c10,c20,c01,c11,c21, m00..m22, o0..o2, s0..s2`.

The implementation in `camss-e006r-cst12.inc` reproduces the exact Titan680 13-bit signed matrix/offset/scale placement and 12-bit clamp placement. Module enable remains an explicit module-state input rather than being guessed from serialized header fields.

## Exact rear tuning authority

The already-source-selected rear MSHW0491 tuning authority is:

- file: `com.surface.tuned.rfc_ov13858.bin`
- SHA-256: `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`
- module: `com.surface.tuned.rfc_ov13858`

Its unique `cst12_ife` record is symbol 28, version 1.2, 108 bytes. Exact DeviceMFT parameter-parser decompilation shows four scalar header words, a `(kind=2, revision-symbol=582)` reference pair, then fixed reserve blocks of 12/12/36/12/12 bytes. Therefore the CST reserve begins at byte 24 and is exactly 84 bytes:

- `c_x0 = [0,0,0]`
- `c_x1 = [4095,4095,4095]`
- matrix float32 values recorded in `TUNING-SAFE.json`
- `o = [0,2048,2048]`
- `s = [0,0,0]`

Qualcomm's CST12 common calculation converts the nine matrix floats with `FloatToQNumber(...,10)`, whose reference implementation is `roundf(value * 2^10)`. The resulting Q10 matrix is:

`[601,117,306,-338,510,-172,-427,-83,510]`.

This is tuning-derived state, not a Windows command-buffer replay. Cross-package audit also found the same IFE CST reserve in every archived Surface camera tuning package, while the IPE CST payload differs, reinforcing that this is an actual pipeline-specific tuning record.

## Private validation

The retained private E006a startup0 and startup1 MAIN packets were decoded locally. For each capture:

1. the 19 CST12 words were extracted privately;
2. they were inverted to the semantic 22-field CST state;
3. that state matched the selected rear tuning reserve plus `enabled=true`;
4. the clean Titan680 packer reproduced **19/19** words exactly.

No raw command bytes or raw Windows register values are committed.

## Coverage

E006p implemented 78 Crop12/RoundClamp12 startup-only words.
E006q implemented 20 MNDS23 startup-only words.
E006r implements 19 CST12 startup-only words.

That makes **117/184 startup-only words implemented**, and **585/714 total startup registers (81.9%)** with concrete providers when combined with E006o's 468 safe singleton providers.

## Runtime gate

This remains compile-only. Native rear Linux ISP submission is still denied. The remaining startup-only families contain stats configuration and other tuning/state producers that must be closed on their own semantics; they must not be replaced by captured constants.

Next: continue the remaining 67 startup-only producer burn-down, preferring the small source-defined IQ config families before stats producers.
