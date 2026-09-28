# E011G — rear Tintless_BG first-consumer seed resolved

Parent Git: ec6b0190550cf957d97f398ae994f013bae4029e (E011F).

Status: SOURCE + LIVE FIRST-CONSUMER SEED CLOSED for the pinned rear4K mode. Other E008p gates and native rear ISP runtime remain open/denied.

The original same-SP11 `QcDeviceMFT8380.dll` has two source writes to the same Tintless request record. IFENode's helper RVA 0x736DB0 addresses pointer table entry 1 plus `+0x1A0`, which is retained/request configuration `+0x500`. In E011F, its first retained invocation saw node field `+0x9764=18`, half-width selector 0 and window override 0, then wrote grid 32x24, origin zero, full 4064x2286, four `(1 << 18)-1 = 0x3ffff` thresholds, and record `+0x28=18`.

A separate branch of `IFENode::HardcodeSettings` RVA 0x735940 writes through the same pointer table entry 1 at `+0x1A0`. Its condition is changed-family bit `0x100`, or cold argument `param4=1`, or initialization state at node `+0x9A70` equal to zero. It derives the four threshold lanes from node `+0x9764`, initializes the same 32x24/zero-origin geometry and active width/height, but explicitly writes the eight bytes at record `+0x28` as `14,0`. This source store explains the E011F retained `+0x28` changing from 18 after the helper to 14 before the first dependency while thresholds remained 0x3ffff. The actual HardcodeSettings store instruction was not separately trapped, so the exact true branch arm in that physical call is not claimed.

E011D and E011F directly observed the first `TintlessBGStats17` dependency at RVA 0xA10E58 for request ID 1 consume the request `+0x500` record with grid 32x24, zero origin, full 4064x2286, four 0x3ffff lanes and `+0x28=14`. E011F's later watch caught a direct store in Tintless Execute RVA 0xA1174C writing `18` over `14` in the retained record. E011D also observed request ID 2 consume the same geometry/thresholds and `+0x28=18`. This is a cold first-consumer seed followed by module-owned update, not a permanent word-14 policy.

Native implementation must derive the record from active bounds and source mode controls, preserve the HardcodeSettings cold/changed-family branch and the subsequent module-owned update, and remain detached until the other first-frame stats/3A/LSC/GTM seeds and VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement pass. This stage does not authorize any native rear ISP runtime submission.

All private OEM bytes and debugger output remain on SP11; Git holds only source-safe scalar relationships.
