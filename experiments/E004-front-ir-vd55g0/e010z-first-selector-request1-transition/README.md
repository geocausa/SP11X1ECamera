# E010z — first selector request identity and cold-seed transition

Status: **the first BHist selector after cold rear 4K start is request ID 1 and consumes the 90% cold seed; that same request-owned context is later overwritten with the full active crop by a bulk per-request config copy, after which a later selector for request ID 1 sees full crop.**

A fresh same-SP11 Windows run armed the pinned BHist selector (RVA 0xA06BE8) immediately after QcDeviceMFT8380.dll loaded and before releasing reader start. No selector hit occurred during MediaCapture initialization. The first selector hit occurred only after START.GO.

At that first selector:
- request identity at request context + 0x1ff8 was 1
- selected BHist context pointer at request context + 0xf20 was the fixed request-owned slot
- the selected BHist rectangle was (0,0,3658,2058)

A write watch on the same request-owned width field then stopped in the bulk config copy path. Immediately before the watched store the slot still held (0,0,3658,2058). Single-stepping the watched store changed the same slot to (0,0,4064,2286).

The live copy state showed:
- destination base = the selected request-owned slot
- source base = a separate per-request config object
- copy return site = RVA 0x740E5C, within the request-frame copy path
- the source object's BHist rectangle was the full active crop

A subsequent selector hit again reported request ID 1, the same selected request-owned slot, now containing (0,0,4064,2286).

Combined with E010X's writer proof, the sequence is therefore:

1. cold/default IFENode HardcodeSettings seeds BHist from active bounds using width - floor(width/10), height - floor(height/10)
2. request 1's first BHist selector consumes that 90% seed
3. the request-frame bulk config copy overwrites the same request-owned slot from the live per-request config
4. a later selector for the same request ID 1 sees full crop

For the rear 4064x2286 active bounds:
- cold seed = 3658x2058
- normal per-request replacement = 4064x2286

This removes the earlier ambiguity between a permanent 90% request policy and startup behavior. The 90% rectangle is a cold/default first-selector seed, while the live request config supersedes it later in request 1.

The run closed cleanly with 418 valid 3840x2160 frame handles and successful StopAsync.

Native implication: model the 90% BHist rectangle as startup/default first-selector state derived from the active bounds, not as a hard-coded 3658x2058 rectangle and not as a permanent per-request 90% crop. Preserve the later caller-owned per-request replacement path.

This result does not by itself authorize native rear ISP runtime. Remaining first-frame stats seeds and the VFE1 WM16 IRQ/DMA/IOMMU generation-safe stop-and-drain proof remain gates.
