# E006x — Titan680 TintlessBGStats17 semantic startup packer

Parent Git: bb549786 (E006w rear AECBEStats17 compile PASS).

Status: **STAGED / COMPILE-ONLY**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Close the 18 TintlessBGStats17 startup-only words at 0xB660..0xB6A4 from adjusted semantic Tintless Bayer-grid state, without freezing captured Windows values.

## Exact Titan680 closure

Pinned Surface QcDeviceMFT8380.dll source-locks IFETintlessBGStats17Titan680:

- CreateCmdList 0x180b45e60 emits five ranges: 0xB66C count 5, 0xB680 count 10, then one word each at 0xB668, 0xB664 and 0xB660.
- PackIQRegisterSetting 0x180b39950 is bit-for-bit the same semantic Bayer-grid packer used by E006w AECBEStats17, translated by register-window delta 0x600.
- Hardware-capability helper 0x180b39870 is shared with E006w.
- Tintless-specific CheckDependenceChange, AdjustROIParams, ValidateDependenceParams and Execute remain separate upstream producer policy.

The common semantic state is H/V ROI offsets and grid counts, adjusted region width/height, R/B/GR/GB upper thresholds, black-level-derived lower thresholds, Q4 Y coefficients, the source-defined 0xFFFF sample pattern, QUAD_SYNC_EN and enable state. The request field at byte offset 0x2170 is the same source-locked blackLevelOffset used by E006w.

The Linux compile-only wrapper intentionally reuses the E006w semantic state/packer rather than duplicating a second register-shaped implementation. Tintless AEC/tintless policy, striping and ROI adjustment remain upstream Linux responsibilities.

## Private validation

The retained E006a rear Windows startup packets are decoded only by validate-private.py. Startup1 and startup2 each invert and repack exactly across all 18 words through the shared semantic core; startup3 and startup4 omit the Tintless block. No raw packet bytes or captured register values are committed.

## Coverage on compile PASS

E006x will add all 18 TintlessBGStats17 startup-only words:

- startup-only implemented: **166/184**
- concrete startup providers: **635/714 (88.9%)**
- remaining startup-only registers: **18** — AWBBGStats17 only

## Runtime gate

Compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED**. Upstream Linux Tintless/AEC state production must eventually supply the semantic inputs for full parity.

Next after compile PASS: AWBBGStats17.
