# E009e — physical first-normal AF zoom into source-forward BF ROI

Status: **SAME-SP11 LIVE AF INPUT OBSERVED; FOUR STARTUP SELECTOR-1 PAYLOADS EXACT OFFLINE; REAR ISP RUNTIME DENIED**.
Parent E009d `130026ef` and port-map `befd1d3a`.

## Bounded original Windows session

On 2026-09-28 SP11 booted Windows once via the guarded direct-EFI
BootNext helper. A fresh one-shot rear Color VideoRecord NV12 3840×2160
holder initialized, waited for the probe, then streamed eight seconds:
Start/Stop succeeded with **52 valid 4K handles**. The exact pinned
`QcDeviceMFT8380.dll` was loaded in FrameServer before Start. SP7
external KD used a process-scoped, read-only processor *execute*
breakpoint at `af_util_adjust_roi` RVA 0x628AB0. It inspected only scalar
fields at entry and immediately continued after each hit; no code or
register was changed. The process breakpoint was removed, `bl` was empty,
and Windows rebooted normally to protected Golden Linux. The overlap guard
passes: Golden kernel, saved entry, empty next entry and idle cameras.

Four sampled pre-request GetParam calls (three manual, one auto) used CAMIF
4064×2286, ROI type 0, zoom float32 **1.0** and loaded HAF fractions
**0.25/0.25**. In the subsequent auto-continued subset, one first-normal
AF call from RVA 0x61FBF8 had zoom bits **0x3F7F3F0F**, or
**0.9970559477806091**, with the same CAMIF/type/HAF pair. Twenty later
calls from that same caller had zoom 1.0. A separate GetParam call also
had zoom 1.0. The observed transient is therefore an actual request-stage
scalar, not the E009d post-hoc illustrative 0.998 value. The breakpoint
itself did not carry an RT-CDM packet ID, so assigning that AF call to
packet1 uses the known E008g startup order plus the independently
measured packet shape; it is not a direct per-packet trace correlation.
The upstream calculation that produced zoom 0.9970559 is still open.

Private Windows holder and log remain on SP11; the external debugger
terminal/private scalar ledger remain on SP7. No raw pointer, debugger
transcript, OEM binary, image, RAW data, captured DMI or payload hash is
committed or exported.

## Forward comparison

`offline-roi.c` accepts **two caller-supplied zooms**: the first normal
request and settled requests. It uses the pinned selected HAF 25% pair,
accepted crop, E008z default AF rectangle, E009c request-scoped even/BAF
5×5 handoff, E008t per-packet BF semantics and E007e packer. Packet0
retains its independent IFENode hardcode seed. The offline host code has
no camera or CAMSS runtime call site and embeds no captured ROI coordinate.

`audit-private.py` pins same-SP11 MFT and tuning hashes, checks the selected
serialized HAF pair, supplies the **physically observed float32** zoom
for packet1 and 1.0 for packets2/3, then privately compares original
selector-1 DMI:

| Sample | Exact selector-1 bytes |
| --- | ---: |
| startup0 | 300/300 |
| startup1 | 300/300 |
| startup2 | 300/300 |
| startup3 | 300/300 |
| one retained steady | 300/300 |

A zoom-1.0 negative control for packet1 matches 250/300. This is the
first source-forward four-startup BF ROI payload match with an independent
same-device physical AF scalar. It is bounded to the named corpus and one
live AF session; it does not prove all request policies or complete rear
command packet parity.

## Next gates

Source-derive the upstream zoom/input metadata for startup and steady
requests, then feed the request-scoped E009c handoff from Linux-owned
state. Do not freeze 0.9970559 as a driver startup constant. Independently
close E008p AEC/AWB/statistics/LSC/GTM semantic seeds and E005m/n VFE1
WM16 composite-group-7 IRQ, buffer-generation and DMA/IOMMU retirement
before any native rear ISP submission. Golden, front native PIX, rear RAW
plus software 4K and IR-off policies remain protected.
