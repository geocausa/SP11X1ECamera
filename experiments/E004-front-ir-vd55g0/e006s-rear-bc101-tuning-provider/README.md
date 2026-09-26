# E006s — Titan680 BC101 rear-tuning provider

Parent Git: `f7751d66` (E006r rear CST12 compile PASS).

Status: **STAGED / COMPILE-ONLY**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Implement the three remaining startup-only BC101 words from the same semantic state used by Windows rather than from captured command values:

- 0x3F60
- 0x3F64
- 0x3F68

## Exact Titan680 packing

Pinned Surface `QcDeviceMFT8380.dll` source-locks `CamX::IFEBC101Titan680`.

`CreateCmdList` emits one contiguous three-word range beginning at 0x3F60.

`PackIQRegisterSetting` consumes five semantic 16-bit values:

- module enable -> bit 0 of 0x3F60
- four calculated BC region values -> low byte / bit16 byte of 0x3F64 and 0x3F68

The BC101 common-setting function `FUN_1809c42f0` preserves zero and otherwise clamps each of the four region values to 128 before the Titan680 byte packing.

## Rear tuning authority and disabled path

The selected rear tuning authority remains:

- file: `com.surface.tuned.rfc_ov13858.bin`
- SHA-256: `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`
- module: `com.surface.tuned.rfc_ov13858`
- record: `bincorr10_ife_v2`, symbol 23, version 1.0

The parsed rear record has module enable = 0. Its four region values are 112,112,112,112, but they are not consumed on the disabled execution path.

Static DeviceMFT closure shows:

1. Titan680 allocates the 12-byte BC register image and explicitly zero-initializes all three words.
2. `CheckAndUpdateChromatixData` propagates the rear tuning enable into the active module-enable state.
3. With enable false, `IFEBC101::Execute` takes the disabled `CreateSubCmdList` path rather than the interpolation/calculation path.
4. `CreateSubCmdList` changes only bit 0 of the existing first word to the requested enable value and writes all three words.
5. Therefore the selected rear startup BC101 output is the semantic three-word disabled image, not a captured constant.

The provider also implements the enabled packing rule for future Linux-owned state by applying the exact common-library clamp and Titan680 byte placement.

No raw E006a command words are embedded or required to derive this output.

## Coverage

E006s adds 3 startup-only registers:

- startup-only implementation: 120/184
- concrete startup providers including E006o singletons: 588/714 (82.4%)

The other four small startup-only IQ config words (BayerGTM101, BayerLTM101, LCAC111 and UVGamma101) are intentionally left for the next checkpoint; all four are source-locked as module-enable bit words.

## Runtime gate

This is compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED**.
