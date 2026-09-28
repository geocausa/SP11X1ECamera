# E011B — rear AEC_BE/AWB_BG cold slot map

Parent Git: 50b90a67bda479f90c55a44007fd557567126bc4 (E011A).

Status: SOURCE MAP PASS, LIVE REPLACEMENT OPEN. This records the exact first-frame cold record identities and their request consumers. It does not close the full statistics seed or authorize native rear ISP.

## Pinned original source path

In the same-SP11 original `QcDeviceMFT8380.dll`, `IFENode::ExecuteProcessRequest` at RVA 0x7453D0 builds its per-request pointer table: entry 1 is request configuration `+0x360`, entry 3 is `+0xCF8`. It calls `IFENode::HardcodeSettings` RVA 0x735940 with cold-init argument 1 on the first initialization path, then with argument 0 for the ordinary request update. The source places the four AEC_BE cold records at offsets `+0x80`, `+0x3B8`, `+0x438`, `+0x4B8` relative to pointer entry 1. Thus the request object offsets are `+0x3E0`, `+0x718`, `+0x798`, `+0x818`. It initializes a separate AWB_BG record through pointer entry 3 at request offset `+0xCF8`.

All five records use a 64x48 grid, zero origin, active inclusive width minus floor(width/10), active inclusive height minus floor(height/10), and four threshold lanes derived from `(1 << source_bit_depth) - 1`. E011A saw 3658x2058 and 0x3ffff at request ID 1 in the first normal AEC_BE and AWB_BG consumers. These observed scalars agree with the 4064x2286 active bounds and source bit depth 18; the formula, not these values, is the portable seed.

`AECBEStats17::GetAECBEConfig` RVA 0xA05978 reads the request pointer at context `+0xF20`. Its normal path selects request `+0x3E0`. In HDR exposure mode, exposure type 0 selects `+0x798`, type 1 selects `+0x818`, and type 2 selects `+0x718`; an invalid type emits an error. `AWBBGStats17` dependency check RVA 0x9FDF60 reads request `+0xCF8` and request ID at context `+0x1FF8`. These are selector relationships, not claims that the HDR paths were entered during E011A.

The same request setup calls `FUN_180740D88` after configuration processing on one branch. Its broad `0xF508` copy has request and retained node configuration as endpoints, with several subrange copies in the opposite direction. It is a possible transfer/retention boundary, but source alone does not show when the first consumer sees replacement geometry. No replacement for the AEC_BE or AWB_BG slots was watched in E011A. E010Z proves that transition only for BHist.

## Distinct remaining paths

`TintlessBGStats17` dependency check RVA 0xA10E58 reads request `+0x500`, separate from the five cold records above. The HardcodeSettings branch examined here does not establish that slot's geometry. RSStats14 executed for request 1 in E011A, but its state, initialization and output policy remain separate. Neither path is marked closed. BFStats25, first neutral 3A and request-tagged LSC/GTM also remain open under E008p. VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement is still required before any native rear runtime.

No OEM code, raw debugger log, pixels or proprietary calibration are stored in Git. Original decompilation remains private on SP11. Native rear ISP runtime stays denied.
