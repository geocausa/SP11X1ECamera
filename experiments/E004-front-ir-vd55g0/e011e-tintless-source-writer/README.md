# E011E — Tintless_BG source writer and remaining ordering ambiguity

Parent Git: 933511ea6699f6f374c052e46b769748fe57992b (E011D).

Status: SOURCE WRITER SHAPE PASS, FIRST-CONSUMER PRODUCER ORDER OPEN. Rear ISP runtime remains denied.

The pinned original same-SP11 `QcDeviceMFT8380.dll` IFENode helper at RVA 0x736DB0 writes through pointer table entry 1, which `ExecuteProcessRequest` RVA 0x7453D0 sets to request configuration `+0x360`. The helper's record offset `+0x1A0` therefore resolves to request `+0x500`, exactly the slot read by `TintlessBGStats17` dependency check RVA 0xA10E58 in E011D. The execute function calls this helper after `HardcodeSettings` on the successful configuration path. This is a concrete source writer, not a guessed module mapping.

The helper sets grid 32x24 and zero origin. Its rectangle normally uses inclusive active height and active width; a flag at pointer table `+0xEC` selects half inclusive width instead. An IFENode override flag at `+0x7CAC` substitutes a separate window's inclusive width/height. It sets four threshold lanes with `(1 << (node_field_0x9764 & 31)) - 1`, copies that field into record `+0x28`, and clears record `+0x2C`. For E011D's full 4064x2286 first consumer, the mode selected a full-size result, but the trace did not sample both branch controls, so do not freeze a specific branch predicate for native runtime.

There is a causal mismatch to resolve. E011D's first Tintless request-1 dependency read four 0x3ffff thresholds and record `+0x28=14`. This helper writes both from the same source field in one call; if it alone wrote the final record immediately before that consumer, these values would agree on bit depth. The watched broad copy later made `+0x28=18` while preserving the four thresholds, and request 2 consumed that resulting record. Thus this helper explains the source geometry/record location, but the exact earlier writer/order or intermediate mutation of `+0x28` is still open. Treat the first consumed scalars as observed, not as an inferred single-call output.

Next: use a fresh pre-start write watch on request `+0x528` after the request object is known, or trace writes to node field `+0x9764` and the helper call sequence, with an atomic holder and debugger-safe wait. Also close RS initial request source and other E008p first-frame seeds. No native rear ISP submission until the semantic and VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement gates close.

The private Ghidra project and decompilation remain on SP11 outside Git. Only source-safe offsets, branch relationships and scalar observations are committed.
