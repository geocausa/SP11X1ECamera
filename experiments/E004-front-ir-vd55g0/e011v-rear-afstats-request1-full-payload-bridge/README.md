# E011V — rear AFStatsControl request-1 full-payload bridge

Parent Git: `7346f2ed` (E011U). Evidence: pinned OEM static analysis plus bounded OEM Windows request-1 live trace. Native rear ISP runtime remains denied.

Status: **SOURCE + LIVE REQUEST-1 AF/BF FULL-PAYLOAD BRIDGE CLOSED; SEPARATE PACKET-0 HARDCODE TIMING REMAINS OPEN.**

E011T proved that the observed request-1 IFENode BF consumer takes the normal nonzero 25-ROI path. E011U then closed the request-1 ROI-count mapping from CAF ROI output through `PropertyIDAFStatsControl` to IFENode, but left all 25 ROI validity flags and the full publication payload identity open. E011V closes those two request-1 gaps.

## Static publication boundary

The pinned property value at data RVA `0x147ABC4` is `0x3000000E`, i.e. `PropertyIDAFStatsControl`. The CAF publication-registration path in function RVA `0x816CF0` publishes a `0x1CC0`-byte payload for that property.

`CAFIOUtil::PublishOutput` RVA `0x817710` contains the request-indexed full-record copy. At call site RVA `0x818B7C`, the source is the completed internal AF/BF record, the destination is the request-indexed output slot, and the copy size is exactly `0x1CC0` bytes. This is the same record layout whose BF ROI count reaches IFENode at published offset `+0x1C8C`; first ROI validity is at `+0x354` with `0x24` stride.

## Fresh E011V-0810A live trace

A fresh atomic rear Color VideoRecord NV12 3840x2160 holder was used. `CAFStatsProcessor::ExecuteProcessRequest` RVA `0x8288C0` was observed for request ID **1** before the full-record publication copy.

At the live `CAFIOUtil::PublishOutput` copy call RVA `0x818B7C`:
- copy size was `0x1CC0`;
- source BF words at `+0x1C88/+0x1C8C` were `0,25`;
- destination BF words before the copy were `0,0`;
- after single-stepping the copy, destination words were `0,25`;
- all **25** destination ROI validity fields at `+0x354 + n*0x24`, `n=0..24`, were **1**.

The same request then reached `IFENode::Get3AFrameConfig` BF count load RVA `0x741C7C` with request ID **1**. Its metadata-pool AFStatsControl pointer was a **different allocation** from the CAF request-indexed copy destination, but:
- its BF words at `+0x1C88/+0x1C8C` were again `0,25`;
- all **25** published ROI validity fields were **1**;
- a dword-by-dword comparison over the complete `0x1CC0` bytes against the CAF publication destination produced **zero differences**.

This closes the request-1 AFStatsControl payload bridge as:

`CAF internal AF/BF record -> 0x1CC0 request-indexed publication copy -> metadata-pool PropertyIDAFStatsControl -> IFENode request-1 consumer`.

The metadata allocation is intentionally not claimed to alias the publisher buffer; live proof shows that it does not. The closure is complete payload identity across publication, not pointer identity.

## Session and safety

E011V-0810A completed cleanly:
- `StartAsync=Success`
- **103 valid 4K handles**
- `Stop=PASS`
- trace breakpoints were cleared
- local ARM64 CDB detached cleanly
- fresh SP7 KDNET was stopped after the session

The private CDB, holder and KDNET transcripts were archived under the private E011V session directory before this checkpoint so the raw capture is not lost. They remain off Git.

This does **not** prove that a distinct earlier packet-0 hardcode event did not occur. E008s already source-closed packet-0 filter/coring, centered 5x5 ROI semantics and -3/0 IIR shifts, while E008u/E009e matched startup payloads; the remaining AF/BF question is timing/occurrence of that separate startup fallback if it is still required. Neutral-3A, LSC/GTM and VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remain separate gates.

No native camera module was installed or loaded and no RT-CDM submission occurred. Only stable RVAs, property IDs, offsets and scalar relationships are committed; raw OEM bytes, process addresses and private debugger logs remain private.
