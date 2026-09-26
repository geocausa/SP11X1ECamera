# E006y — Titan680 AWBBGStats17 semantic startup packer

Parent Git: 81402fd8 (corrected E006x TintlessBGStats17 compile PASS record).

Status: **COMPILE-ONLY PASS**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Close the final 18 startup-only registers, AWBBGStats17 at 0xB860..0xB8A4, from adjusted semantic AWB Bayer-grid state.

## Exact Titan680 closure

Pinned Surface QcDeviceMFT8380.dll source-locks IFEAWBBGStats17Titan680:

- CreateCmdList 0x180b39720 emits 0xB86C count 5, 0xB880 count 10, and one word each at 0xB868, 0xB864 and 0xB860.
- CreateSubCmdList 0x180b398a0 patches only the enable word.
- PackIQRegisterSetting 0x180b39950 is the exact same hardware function used by TintlessBGStats17 and the same semantic field algorithm clean-room implemented by E006w.
- Hardware capability helper 0x180b39870 is shared.
- AWBBG ValidateDependenceParams 0x1809fe600, AdjustROIParams 0x1809fe120 and Execute 0x1809fe780 define the AWB-specific upstream boundary.
- Dependence-copy helper 0x1809fdf60 consumes the AWB BGBE state and the same request blackLevelOffset at byte offset 0x2170.

The compile-only Linux wrapper therefore maps the AWB register window onto the E006w semantic core with delta 0x800. AWB algorithm policy, striping and ROI adjustment remain upstream Linux producer responsibilities.

## Private validation

The retained E006a rear Windows startup packets are decoded only by validate-private.py. Startup1 and startup2 each invert and repack exactly for all 18 AWBBG words; startup3 and startup4 omit the block. No raw Windows packet bytes or captured register values are committed.

## Coverage on compile PASS

E006y will complete startup-only producer coverage:

- startup-only implemented: **184/184 (100%)**
- concrete startup providers: **653/714 (91.5%)**
- remaining startup-only registers: **0**

The remaining 61 of 714 startup registers are the previously classified non-startup-only contracts: dynamic producers and startup-specific shared-register variants. They are not silently treated as solved by this milestone.

## Build result — PASS

The full E006 verifier chain through E006y passed in an isolated copy of the accepted CAMSS source.

- W=1 warnings/errors: 0
- qcom-camss.ko: 13,644,248 bytes
- SHA-256: `c0ce367dde73434d9951ec7454772ef48aac3ad55371ff0d1abc7c68cd075aed`
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- retained symbols: `e006y_awbbg17_lookup`, `e006y_awbbg_stats17_recipe`
- install/load/camera/RT-CDM submission: none

## Runtime gate

Compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED**. Full parity still requires the upstream 3A/state producers and the remaining dynamic/startup-shared contracts to be wired and validated.

Next: audit the remaining 61 non-startup-only callback contracts and join all providers into the non-submitting packet integration path.
