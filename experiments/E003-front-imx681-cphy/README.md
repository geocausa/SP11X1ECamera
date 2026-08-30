# E003 — front IMX681 / CSI-2 C-PHY

## Goal

Bring up the Surface Pro 11 front RGB camera natively on Linux after accepted rear-camera production integration, while preserving the FullIO v19c Golden recovery path.

## Same-machine Windows oracle boundary

Already mechanically established from this SP11's installed camera packages and platform parser:

- sensor: Sony IMX681 / `SONY0681` / `MSHW0490`;
- Linux 7-bit address `0x10`; FAST/400 kHz CCI;
- identity register `0x0004`, expected `0x0aff`;
- CCI route: **CCI1 / master1**;
- receiver: **CSIPHY2**;
- sensor signalling: **CSI-2 C-PHY**, proven by `0x0111 = 0x03`;
- one trio is high-confidence from `0x0114 = 0`, to be host-side confirmed before streaming;
- MCLK4 19.2 MHz; reset GPIO237;
- LDO3_M 1.8 V and LDO7_B 2.8 V;
- first normal target: RAW10 VC0 mode0, 3840x2640 @ 30 fps, line length 6752, frame length 3554, output pixel clock 548.57 MHz.

Canonical evidence remains under `../E001-windows-oracle-map/derived/`. Proprietary package bytes are never committed.

## Safety / experiment split

1. **E003a — static C-PHY + sensor-driver audit.** No hardware mutation.
2. **E003b — electrical identity only.** Power/reset/MCLK4/CCI1 master1, no CSI endpoint, no stream.
3. **E003c — native IMX681 V4L2 bind**, still no CSI streaming.
4. **E003d — C-PHY graph/receiver configuration — ACCEPTED.** Immutable IMX681 → CSIPHY2 link with PM/electrical idle and stream block proven.
5. **E003e — mode0 standby — ACCEPTED.** Exact Windows init + 3840x2640@30 mode0 programmed with MODE_SELECT=0; fixed one-trio C-PHY metadata proven and CSIPHY2 idle.
6. **E003f — receiver-only C-PHY electrical activation — ACCEPTED.** Under a VFE0-powered host-context harness, CSIPHY2 matched all 121 Windows-live final registers exactly and unwound cleanly while IMX681 remained non-transmitting. E003g later proved that this VFE0 call supplied host context only; the active Windows front output route is CSID1 -> VFE1.
7. **E003g — Windows CSID/VFE route resolved.** A route-complete two-pass same-machine Windows oracle proves the front physical path is **IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1**. CSID1 IPP receives RAW10 VC0 and crops the 3840x2640 sensor mode to 3840x2160 for the Windows ISP path. VFE1, not VFE0, is active. Linux VFE680 currently supports only RDI output, so the next bounded transport gate must preserve the Windows-proven CSID1/VFE1 instance route while using Linux's supported raw RDI path.
8. **E003h — Windows-parity VFE1 PIX transport, active.** The front physical RDI frame is proven but is explicitly not Windows parity. The parity path is IMX681 -> CSIPHY2 -> CSID1 IPP -> VFE1 PIX/ISP -> FULL QC10C. The first bounded PIX runtime executes the complete pre-CSID RT-CDM prefix (13 FIFO0 completions) and starts IMX681, then times out before VFE1 Epoch0. Same-machine static work has since closed IFE `0x804` as logical-only for front use-case 2 and recovered the real CSID `0x804` IPP start semantics. Static patch `0042` now matches the exact Windows CSID1 RX/BUF/IPP/TOP masks and two omitted zero writes, adds read-only pre-teardown CSID telemetry, builds with Golden vermagic and passes a fail-closed patch/source/oracle inspection. **No new runtime is authorized yet**; next package and inspect one exact `0042` one-shot candidate before a single diagnostic.

Each runtime gate must keep Golden as saved default, use a one-shot candidate, and verify audio/touch/Wi-Fi before and after.
