# E006x — Titan680 TintlessBGStats17 semantic startup packer

Parent Git: bb549786 (E006w rear AECBEStats17 compile PASS).

Status: **STAGED / COMPILE PENDING**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Close all 18 TintlessBGStats17 startup-only words at 0xB660..0xB6A4 from adjusted semantic Tintless BG state.

## Shared Titan680 Bayer-grid core

Pinned Surface QcDeviceMFT8380.dll proves IFETintlessBGStats17Titan680 emits the same five-range 5+10+1+1+1 topology as AECBE, shifted by +0x600. Its PackIQRegisterSetting at 0x180b39950 is field-for-field the same semantic algorithm already clean-room implemented by E006w: ROI/grid geometry, channel maxima, black-level-derived minima, Q4 Y coefficients, region sampling, QUAD_SYNC_EN and enable.

The Tintless dependency path reads the same request byte offset 0x2170, source-locked by E006w as blackLevelOffset. Tintless uses the same Titan680 hardware-capability helper (0x180b39870) and modern 16..512 region / 64x64 grid limits.

E006x therefore translates the Tintless register window onto the compiler-checked E006w semantic core rather than duplicating the packer.

## Private validation

The retained private E006a oracle is decoded only by validate-private.py. Startup1 and startup2 each repack exactly for all 18 words through the shared semantic layout; startup3 and startup4 omit the block. No raw register values or packet bytes are committed.

## Coverage on compile PASS

- startup-only implemented: **166/184**
- concrete startup providers: **635/714 (88.9%)**
- remaining startup-only registers: **18** — AWBBGStats17

## Runtime gate

Compile-only. Native rear Linux ISP and RT-CDM submission remain **DENIED**. Upstream Tintless state production remains required for parity.

Next after compile PASS: AWBBGStats17.
