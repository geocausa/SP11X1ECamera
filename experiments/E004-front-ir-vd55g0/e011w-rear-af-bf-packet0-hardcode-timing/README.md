# E011W — rear AF/BF pre-request hardcode timing

Parent Git: `a0b67437de83cb03e94096525e862d7fc31ab28d` (E011V). Evidence class: pinned OEM static analysis plus bounded OEM Windows user-mode live trace. No native rear ISP runtime.

## Question

E011V closed the request-1 `PropertyIDAFStatsControl` full-payload producer-to-consumer bridge. The one AF/BF bootstrap question left open was whether the distinct hardcoded BF configuration path occurs before normal request-owned AF/BF data, and specifically whether `IFENode::Get3AFrameConfig` takes its zero-ROI fallback.

E008s remains the source authority for the hardcoded BF semantics themselves: packet/bootstrap filter and coring settings, centered 5x5 / 25-ROI construction, and -3/0 IIR shifts. This stage does not redo those fields.

## Static path separation

Pinned `QcDeviceMFT8380.dll` SHA-256 remains `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

The shared hardcoded ROI helper is RVA `0x7637D8`; its semantic helper is RVA `0x7635A8`, called at RVA `0x763818`.

There are two code callsites to the ROI helper:

- RVA `0x736438`, inside `IFENode::HardcodeSettings` (function entry RVA `0x735940`). The call is selected when the relevant hardcode mask contains bit `0x4` or the function's force/default argument is 1.
- RVA `0x741D38`, inside `IFENode::Get3AFrameConfig` after the BF ROI-count check at RVA `0x741C7C` takes its zero-count branch through RVA `0x741D08`.

This separation matters: observing the shared helper does not by itself prove that the request-time zero-ROI fallback ran.

## Fresh E011W-0942A live trace

A fresh atomic Windows identity `E011W-0942A` was used. Breakpoints were armed after camera initialization and before stream start at the two hardcode helpers, the `Get3AFrameConfig` zero-count branch, BFStats25 dependence check, CAF request processing, and the IFENode BF count load.

The first live hardcode events were two calls to ROI helper RVA `0x7637D8`, each returning to RVA `0x73643C`, followed by the semantic helper returning to RVA `0x76381C`. Therefore both observed pre-request hardcode invocations came from `IFENode::HardcodeSettings` callsite RVA `0x736438`.

The request-time zero-ROI fallback branch at RVA `0x741D08` recorded **zero hits**.

After the two pre-request hardcode-helper pairs, normal BF/AF request processing began. `IFENode::Get3AFrameConfig` was observed 2,237 consecutive times for request IDs 1 through 2237. Every observation at BF-count load RVA `0x741C7C` had adjacent BF words `0,25`; the mechanically checked count-word mismatch total was zero. Thus every observed request took the nonzero, normal AF/BF configuration path, including request 1.

The bounded rear Color VideoRecord NV12 3840x2160 stream reported `StartAsync=Success`, acquired 2,366 valid 4K handles, and `Stop` passed. CDB was detached after clearing breakpoints and the fresh KDNET session was stopped. Raw CDB/KD/holder transcripts and private addresses remain archived only under the private E011W session directory and are not committed.

## Closure

For this OEM rear stream, the distinct live hardcode occurrence before request 1 is the `IFENode::HardcodeSettings` bootstrap path. The separate `Get3AFrameConfig` zero-ROI fallback was not used in request 1 or any of the 2,237 observed requests. Combined with E008s and E011T/U/V, the remaining AF/BF bootstrap timing question is closed without changing the already source-closed hardcode field semantics.

Next semantic gates are neutral-3A and then LSC/GTM. The separate VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle gate remains open. Native rear ISP runtime remains denied: do not install/load the native camera module or submit RT-CDM until those gates close.
