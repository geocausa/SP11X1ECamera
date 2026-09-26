# E006w — Titan680 AECBEStats17 semantic startup packer

Parent Git: f1240a5f (E006v rear RSStats14 compile PASS).

Status: **COMPILE-ONLY PASS**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Close the 18 AECBEStats17 startup-only words at 0xB060..0xB0A4 from adjusted semantic AEC BE state. Captured Windows register values are validation only and are not embedded.

## Exact Titan680 command topology

Pinned Surface QcDeviceMFT8380.dll source-locks IFEAECBEStats17Titan680:

- CreateCmdList 0x180b3f660 emits five ranges: 0xB06C count 5, 0xB080 count 10, then one word each at 0xB068, 0xB064 and 0xB060.
- PackIQRegisterSetting 0x180b3f860 fills the 18-word image from adjusted Bayer-grid state.
- CreateSubCmdList 0x180b3f7b0 patches only the enable bit in 0xB060.
- AECBEStats17::AdjustROIParams 0x180a06288 and ValidateDependenceParams 0x180a067d8 define the modern producer boundary.

The 18 words encode H/V ROI offsets and grid counts, adjusted region width/height, R/B/GR/GB upper thresholds, five common black-level-derived lower thresholds, Q4 Y coefficients, the source-defined 0xFFFF region sample pattern, QUAD_SYNC_EN and module enable.

## Source closure beyond register packing

The request field consumed by the Titan680 packer at byte offset 0x2170 is source-locked as `blackLevelOffset`: the BLS update path publishes and logs that exact field before the stats modules consume it. The Titan680 Bayer-grid firmware sibling independently names CFG bit 9 as `QUAD_SYNC_EN` and names the high/low threshold outputs as r/gr/gb/b/y max/min.

The provider accepts already-adjusted semantic AEC BE state. AEC algorithm policy, stripe selection and ROI adjustment remain upstream Linux producer responsibilities and are not frozen to one Windows startup capture.

## Private validation

The retained E006a Windows rear startup packets are decoded only by `validate-private.py`. Startup1 and startup2 each invert to semantic state and repack exactly across all 18 words; startup3 and startup4 omit the AECBE block. The committed validation summary contains no raw packet bytes or captured register values.

## Coverage on compile PASS

E006w will add all 18 AECBEStats17 startup-only words:

- startup-only implemented: **148/184**
- concrete startup providers: **617/714 (86.4%)**
- remaining startup-only registers: **36** — TintlessBGStats17 and AWBBGStats17, 18 words each

## Build result — PASS

The E006g/j/l/m/o/p/q/r/s/t/u/v/w verifier chain passed and the complete staged provider set was injected into an isolated copy of the accepted CAMSS source.

- W=1 warnings/errors: 0
- qcom-camss.ko: 13,641,464 bytes
- SHA-256: `048f5c3ed40f418646d814ce544b68b5fabe003cbb50e0b6bc8887019b7a0421`
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- retained symbols: `e006w_aecbe17_lookup`, `e006w_aecbe_stats17_recipe`
- install/load/camera/RT-CDM submission: none

## Runtime gate

Compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED**. Upstream Linux AEC state production must eventually supply the semantic inputs for full parity.

Next: TintlessBGStats17, then AWBBGStats17.
