## E002e ACCEPTED — rear 592.8 MHz transport metadata — 2026-08-27

Automatic driver endpoint validation proved four-lane D-PHY at 592800000 Hz. Read-only V4L2 controls returned LINK_FREQ=592800000 and PIXEL_RATE=474240000, exactly matching the Windows QTI RAW10/four-lane transport. The immutable enabled OV13858->CSIPHY1 link remained present; sensor runtime PM stayed suspended/usage 0 and MCLK1/CSIPHY1/CSI1 timer enable counts stayed 0 after identity. No PLL/mode register array or stream operation was executed. E002e is accepted. Next is E002f: program the focused Windows Surface mode0 PLL/register delta in sensor standby, still with no stream/CSIPHY power.

## E002e prepared — rear 592.8 MHz transport metadata, hard no-stream — 2026-08-27

Exact Windows QTI mode data proves the Surface rear transport uses RAW10/four-lane D-PHY at 474.24 MHz pixel rate = 1.1856 Gbit/s/lane = 592.8 MHz DDR link frequency. Windows mode0 is 4076x2806 and differs from upstream full-res in only 19 of 199 shared final register values plus a small address delta. E002e intentionally changes no sensor PLL/mode register arrays: it adds 592.8 MHz endpoint/control metadata, validates four-lane D-PHY at probe, and installs a DT-selected stream guard before runtime-PM power-up. Candidate initrd A/B are byte-identical at `48517776...`; candidate DTB `0e25c28f...`.

## E002d ACCEPTED — native rear OV13858 -> CSIPHY1 graph — 2026-08-27

Read-only `MEDIA_IOC_G_TOPOLOGY` proved `ov13858 1-0010` pad0 -> `msm_csiphy1` pad0 with flags `0x3` (ENABLED + IMMUTABLE) and data-link type. Sensor remained runtime-suspended (usage 0), MCLK1/CSIPHY1/CSI1 PHY timer enable counts stayed 0, reset stayed asserted, and no rail activity occurred after boot identity. E002d is accepted. Next gate is E002e: reconcile Windows rear mode/lane timing with native OV13858 link-frequency/mode metadata, still with no stream operation.

## E002d prepared — rear OV13858 <-> CSIPHY1 graph only — 2026-08-27

E002d adds only reciprocal four-lane D-PHY endpoints between the accepted native OV13858 and CAMSS `port@1`, mechanically mapped by the exact X1E source to CSIPHY1 and independently proven by Windows routing. Host lanes are `<0 1 2 3>`, sensor lanes `<1 2 3 4>`, bus type explicitly D-PHY. No link frequency, mode, CSID/VFE route or stream is added. Local source proves async graph completion/media-link creation does not power or stream CSIPHY. Candidate DTB `ea55cafd...`; E002c-r1 kernel/initrd remain byte-identical.

## E002c-r1 ACCEPTED — native OV13858 bind / identity / runtime PM — 2026-08-27

E002c-r1 automatically loaded the accepted RPMh provider, exact V4L2 dependencies and patched native `ov13858` from initrd. The native driver bound to `1-0010`, upstream 24-bit identity passed, then all rails and MCLK tore down with runtime PM `suspended`, usage 0. Loaded sensor module srcversion `02C96088AA5798CD5A70BFE` proves the patched module was running. No sensor CSI endpoint existed and no stream occurred. E002c is accepted. Next gate E002d adds only rear four-lane D-PHY graph wiring to Windows-proven CSIPHY1.

## E002c-r1 prepared — packaging-only fix after manual native PASS — 2026-08-27

E002c r0 automatic loading failed before electrical action because Golden has no module `extra/` directory and r0 emitted only its nested `extra/e002c/`. Loading the exact same provider and patched native driver after full boot passed completely: native OV13858 bound, ID verified, runtime-suspended, rails/MCLK off, reset asserted. r1 changes only initrd packaging: emit the missing parent `extra/` and preserve real insmod errno. r1 initrd A/B are byte-identical at `d1e56f66...`; kernel, DTB and camera module bytes are unchanged.

## E002c prepared — native OV13858 bind only, no CSI — 2026-08-27

E002c now cleanly separates native sensor-driver ownership from transport. Starting from accepted r3g, the DT changes only the rear client compatible to `ovti,ov13858`; no endpoint is added. The exact upstream OV13858 source was adapted only to own Denali's proven four-rail/GPIO110/MCLK1 power lifecycle and runtime PM. The module builds with exact Golden v4 vermagic (`35c99b5...`). A Golden-based initrd containing the accepted RPMh provider, exact V4L2 dependencies and patched native driver was built twice byte-identically (`48e092c4...`). No E002c runtime boot has occurred yet.

## E002b-r3g ACCEPTED — rear OV13858 physical contact / identity — 2026-08-27

The strict A/B boot removed only `clk_ignore_unused pd_ignore_unused` and reproduced the permissive result: GPIO97 `0x00000244`, OV13858 ID `0xd855` at address `0x10`, clean reverse teardown, CAMSS nodes present, Wi-Fi/audio healthy. E002b is accepted. The r3f NACK root cause was the missing physical MCLK1 GPIO97 route. Next gate is E002c: native Linux OV13858/V4L2 bind plus the minimum rear CSI endpoint, with no streaming yet.

## E002b-r3g permissive runtime PASS — 2026-08-27

The one-variable GPIO97 correction changed the rear OV13858 from the r3f `-ENXIO` NACK to a valid `0xd855` chip ID at `0x10`. GPIO97 reads `0x00000244` exactly as Windows did; the unchanged r3f probe then completed and tore all rails/MCLK down cleanly. Wi-Fi, playback and capture remained healthy and Golden remained the saved default. This proves missing physical MCLK1 routing was the r3f NACK root cause. A strict one-shot with only `clk_ignore_unused pd_ignore_unused` removed is required before accepting the identity gate.

## E002b-r3g prepared — physical rear MCLK1 pad proven — 2026-08-27

A one-shot SP11 Windows KD session read X1E TLMM directly. Windows leaves GPIO97 at `0x00000244`: function 1 `cam_mclk`, 4 mA, no pull, output enabled. Golden/r3f Linux reads GPIO97 as `0x00000001`: GPIO/function 0, 2 mA, pull-down, output disabled. Qualcomm's 2026 Hamoa/X1E80100 pinctrl series independently maps `cam_mclk1_default` to GPIO97 and its camera overlay pairs that pinctrl with `CAM_CC_MCLK1_CLK`.

r3g is therefore a DT-only correction applied directly to the exact r3f DTB. It adds one GPIO97 `cam_mclk` state plus `pinctrl-0`/`pinctrl-names` on the existing rear probe node. Kernel, r3f initrd/probe module, rail/reset order, MCLK1 19.2 MHz, CCI0/master1 @ 400 kHz, address `0x10`, and the Windows-exact `0x300b -> 0xd855` transaction are unchanged. Candidate DTB SHA-256: `396259a06edffd4f9e0482480ef02201aa88acd98731db57fbb33358650a0b33`.

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
