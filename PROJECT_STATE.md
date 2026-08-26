# Project state

**Updated:** 2026-08-26  
**State ID:** E001 Windows oracle map  
**Golden remains:** SP11 Audio FullIO v19c

## Current boundary

E001 has completed the implementation-grade static/host routing map needed to begin a Linux rear-camera experiment. The one-shot Windows oracle boot returned cleanly to Linux. Running kernel is still `7.1.5-sp11-render-parity-v4+` from FullIO v19c, GRUB `saved_entry=sp11-audio-fullio-v19c`, `next_entry` is empty, and Linux still exposes zero `/dev/video*` / `/dev/media*` nodes.

No camera kernel/DT/runtime change has yet been installed.

## Exact SP11 camera hardware

- rear RGB: OmniVision **OV13858**, `OVTID858`, `MSHW0491`;
- front RGB: Sony **IMX681**, `SONY0681`, `MSHW0490`;
- front IR/Hello: ST **VD55G0**, `SMO55F0`, `MSHW0492`;
- camera platform: Qualcomm **Spectra 695 / X1E80100**, Surface `MSHW0495`.

## Windows-derived board routing

The exact installed `CAMP_PCFG_MSHW0495.bin` and `qccamplatform8380.sys` were decoded/reversed. The driver parser proves the packed platform connection fields and the flattened CCI-master split.

| Sensor | CCI route | Receive PHY | Physical mode |
|---|---|---|---|
| OV13858 rear | **CCI0 master1** | **CSIPHY1** | 4-lane D-PHY |
| IMX681 front | **CCI1 master1** | **CSIPHY2** | **1-trio C-PHY** |
| VD55G0 IR | **CCI0 master0** | **CSIPHY0** | to be finalized later |

Front IMX681 C-PHY is independently proven by Microsoft's own sensor register program: `CSI_SIGNALING_MODE (0x0111) = 3`, with Linux CCS definitions independently identifying value 3 as CSI-2 C-PHY.

Windows MIPI-CSI MMIO resources line up with upstream X1E CSIPHY0/1/2/4 and CSITPG blocks, so Windows is using the same receive fabric Linux models.

## Rear OV13858 first-target facts

Windows power/resources:
- reset GPIO **110**;
- MCLK **cam_cc_mclk1_clk @ 19.2 MHz**;
- LDO6_M 1.8 V;
- LDO1_M 1.2 V;
- LDO5_M 2.8 V;
- LDO16_B 2.9 V;
- exact D0/D3 order/delays are in E001 `power-map.md`.

Probe:
- Linux 7-bit slave address **0x10**;
- ID register **0x300b**;
- expected ID **0xd855**;
- Qualcomm FAST CCI mode.

Transport:
- VC0 / RAW10;
- four lanes (`laneAssign=0x3210`);
- Windows route **CCI0 master1 -> CSIPHY1**;
- 474.24 MHz RAW pixel rate => **1.1856 Gbit/s per lane**, **592.8 MHz link frequency**;
- Microsoft's PLL is not mainline's stock 540/270 MHz OV13858 profile (`0x0300=0x05`, `0x0301=0`, `0x0302=0xf7`, `0x0303=0`).

Therefore E002 must not simply wire the generic mainline OV13858 mode and call it parity. Reuse the upstream driver infrastructure, but introduce/audit an SP11 Windows-derived mode/link profile.

## Reuse boundary

Reuse upstream Linux:
- X1E CAMSS;
- CCI;
- D-PHY/CSID/VFE/media-controller infrastructure;
- generic OV13858 driver architecture.

Derive Surface-specific behavior from Windows:
- board routing;
- power/reset/regulator sequencing;
- MCLK;
- sensor modes/PLL/link frequency;
- front C-PHY extension;
- later privacy LED/IR illumination and image-quality parity.

## Remaining Windows parity observations

Not blocking rear E002:
- exact runtime `settleTimeNS` value used by Windows receiver;
- privacy LED transition timing/ownership;
- whether any specialized profile changes receiver routing.

Keep them on the parity backlog; do not guess them into Linux.

## Next action

**E002 — rear OV13858 D-PHY infrastructure.**

From Golden v19c, audit the current X1E CAMSS/CCI/CSIPHY source and Denali DT, then create the smallest isolated candidate that describes only the proven rear path. First milestone is safe enumeration/probe; streaming comes only after the graph and power lifecycle are proven.
