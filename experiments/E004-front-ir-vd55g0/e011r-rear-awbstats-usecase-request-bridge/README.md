# E011R — rear AWBStatsControl request bridge

Parent Git: `14133f6e820dac1b61ece91d4855f0383bcbb951` (E011Q).

Status: **SOURCE + LIVE EXACT REQUEST PROPERTY BRIDGE CLOSED; USECASE RELATIONSHIP IS A SHARED PRODUCER, NOT A DIRECT PROPERTY-TO-PROPERTY COPY.** Native rear ISP runtime remains denied.

E011Q proved that AWB initialization creates the normal rear BG statistics configuration before request 1 and that `CAWBIOUtil::PrePublishMetadata` materializes that state as a 0x80-byte Usecase property. E011R identifies the exact request property consumed by E011P and proves its request-1 producer path live.

The property-name table identifies:
- `0x5000001D` = `PropertyIDUsecaseAWBStatsControl`
- `0x3000000D` = `PropertyIDAWBStatsControl`

Pinned source shows the request output descriptor constant at data RVA `0x840E58` as `0x803000000D`: a 0x80-byte output for `PropertyIDAWBStatsControl`. CAWBIOUtil initialization associates that descriptor with the request output buffer at qword index `0x5FD` (byte offset `+0x2FE8`).

A fresh request-1 trace hit `CAWBStatsProcessor::ExecuteProcessRequest` RVA `0x82EF50`, with request ID 1. Its call site RVA `0x82FA60` entered helper RVA `0x846020`, whose pinned source contains `CAWBIOUtil::FillBGConfigurationData`. At helper entry:
- the internal CAWBIOUtil BG source at `+0xCB4` already carried the normal E011Q seed;
- the request output buffer passed as the third argument was still zero.

The internal source carried 64x48, ROI selection 2, default sensor resolution 4064x2286, four `0x3c3fe` thresholds and adjacent mode word `0x12`. On return at RVA `0x82FA64`, the previously-zero request output buffer contained:
- H/V grid `64 x 48`
- effective ROI `0,0,4064x2286`
- four `0x3c3fe` thresholds
- adjacent mode word `0x12`

This closes the request-1 normal producer for `PropertyIDAWBStatsControl`.

The downstream side was then trapped in the same request. `IFENode::Get3AFrameConfig` RVA `0x741570` builds the adjacent property IDs `0x3000000C..0x3000000F`; output-array index 3 is therefore `0x3000000D PropertyIDAWBStatsControl`. At the live source load RVA `0x741BA8`, request ID 1 carried a non-null index-3 metadata pointer whose 0x80-byte payload exactly matched the just-produced normal AWBStatsControl record. E011P's first store at RVA `0x741BC8` then copies that record into request `+0xCF8`.

The metadata pointer observed by IFENode is not the same allocation as CAWBIOUtil's qword-index `0x5FD` output buffer (byte offset `+0x2FE8`), consistent with publication through the metadata pool. The closure is therefore producer -> published request property -> Get3A consumer, not pointer aliasing.

The Usecase property from E011Q is related but is not a direct precursor copy: `PrePublishMetadata` constructs `PropertyIDUsecaseAWBStatsControl 0x5000001D` from the same CAWBIOUtil internal BG configuration at `+0xCB4`, while request processing independently constructs `PropertyIDAWBStatsControl 0x3000000D` from that same internal source. Later-request dependency code at `CAWBStatsProcessor::GetDependencies` RVA `0x830EE0` explicitly carries `0x3000000D` forward with one-request offset when that dependency mode is active.

The E011R-0732A rear4K holder completed cleanly: Start success, **446 valid 4K handles**, Stop success, and all trace breakpoints were cleared. No native rear ISP module was installed or loaded and no RT-CDM submit occurred.

Only stable RVAs, property IDs, offsets and scalar semantic relationships are committed. OEM bytes, debugger logs, process addresses and heap pointers remain private.