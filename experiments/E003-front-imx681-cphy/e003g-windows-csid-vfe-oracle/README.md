# E003g Windows CSID/VFE route oracle — route resolved

Date: 2026-08-28

## Purpose

Freeze and mechanically decode the same-machine Windows front-camera route before any Linux first-frame change. Windows remains the behavioral oracle; external Linux implementations and Qualcomm downstream source are used only to name/register-map hardware that Windows itself proves active.

## Route-complete acquisition

Physical target: this Surface Pro 11 / X1E80100.

Windows device explicitly selected: `Surface Camera Front` / Sony IMX681.

Trigger: WinRT `MediaCapture` + `MediaFrameReader`. Two independent runs returned `StartAsync=Success`; both were stopped through normal `MediaFrameReader.StopAsync()` teardown. SP7 KDNET captured physical MMIO at:

`IDLE -> LIVE1 -> POST -> LIVE2 -> POST2`.

Every phase contains these complete hardware resources:

| block | physical range | size |
|---|---|---:|
| CSID wrapper | `0x0acb6000..0x0acb6fff` | 4 KiB |
| CSID0 | `0x0acb7000..0x0acb8fff` | 8 KiB |
| CSID1 | `0x0acb9000..0x0acbafff` | 8 KiB |
| CSID2 | `0x0acbb000..0x0acbcfff` | 8 KiB |
| VFE0 / IFE0 | `0x0ac62000..0x0ac65fff` | 16 KiB |
| VFE1 / IFE1 | `0x0ac71000..0x0ac74fff` | 16 KiB |
| CSIPHY2 | `0x0ace8000..0x0ace9fff` | 8 KiB |

Canonical raw capture:

- `raw/E003G_ROUTE_ORACLE_20260828.log`
- bytes: `2457712`
- SHA-256: `fd8edcee46e794dffa0e2305331f19d4e9d2cd5b9ba5197484aa1cc7fa6c6fca`

`extract_route_oracle.py` validates the expected dword count for every region in all five phases, emits per-region live-value CSVs, and writes `route-oracle-summary.json`.

## Critical correction to the first E003g checkpoint

The 2026-08-27 first capture inspected CSID0 plus VFE0 and initially treated the address space after the 16 KiB VFE0 window as a possible continuation of VFE0. That interpretation is superseded.

The Denali camera resources are separate VFE instances: VFE0 starts at `0x0ac62000`, while VFE1 starts at `0x0ac71000`. The route-complete Windows capture proves VFE0 is inactive for this front WinRT stream and VFE1 is active. The original raw 2026-08-27 capture remains committed as historical evidence, but its pending "extend VFE0 to 0xf000" action must not be resumed.

## Proven Windows physical route

Wrapper live state is reproducible in both passes:

- CSID0 wrapper `IO_PATH_CFG0`: `0x00000001`;
- **CSID1 wrapper `IO_PATH_CFG0`: `0x00000101`**;
- CSID2 wrapper `IO_PATH_CFG0`: `0x00000001`.

Using the CSID680 top-register definition, bit 8 is `OUTPUT_IFE_EN`. Only CSID1 sets it.

Independent block activity agrees:

- CSID0: 79 live non-zero/non-sentinel dwords, no LIVE1/LIVE2 differences; default/inactive programmed state;
- **CSID1: 107 live non-zero/non-sentinel dwords, with only six expected counter/timestamp differences between passes; active**;
- CSID2: same inactive/default pattern as CSID0;
- VFE0: **zero** live non-zero/non-sentinel dwords;
- **VFE1: 217** live non-zero/non-sentinel dwords, with 34 expected live-variable address/status fields;
- CSIPHY2: active with the already-established C-PHY state.

Therefore the Windows front RGB route is:

**IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1**.

Both POST and POST2 return exactly to IDLE across every captured region.

## CSID1 IPP decode

Qualcomm's published CSID680 register table mechanically identifies `CSID +0x300` as IPP `CFG0`, not RDI0. Windows CSID1 has:

- IPP `CFG0 +0x300 = 0x802b2000`;
- IPP `CFG1 +0x310 = 0x00007241`;
- horizontal crop `+0x35c = 0x0eff0000` -> pixels `0..3839`;
- vertical crop `+0x360 = 0x086f0000` -> lines `0..2159`;
- format measure config `+0x388 = 0x08700f00` -> `3840x2160`.

`CFG0` decodes as:

- path enable = 1;
- VC = 0;
- CSI-2 data type = `0x2b` = RAW10;
- decode-format field = 2 (10-bit decode in this CSID680 layout);
- DT_ID = 0.

This establishes an important boundary: the accepted sensor mode remains RAW10 VC0 `3840x2640 @ 30 fps`, while the Windows WinRT processing path crops that incoming mode to `3840x2160` at CSID1 IPP before IFE processing.

## VFE1 / IFE1 decode

The VFE1 bus register layout matches VFE680. Windows actively enables these bus clients (`CFG bit0 = 1`):

- WM0 `FULL_Y` — `CFG=0x00000011`;
- WM1 `FULL_C` — `CFG=0x00000011`;
- WM2 `DS4` — `CFG=0x00000011`;
- WM3 `DS16` — `CFG=0x00000011`;
- WM11 `STATS_BE0` — `CFG=0x00010001`;
- WM12 `STATS_BHIST0` — `CFG=0x00010001`;
- WM13 `STATS_TINTLESS_BG` — `CFG=0x00010001`;
- WM14 `STATS_AWB_BG` — `CFG=0x00010001`;
- WM18 `STATS_RS` — `CFG=0x00010001`.

Windows does **not** enable the VFE680 `PIXEL_RAW` or RDI0/1/2 write-master clients for this WinRT stream. The Windows oracle is therefore a full ISP video pipeline, not evidence for copying a particular RDI write-master mode into Linux.

## Linux representation boundary

Our current `drivers/media/platform/qcom/camss/camss-vfe-680.c` explicitly documents that RDI is all it supports today and maps full VFE RDI output to WM24..26. It does not represent Windows' FULL/DS/statistics ISP pipeline.

Therefore the smallest defensible Linux transport gate is:

1. preserve the Windows-proven physical instance route **CSIPHY2 -> CSID1 -> VFE1**;
2. keep sensor mode0 at the accepted Windows values, initially including the full 3840x2640 RAW10 transport;
3. use Linux's existing supported RDI output path on VFE1 for the smallest transport proof rather than cloning Windows FULL/DS/statistics programming;
4. keep the experiment bounded, one-shot, fail-closed, with complete stream/power teardown;
5. only after raw transport is proven decide whether a later Linux pixel/IPP implementation should reproduce the Windows 3840x2160 crop/full-ISP path.

No Linux first-frame patch is part of this oracle checkpoint.

## Register-map reference policy

For semantic register names/layout only, E003g consulted Qualcomm's published `camera-driver` tree at commit:

`0f16924ff6a7f9bb56a7e958016da2ed8a174f2f`

Relevant CSID680/VFE680 tables explicitly map X1E-family camera hardware. Those source files are not treated as behavioral truth: **the values, active route, crop, and write-master state accepted above all come from the same-machine Windows capture.**

A separate working Linux implementation remains a differential reference only; its timing/workaround choices are not promoted without Windows proof.

## Safety state after acquisition

The Windows boot was one-shot. After capture the machine returned to unchanged Golden:

- kernel `7.1.5-sp11-render-parity-v4+`;
- `sp11_entry=7.1.5-sp11-fullio-v19c`;
- GRUB `saved_entry=sp11-audio-fullio-v19c`;
- empty `next_entry`;
- Golden kernel/initrd/DTB hashes unchanged.
