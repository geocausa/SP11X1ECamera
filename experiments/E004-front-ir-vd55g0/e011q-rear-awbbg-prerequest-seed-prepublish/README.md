# E011Q — rear AWB_BG pre-request normal seed and AWB prepublish writer

Parent Git: `9d63d0c6254d31b6220604c695051b7eba48659a` (E011P).

Status: **SOURCE + LIVE PRE-REQUEST NORMAL SEED CLOSED; USECASE PREPUBLISH WRITER SOURCE-CLOSED; EXACT USECASE-TO-REQUEST PROPERTY BRIDGE OPEN.** Native rear ISP runtime remains denied.

E011P closed the request-side 3A AWB handoff: `IFENode::Get3AFrameConfig` consumes a normal 0x80-byte AWB configuration and copies it into request `+0xCF8`, where request-1 `AWBBGStats17` consumes it. E011Q moves upstream and establishes that the matching normal AWB_BG semantic configuration already exists before request 1.

A fresh Windows trace bracketed the successful AWB initialization helper from `CAWBStatsProcessor::Initialize` (containing RVA `0x82E140`). The call site at RVA `0x82ED9C` enters helper RVA `0x831510` and returns at `0x82EDA0`. At helper entry the AWB IO BG configuration was still zero/uninitialized. At the successful return it held:
- H/V grid: `64 x 48`
- ROI selection: `2`
- default sensor resolution used by this path: `4064 x 2286`
- direct ROI fields: zero, with selection 2 resolving the effective ROI to full default-sensor bounds `0,0,4064 x 2286`
- thresholds: four `0x3c3fe`
- adjacent mode word: `0x12`

Thus the normal AWB_BG semantics later observed by E011P are seeded during AWB initialization, before request-1 processing. A separate request-1 `CAWBStatsProcessor::ExecuteProcessRequest` trace (RVA `0x82EF50`) entered with the same normal configuration already present, and the first request-1 AWB algorithm call returned at RVA `0x82F5F8` without changing those primary values. Request 1 therefore does not originate this normal seed.

Pinned source of helper RVA `0x831510` also identifies the AWB prepublish write. The function writes a 0x80-byte payload through the node publication helper at RVA `0x5D6A18`; the exact call site is RVA `0x831E00`, with property ID `0x5000001D`. The same function identifies the operation as `CAWBIOUtil::PrePublishMetadata` / writing to the UsecasePool by AWB. The successful live initialization invocation brackets this helper from entry to its single return, while the static path contains the prepublish write before that return.

This closes the origin and timing of the pre-request normal AWB_BG seed and source-closes the 0x80-byte UsecasePool prepublish writer. It deliberately does **not** claim that Usecase property `0x5000001D` is itself the exact per-request 3A property later read by `IFENode::Get3AFrameConfig`. The remaining narrow boundary is the explicit UsecasePool-to-per-request 3A publication bridge.

The E011Q-0230E rear4K holder completed `StartAsync`/`StopAsync` successfully with **7,496 valid 4K handles**. The stale debugger transport was retired after the trace and a fresh KDNET session reconnected cleanly. No native rear ISP module was installed or loaded and no RT-CDM submit occurred.

Only source-safe scalar relationships and stable RVAs are committed. OEM bytes, debugger logs, process addresses, heap pointers and private payloads remain off Git.
