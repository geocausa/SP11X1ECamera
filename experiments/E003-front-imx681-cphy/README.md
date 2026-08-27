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
5. **E003e — mode0 standby.** Exact Windows mode0 register lifecycle + transport metadata, MODE_SELECT still prohibited and CSIPHY2 idle.
6. **E003f+ — bounded C-PHY transport and first frame**, only after preceding gates pass.

Each runtime gate must keep Golden as saved default, use a one-shot candidate, and verify audio/touch/Wi-Fi before and after.
