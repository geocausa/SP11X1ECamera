# E011T — rear BF request-1 ROI boundary

Parent Git: `271e4c0a` (E011S). Evidence class: pinned OEM static analysis plus bounded OEM Windows user-mode live trace. No native rear ISP runtime.

## Correction to E011S

E011S described E008r's packet-0 filter/coring, numeric IIR shifts, 25-ROI seed and phase validity as open. E008s already source-closed these from the pinned DeviceMFT and selected rear tuning; E008t composed the phase model, and E008u/E009e checked 300/300 packet-0 payload matches and all four startup ROI payloads. The packet-0 hardcode shifts are -3/0, and the normal AF/BAF shifts are 3/3. Do not redo E008s. The remaining question is the live request-owned normal AF/BF publication and its ordering relative to IFENode's early zero-ROI hardcode fallback.

## Static refinement

Pinned `QcDeviceMFT8380.dll` SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

`CAFStatsProcessor::Initialize` RVA 0x827940 sends outer SetParam 0x16, then outer 0x15 with a 0xA0-byte AF/HAF settings snapshot at data RVA 0x176B640, via helper 0x82D450 and `SetSingleParamToAlgorithm` 0x82D820. The AF core outer SetParam dispatcher RVA 0x616450 has its ID 0x15 arm at RVA 0x619910. That arm stores the input settings pointer at AF core object +0x1A4D8 and calls RVA 0x622020 (`af_haf_set_setting_info`), which forwards the settings to two HAF logic callbacks. This establishes settings handoff, **not** a byte-to-BF filter/ROI field map. A distinct nested ID 0x15 occurs in the outer dispatcher ID 0x0A arm; keep the namespaces separate.

`IFENode::Get3AFrameConfig` RVA 0x741570 checks the published BF ROI count at RVA 0x741C7C (input BF configuration +0x1C8C). Zero count branches at 0x741C80 to RVA 0x741D08, with the early-request hardcoded ROI helper call at 0x741D38 to RVA 0x7637D8, which invokes semantic helper 0x7635A8. Nonzero count takes the normal configuration copy at 0x741C94. This is the exact consumer branch for the live probe.

## Fresh E011T-0838B live observation

The earlier E011T-0732A staging identity was consumed at pre-enumeration by a script token substitution error; it opened no camera. A corrected fresh atomic identity E011T-0838B was used for this trace. SP11 Windows and SP7 were online. A fresh SP7 KDNET PTY `job_cuUVKS5-9B69o2cV0s5Ohr4K` initially connected but its later break-in retried without a prompt; it was stopped. Local ARM64 CDB attached to the SP11 FrameServer process instead. Private debugger transcript and holder script remain only on SP11 Windows.

Under the single rear Color VideoRecord NV12 3840x2160 holder, first observed BFStats25 `CheckDependenceChange` RVA 0xA1D340 entered with request scalar 1. Subsequently `CAFStatsProcessor::ExecuteProcessRequest` RVA 0x8288C0 entered with request ID 1 in its request data. Then `IFENode::Get3AFrameConfig` reached RVA 0x741C7C with request ID 1 and the published BF ROI count **25** at input +0x1C8C. At this observed consumer pass, branch 0x741C80 therefore took the normal, nonzero BF configuration path; the zero-count hardcoded fallback was not selected at that point. This does not prove that no earlier or separate packet-0 hardcode path ran, nor does it prove which producer populated all 25 ROIs or the values/validity of the 25 ROI records. The adjacent request output field checked before copy was zero. The private pointer and raw memory bytes are omitted.

Breakpoints were cleared before continuing. `StartAsync=Success`, 618 valid 4K handles were acquired, and `Stop` passed. CDB detached cleanly. No camera module install/load or RT-CDM submission occurred.

## Next narrow gate

Statically identify the request-1 BF property descriptor and the exact CAF/BAF writer that populates the 25-ROI published record, then trap the writer and consumer in a **new** atomic Windows identity. Prove request ID, per-record validity and ordering. The outer 0x15 AF/HAF settings pointer handoff is a distinct path until a consumer field mapping proves more. Keep native rear ISP runtime denied until BF/AF request bridge, remaining neutral-3A and LSC/GTM semantic gates, and VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle gates close.
