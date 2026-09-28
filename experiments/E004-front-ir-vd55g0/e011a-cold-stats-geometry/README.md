# E011A — first rear stats cold geometry

Parent Git: a01a44f606472946143af3ac351302647db25095 (E010Z).

Status: SOURCE + LIVE PARTIAL. This closes the shared cold geometry rule for the first AEC_BE and AWB_BG consumers. It does not close complete stats seed semantics or authorize native rear ISP.

## Source boundary

The pinned original DeviceMFT IFENode::HardcodeSettings at RVA 0x735940 uses the active rectangle's inclusive width and height. Its initialization path (param4=1) sets four BG-style configuration records to a 64 by 48 grid, zero origin, and width - floor(width/10), height - floor(height/10). It sets threshold lanes from the source bit-depth expression (1 << bitDepth) - 1. This branch runs on cold initialization even if the normal changed-family flag is clear. The exact record-to-module mapping, weights and per-request overwrite still require independent proof.

The pinned original AWBBGStats17 dependence checker at RVA 0x9FDF60 reads the request configuration via request context +0xF20 and the selected BG record at +0xCF8. AECBEStats17 validation at RVA 0xA067D8 selects a BG record at +0x3E0. RSStats14 Execute at RVA 0xA0E0D0 and TintlessBGStats17 Execute at RVA 0xA11610 were also selected as observation points. These are source offsets, not native runtime writes.

## Interrupted but cleanly recovered physical session

Fresh E011A-2010A Windows rear Color VideoRecord NV12 3840x2160 holder had an atomic entry marker and a 30 minute operation wait. CDB attached to FrameServer and first entered the request-1 AEC_BE validation point. Its selected record was grid 64x48, origin 0, rectangle 3658x2058. The first observed AWB_BG validation point saw request ID 1 and the same grid, origin and rectangle. The observed bit-depth threshold lanes were 0x3ffff. RS Execute also ran for request ID 1; a step from its initial state produced a 16x1024 pair and related output fields. The four breakpoints were cleared before continuing; Tintless_BG was not observed and no claim is made for it.

The UI allowance ended with FrameServer paused in CDB. On resumption CDB continued, StartAsync succeeded, 656 valid rear 4K frame handles were acquired, StopAsync passed, the holder exited, CDB detached, and ordinary reboot returned to Golden Linux. The overlap guard passed. The long paused interval makes this a startup configuration observation, not an uninterrupted timing trace.

## Native implication and next gate

Derive the BG cold rectangle from active bounds, never embed the observed 3658x2058 as a mode constant. Keep the first request's source-owned replacement separate as in E010Z. A follow-up must prove the Tintless_BG and RS cold branches, map all four BG records to consumers, and observe request-1 copy/transition before E008p can mark their complete initial grid/threshold/weight seed closed. BFStats25, neutral AEC/AWB, LSC/GTM and VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement remain open. Native rear ISP runtime is denied.

Only source-safe scalar observations are recorded here. OEM binaries, raw logs and pixels stay private on SP11.
