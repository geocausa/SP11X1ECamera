# E010u — request-1 BHist config source-copy watch

Status: **request identity narrowed: the observed request-1 config slot is populated with the full active rear crop through a bulk config copy; the producer of that source config and the earlier smaller startup BHist seed remain open.** Parent evidence: E009h, E010o and E010p.

A fresh same-SP11 Windows rear 4K MediaFrameReader run used debugger-safe extended WinRT waits and a user-mode CDB attached to FrameServer. At the pinned `CAECStatsProcessor::SetBHistConfigFromAlgoConfig` boundary, the first captured setter was processor request ID 0, camera 0, ROISelection 1, with the full active rear crop (4064x2286). This is consistent with E010o/E010p and again does not explain the smaller initial BHist rectangle.

The trace then moved upstream to the per-request configuration construction path. At the candidate request-1 slot, the BHist rectangle fields were zero before population. A write watch on the width field fired inside the request-frame bulk-copy path that copies an approximately 0x818-byte config subobject into the request-owned slot. The destination subobject begins at the request slot plus 0x360 and covers the BHist rectangle. When the same request-1 slot was later observed before recycling/clear, its BHist rectangle was the full active crop (0,0,4064,2286).

This is useful provenance narrowing: the request-1 BHist rectangle is not being synthesized by four local scalar stores at the final request slot; it arrives as part of a copied upstream config object. The live watch also did not expose the smaller 3658x2058 startup rectangle in this request-1 slot. However, the stop currently visible in the debugger is a later bulk clear/recycle of the already-populated slot, so that stop itself is not the producer. Do not infer that the copy source is the original AEC algorithm writer.

Combined with E010o/E010p, the remaining target is now sharper: stop immediately before the config-copy call, inspect the source object's BHist rectangle and its owning request/context, then trace the source object backward to the code that first gives it the smaller startup rectangle. Numeric AEC processor request ID and the BHist selector's request-owned context still need an independent association before changing E009g's caller-owned handoff.

No native rear ISP runtime is authorized by this result. The remaining first-frame AEC/AWB/LSC/GTM semantics and the VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement proof are still gates.
