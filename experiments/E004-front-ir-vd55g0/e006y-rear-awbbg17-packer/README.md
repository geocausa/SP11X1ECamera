# E006y — Titan680 AWBBGStats17 semantic startup packer

Parent Git: 81402fd8 (corrected E006x TintlessBGStats17 compile PASS record).

Status: **STAGED / COMPILE-ONLY**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

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

## Runtime gate

Compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED**. Full parity still requires the upstream 3A/state producers and the remaining dynamic/startup-shared contracts to be wired and validated.

Next after compile PASS: audit the remaining 61 non-startup-only callback contracts and join all providers into the non-submitting packet integration path.
