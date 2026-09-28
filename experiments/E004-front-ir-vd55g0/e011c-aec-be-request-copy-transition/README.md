# E011C — rear AEC_BE request slot transition

Parent Git: 92419330a061da049bf28575b20c84a6b7d8e5c9 (E011B).

Status: LIVE REQUEST-SLOT TRANSITION PASS, IMMEDIATE SECOND CONSUMER OPEN. Native rear ISP runtime remains denied.

A fresh same-SP11 Windows one-shot used the original OEM rear Color VideoRecord NV12 3840x2160 path. The isolated E011C holder had an atomic entry marker, separate pre-enumeration/pre-initialization/start gates, and 30-minute debugger-safe operation waits. CDB attached to FrameServer after Init and armed the pinned `AECBEStats17` validation entry RVA 0xA06910 before StartAsync.

The first hit carried request ID 1 in context `+0x1FF8`. Its request configuration pointer at context `+0xF20` selected the normal AEC_BE slot `+0x3E0`: 64x48 grid, origin zero, rectangle 3658x2058, four threshold lanes 0x3ffff and source bit-depth field 18. This agrees with E011A and E011B's cold path. A hardware write watch on that exact slot's width field caught the original MFT bulk configuration copy at the SIMD store. Before that store, the selected slot still held the cold values. Stepping the store changed the slot to grid 32x32, zero origin, full rectangle 4064x2286; the first two threshold lanes were 0x3e7ff at that point while the other two had not yet been overwritten. The same request context still read ID 1.

After the copy, an AEC_BE validation hit at request ID 1153 selected the identical request configuration pointer and read grid 32x32, full rectangle 4064x2286, and all four threshold lanes 0x3e7ff. The breakpoint had been cleared during the watch and rearmed later; the immediate second request-1 validation was **not** captured. Thus the observed request-1 cold slot replacement and later consumption are established, but the exact first-to-second selector timing is not closed as it was for BHist in E010Z. The full rectangle and 32x32 grid are caller-owned per-request configuration, not a permanent cold default. No live HDR exposure-type selector or Tintless_BG seed was observed.

The holder completed StartAsync, acquired 1,302 valid 4K frame handles, passed StopAsync, and ended. CDB breakpoints were cleared and detached. The ordinary reboot returned SP11 to Golden Linux; the overlap guard passed with no active camera process, camera module, or GRUB next entry. This run did not load, submit, or enable native rear ISP code.

Next: trace the distinct Tintless_BG `+0x500` initialization and RS state, then close remaining E008p statistics/3A/LSC/GTM seeds. A tightly scoped follow-up may capture the immediate request-1 AEC_BE consumer, keeping its breakpoint enabled while watching the write. VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement remains a separate gate before native rear runtime.

Only source-safe scalar observations and outcomes are committed. OEM bytes, raw debugger output and optical pixels remain private on SP11.
