# E003h Windows VFE1 GEN_IRQ request tag

Date: 2026-08-29

A focused same-machine Windows KD pass closes the steady BL4 `GEN_IRQ` userdata source for the accepted front stream.

Raw log: `windows-vfe1-epoch0-dmi-payloads/E003H_VFE1_GENIRQ_REQUEST_CORRELATE_20260829.log`, 26,760 bytes, SHA-256 `7a182c14f2f797fef4143177e2c9e17dae885766a6c2a4781564a3f5250a974c`.

The trace contains 246 GEN_IRQ tags `1..0xf6` and 245 selector-2 Epoch0 batch identities `requestId=2..0xf6`, all with `subRequest=0`. The accepted post-start oracle already proves two complete batches are primed before the first completion/Epoch0 consume, explaining the unmatched initial tags 1 and 2. Thereafter every `TAG N` immediately precedes `REQ id=N` through `0xf6` with no mismatch.

`extract_vfe1_genirq_request_tag.py` hash-pins the exact installed `qccamisp8380.sys`, verifies the selector-2 request/subrequest handoff in the exact ARM64 binary, and fails closed on any event-sequence drift. The derived oracle therefore sets the front steady-state rule to:

`GEN_IRQ userdata = low32(requestId)`

This is a request tag, not an independent free-running CDM counter. Captured numeric tag values are evidence only; Linux must derive the tag from its own queued request identity. The nonzero-subrequest case is not observed by this front stream and is not invented.

No Linux RT-CDM submit path is enabled by this oracle.
