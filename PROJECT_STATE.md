# Project state

**Updated:** 2026-08-27
**State ID:** E002b-r3e NACK resolved to Windows-exact ID-transfer gate
**Golden remains:** SP11 Audio FullIO v19c

## Current boundary

E002b-r3f booted stably and used the Windows-exact OV13858 ID transaction (`0x10`, FAST/400 kHz, register `0x300b`, 16-bit expected `0xd855`) on Windows-proven CCI0/master1. The first transfer still returned `-ENXIO`; teardown was clean and no crash occurred.

Live TLMM inspection exposed the strongest remaining omission: CCI GPIO103/104 are correctly muxed, but all X1E camera-MCLK capable GPIO96..99 are func0/unclaimed and the rear node has no MCLK pinctrl state. Before another powered probe, prove from Windows which physical pad carries `cam_cc_mclk1_clk`, then add only that pinctrl correction.

## E002b-r3e boundary and r3f preparation — 2026-08-27

r3e safely reached the first CCI transaction after the full rear power/MCLK/reset sequence, but returned `-ENXIO`. A one-shot Windows KD session plus the exact installed QTI sensor/platform blobs now confirm CCI0/master1, FAST 400 kHz, Linux address `0x10`, GPIO110/reset, MCLK1 19.2 MHz and the existing rail order. The Windows sensor configuration identifies using a 16-bit read at `0x300b`, expected `0xd855`; r3e instead used a generic three-byte read from `0x300a`.

E002b-r3f is prepared as a transaction-only correction. Its module and candidate initrd both build byte-identically across two clean builds. Golden is unchanged. The GRUB audit found no camera-blocking parameter; future accepted camera gates must, however, pass a second strict boot without `clk_ignore_unused pd_ignore_unused` so those permissive flags cannot mask missing DT ownership.

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

**E002b-r3f — Windows-exact rear OV13858 identity transaction.**

Reuse the accepted r3d DT/power route byte-for-byte and change only the r3e identity transfer to a 16-bit read at `0x300b`, expecting `0xd855`. First test permissively; if it passes, repeat without `clk_ignore_unused pd_ignore_unused`. Do not add/start CSI streaming until this identity lifecycle is proven.


## E002b-r1 accepted — isolated camera regulator providers

The first E002b attempt exposed a regulator-provider isolation bug: adding PM8550-B LDO16 into the existing Golden `regulators-0` provider caused that whole provider to fail registration, cascading into audio and Wi-Fi deferrals. This was not a missing-kitchen DTB.

E002b-r1 fixes the architecture by registering PM8550-B LDO16 and PM8010-M LDO1/LDO5/LDO6 in separate camera-only RPMh provider devices with no registration-time voltage constraints. The one-shot r1 boot passed with Wi-Fi, playback, capture and CAMSS intact; all four new camera rails remained at 0 users / 0 mV.

Next gate: E002b-r2 rear OV13858 identity probe. The probe module must be candidate-initrd-only; the shared Golden `/lib/modules` tree must not be modified. No CSI endpoint or streaming is allowed in r2.
