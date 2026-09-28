# E011D — rear Tintless_BG first slot and next consumer

Parent Git: ef0e2334eb27e54cda5b0f2349985f46114f5383 (E011C).

Status: LIVE FIRST-CONSUMER PASS, UPSTREAM PRODUCER OPEN. Native rear ISP runtime remains denied.

A fresh original same-SP11 Windows rear Color VideoRecord NV12 3840x2160 one-shot used a new E011D holder with atomic entry marker and debugger-safe timeouts. CDB attached to FrameServer before StartAsync. The first AEC_BE validation at pinned RVA 0xA06910 exposed request ID 1 and its request configuration pointer. Before the first Tintless dependency check, the distinct request `+0x500` slot already contained grid 32x24, origin zero, full rectangle 4064x2286 and four 0x3ffff threshold lanes. The word at record `+0x28` was 14 at this point. This is not AEC_BE's 64x48, 3658x2058 cold record.

The pinned `TintlessBGStats17` dependency check RVA 0xA10E58 then entered for request ID 1. Its context `+0xF20` selected the same request object, and the record at `+0x500` still had exactly those values. A hardware watch on the record width caught a broad OEM MFT configuration copy into the same request object. Stepping the first watched store preserved grid, origin, full rectangle and thresholds while changing record word `+0x28` from 14 to 18. A second watched copy preserved the resulting record. The next Tintless dependency check was request ID 2 on the same configuration pointer and read grid 32x24, full rectangle, all four 0x3ffff thresholds, and `+0x28=18`.

The meaning and producer of the `+0x28` word need static confirmation; the dependency function's compared geometry/threshold fields do not by themselves identify it. The source of the already-populated request-1 Tintless slot before the first AEC_BE validation is not yet traced. The live evidence closes its first consumed scalar seed for this OEM rear mode and the fact that the observed bulk copy does not replace its geometry. It does not license a fixed 32x24 native default for other modes or close the complete Tintless/3A bootstrap.

The holder completed StartAsync, acquired 246 valid rear 4K handles, passed StopAsync, and ended. CDB breakpoints were cleared and detached. Ordinary reboot returned to Golden Linux with overlap guard PASS. No Linux native rear ISP runtime was loaded or submitted.

Next: trace the request `+0x500` pre-consumer writer and mode/active-bounds policy, then RS first-state source and the other E008p gates. VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement remains required.

Only source-safe scalars and outcome are committed; private OEM binary, debugger output and optical pixels remain on SP11.
