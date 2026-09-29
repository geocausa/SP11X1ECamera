# E011P — rear AWB_BG request-1 normal consumer and 3A handoff

Parent Git: `5c2a71d5d0406a4457398a5f0c32ba8d07862959` (E011O).

Status: **SOURCE + LIVE REQUEST-1 NORMAL CONSUMER CLOSED.** Native rear ISP runtime remains denied.

E011O closed the request-owned AWB_BG same-slot cold-to-normal bulk replacement at request `+0xCF8`, but left two points open: the immediate second request-1 AWBBG consumer after replacement and the direct semantic handoff from the 3A-sourced normal AWB config into that request slot.

Fresh same-Windows tracing closes both of those boundaries.

Pinned source identifies `CamX::IFENode::Get3AFrameConfig` at RVA `0x741570` as the request-side 3A handoff. The AWB branch consumes the fourth returned 3A property pointer, logs it as `Original 3A-AWB ROI Config from 3A`, and copies the complete AWB configuration record into the request-owned AWB_BG slot at `+0xCF8`. The first SIMD store of that live copy is RVA `0x741BC8`.

The live source record and resulting request slot carried:
- H/V grid: `64 x 48`
- ROI: `0,0,4064 x 2286`
- thresholds: four `0x3c3fe`
- adjacent mode word: `0x12`

A later process-scoped execute breakpoint on `CamX::AWBBGStats17::Execute` RVA `0x9FE780` hit request ID 1. At function entry, the request `+0xCF8` record already held the normal values above while the AWBBG module's cached internal record at object `+0x60` still held the cold state:
- H/V grid: `64 x 48`
- ROI: `0,0,3658 x 2058`
- thresholds: four `0x3ffff`

The request-1 path then called `AWBBGStats17::CheckDependenceChange` RVA `0x9FDF60`. At entry to `AWBBGStats17::AdjustROIParams` RVA `0x9FE120`, the internal object record had changed to the same normal `64x48 / 4064x2286 / 0x3c3fe` values from the request slot. After AdjustROI returned, those primary semantic values remained unchanged; only derived region dimensions had been materialized (`62 x 46` in the module's derived fields).

This closes the request-1 normal consumer handoff and proves that E011O's same-slot normal replacement is consumed by AWBBGStats17 on request 1. It also identifies the immediate request-side source as the 3A AWB property returned into Get3AFrameConfig. It does **not** yet prove the earlier AWB policy/algorithm writer that created that upstream 3A property payload.

The supporting rear4K holder completed StartAsync/StopAsync successfully with 1,403 valid 4K handles. KD breakpoints were cleared and execution resumed. No native rear ISP module was installed or loaded and no RT-CDM submit occurred.

Only source-safe scalar relationships and stable RVAs are committed. OEM bytes, debugger logs, process addresses and private payloads remain off Git.
