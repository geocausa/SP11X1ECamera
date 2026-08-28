# E003g route-resolved handoff — 2026-08-28

## Resume point

Branch: `experiment/e003-front-imx681-cphy`.

Pre-route-resolved checkpoint: `7d891b3` (`E003g: archive Windows CSID/VFE oracle checkpoint`).

Golden remains unchanged:

- kernel `7.1.5-sp11-render-parity-v4+`;
- `sp11_entry=7.1.5-sp11-fullio-v19c`;
- GRUB saved entry `sp11-audio-fullio-v19c`;
- one-shot `next_entry` empty after Windows return.

## Accepted chain

- E003b: same-machine IMX681 identity / power / CCI route accepted.
- E003c: native IMX681 V4L2 bind accepted.
- E003d: immutable IMX681 -> CSIPHY2 one-trio C-PHY graph accepted.
- E003e: exact Windows init + 3840x2640@30 mode0 programmed in standby with `MODE_SELECT=0`.
- E003f: host-powered receiver-only CSIPHY2 activation matched 121/121 Windows-live receiver registers and unwound cleanly while the sensor remained non-transmitting.
- E003g: route-complete same-machine Windows CSID/VFE oracle now resolves the active downstream instances and processing path.

## Canonical new oracle

Directory:

`experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/`

Raw capture:

`raw/E003G_ROUTE_ORACLE_20260828.log`

SHA-256:

`fd8edcee46e794dffa0e2305331f19d4e9d2cd5b9ba5197484aa1cc7fa6c6fca`

Two independent Windows front-camera reader starts returned `Success`; both were stopped normally. KD captured complete wrapper, CSID0/1/2, VFE0/1 and CSIPHY2 windows at `IDLE -> LIVE1 -> POST -> LIVE2 -> POST2`. Both post states equal idle exactly.

## Critical route result

The active Windows front route is:

**IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1**.

Proof:

- wrapper CSID0 = `0x00000001`;
- wrapper **CSID1 = `0x00000101`**, uniquely setting `OUTPUT_IFE_EN` bit8;
- wrapper CSID2 = `0x00000001`;
- CSID1 alone shows active receiver/path counters and IPP programming;
- VFE0 has zero live non-zero dwords;
- VFE1 has 217 live non-zero dwords and active bus clients.

The earlier pending action to capture a supposed VFE0 `+0x4000..+0xefff` continuation is **cancelled**. VFE0 and VFE1 are separate 16 KiB resources at `0x0ac62000` and `0x0ac71000`. Do not resume the old VFE0-extension interpretation.

## CSID1 processing result

CSID680 maps `+0x300` to IPP CFG0. Windows CSID1 programs:

- `IPP CFG0 = 0x802b2000` -> enabled, VC0, DT `0x2b` RAW10, 10-bit decode;
- `HCROP = 0x0eff0000` -> 3840 pixels;
- `VCROP = 0x086f0000` -> 2160 lines;
- format measure = `0x08700f00` -> 3840x2160.

The sensor still transmits the accepted 3840x2640 mode0. Windows WinRT crops it to 3840x2160 at CSID1 IPP before IFE processing.

## VFE1 result and Linux boundary

Windows VFE1 enables FULL Y/C, DS4, DS16 and several statistics write masters. It does not use PIXEL_RAW or RDI0/1/2 as the WinRT output.

Our current upstream-style CAMSS VFE680 implementation explicitly supports only RDI output and maps full-VFE RDI to WM24..26. Therefore Windows' ISP output topology cannot simply be copied into this driver.

The first Linux transport gate should preserve the **instance route** proven by Windows but use Linux's supported raw RDI path:

**IMX681 -> CSIPHY2 -> CSID1 -> VFE1 RDI**.

This is a transport proof, not yet a Windows-equivalent processed-video pipeline.

## Exact next task

1. Audit/adjust the E003d/e/f media graph and any hard-coded host-power selection so front mode0 reaches CSID1 and VFE1, not CSID0/VFE0.
2. Trace CSID Gen2 start programming for the selected Linux RDI line and confirm VC0/DT0x2b/decode format without importing Windows IPP crop bits into the RDI register block.
3. Trace VFE1 RDI WM24 programming, buffer ownership, stream start/stop order, timeout path and unwind.
4. Prepare a new one-shot candidate with the IMX681 stream block removed only inside the bounded test path; preserve exact accepted E003e sensor init/mode values and E003f CSIPHY2 electrical table.
5. Before reboot: static build, module ABI, DT compile/decompile parity, route assertions and explicit Golden/GRUB checks.
6. Runtime target: the smallest raw transport proof with bounded timeout and guaranteed stop/power unwind. Do not yet claim Windows-equivalent 3840x2160 processed video.
7. On any failure, return to Golden before further changes and archive evidence before the next hypothesis.

## External-source rule

Qualcomm `camera-driver` commit `0f16924ff6a7f9bb56a7e958016da2ed8a174f2f` is accepted only as a register-layout/name reference. Windows on this SP11 remains the behavioral oracle. External Linux implementations remain differential references only.
