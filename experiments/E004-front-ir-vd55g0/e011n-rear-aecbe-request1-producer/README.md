# E011N — rear AEC_BE request-1 normal producer

Parent Git: `a2d8f7c31f49ecc8a8acf284d0a63ac28c7e95d3` (E011M).

Status: **SOURCE + LIVE IMMEDIATE PRODUCER CLOSED for the request-1 normal AEC statistics replacement.** Native rear ISP runtime remains denied.

E011C had already shown the normal rear AEC_BE request slot entering its first validation at the cold `64x48`, `3658x2058`, four-`0x3ffff` seed, then receiving a watched bulk replacement to `32x32`, full `4064x2286`, with all four thresholds later reading `0x3e7ff`. What remained open was the immediate producer and request ordering behind that replacement.

Pinned source identifies the producer as `CamX::CAECStatsProcessor::SetStatsConfigFromAlgoConfig` at RVA `0x83DF68`. The helper consumes AEC engine frame-control fields for horizontal/vertical region counts, ROI-selection policy and thresholds. When ROI selection is 1 it calls `GetCropWindow` at RVA `0x83D7B0` rather than using the direct ROI words; that path derives the current statistics crop from the request/HAL crop and active geometry. The same helper writes duplicated BG and BE configuration records for downstream publication.

Fresh original-Windows tracing then established the ordering. A pre-request invocation already carried `32x32`, ROI selection 1 and four `0x3e7ff` thresholds. The first observed `CAECStatsProcessor::ExecuteProcessRequest` at RVA `0x8356E0` carried request ID 1. The request-1 call to `SetStatsConfigFromAlgoConfig` again carried `32x32`, ROI selection 1 and four `0x3e7ff` thresholds; its crop-selection path resolved to full `4064x2286`. Thus the request-1 normal AEC algorithm/frame-control path is the immediate normal producer that explains E011C's cold-to-caller replacement.

This run did **not** independently trap the immediate second request-1 IFE AEC_BE validation after the producer call. The downstream application is therefore linked through E011C's exact watched slot copy rather than re-proved in this same run. The result closes the producer identity and order behind the E011C transition; it does not authorize native runtime or collapse the remaining AWB_BG, BFStats25/AF, neutral-3A, LSC/GTM or VFE1 WM16 IRQ/DMA/IOMMU retirement gates.

The E011N rear4K holder completed StartAsync and StopAsync with 383 valid 4K handles and breakpoints were cleared. No native rear ISP module was installed or loaded and no RT-CDM submit occurred.

Only source-safe scalar relationships and stable RVAs are committed. OEM bytes, debugger logs, process addresses and optical payloads remain private on SP11.
