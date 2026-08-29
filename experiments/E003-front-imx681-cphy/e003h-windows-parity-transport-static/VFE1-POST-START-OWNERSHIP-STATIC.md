# E003h VFE1 post-start ownership — static only

Date: 2026-08-29

## Result

Post-`ISP_START_DONE` ownership is now separated into software-owned scheduling/actions versus live hardware state without making any Linux front runtime reachable.

The accepted same-machine Windows log is `windows-vfe1-post-start-ownership/E003H_VFE1_POSTSTART_OWNERSHIP_VALID_20260829.log`, 8,616 bytes, SHA-256 `81aa7b23e2434dd89ddea21868917e23a2ce3abc1220a19b53805324c37825b5`. The deterministic extractor is SHA-256 `54bf175c539255fde78c9483cdd7511394cd4593845e5c43e932ff0ff5730f30`; its derived oracle is SHA-256 `d426c7cf4525f36c80623cab628061005c880abd5df02d17d8a76683fea4e66e`.

## Two-session timeline

Both local Windows windows have the same ownership pattern:

1. one complete nine-client VFE1 address bundle exists before `ISP_START_DONE`;
2. one more complete nine-client bundle is written after `ISP_START_DONE` and before the first completion cycle;
3. the first observed completion cycle is VIDEO `0x03`, AEC_BE_BHIST `0x0d`, TINTLESS_BG `0x0e`, AWB_BG `0x10`, RS `0x12`;
4. a further complete address bundle is written only after that first cycle.

Session 1 is sequences `0..32`: pre-start bundle `0..8`, `START_DONE=9`, second bundle `10..18`, first completion cycle `19..23`, refill `24..32`. Session 2 is sequences `42..74`: pre-start bundle `42..50`, `START_DONE=51`, second bundle `52..60`, first completion cycle `61..65`, refill `66..74`.

This is an observed initial prime depth of two complete address bundles, not a claim about an undocumented Windows allocator maximum. It fits the already-retained Linux two-slot ownership model: a second slot can be primed while the oldest slot is still in flight; after all five logical completion groups retire the oldest slot, that reusable slot can be replenished.

The five completion IDs are an observed sequence only. The exact Windows completion helper already proves independent FIFO ownership per group, so Linux must not require one fixed cross-group interrupt order.

## Exact Windows call graph

The exact installed `qccamisp8380.sys` remains SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`.

Static ARM64 anchors close the software scheduler:

- IFE ISR diagnostic `IFE%d IFE Epoch0 Irq occured.` is at RVA `0x37a60`;
- the ISR invokes Epoch0 handler RVA `0x25268` at call site `0x1f410`;
- completion event dispatch begins later at RVA `0x1f438`, so Epoch0 processing precedes completion dispatch in that ISR path;
- Epoch0 calls resource-update wrapper RVA `0x28380` at `0x25a38`;
- X1E registers the real BUS address writer RVA `0x1dd20` in the IFE callback slot used by that wrapper;
- Epoch0 then calls RT-CDM dispatcher RVA `0x28480` at `0x25ec8` with selector `2`;
- selector 2 dequeues/programs the queued BL batch and reaches FIFO0 base/length/store writes at RT-CDM-relative `+0x50/+0x54/+0x58`;
- the same exact CDM dispatcher uses selector `1` to accumulate individual BL descriptors and selector `0` to queue the accumulated batch.

Therefore the Windows steady-state software order is represented as:

`IFE Epoch0 -> complete VFE1 BUS IOVA update -> queued RT-CDM BL consume/program -> completion dispatch/retirement`.

The debugger capture that attempted to print CDM op0/op2 directly was malformed after its first hit and is deliberately not canonical evidence. The accepted runtime timeline plus hash-pinned exact-driver call graph is sufficient for this ownership gate.

## Register ownership after startup

`0020/0021` already established the startup-template boundary. This gate does not reclassify those values:

- `period_cfg +0x008c` is startup command data; prior live samples read it back as zero;
- `+0x3b70` is exact startup-template data and remained stable only in the bounded live samples;
- `+0x3d78/+0x3d7c/+0x3d80/+0x3d84` are exact startup-template data but mutate live while Windows streams.

No post-start software rewrite of those six register identities is proven. In particular, the live mutation of `+0x3d78..+0x3d84` is hardware observation, not a Linux periodic-write recipe. The per-frame **BUS IOVA addresses** are the proven software-owned changing VFE state.

## Linux `0023`

`0023-x1e-front-post-start-ownership-unreachable.patch` adds one retained read-only data contract to `camss.c`. It records:

- post-start stage order: Epoch0, BUS update, RT-CDM batch consume, completion retirement;
- nine clients per complete address bundle;
- two observed initially primed bundles;
- five logical completion groups with no required cross-group order;
- slot reuse only after all groups retire;
- BUS IOVA update, RT-CDM batch consume and completion retirement as software-owned Windows behavior;
- `0x008c/0x3b70/0x3d78/0x3d7c/0x3d80/0x3d84` as no-post-start-rewrite identities;
- `0x3d78..0x3d84` as live-mutating observation-only registers;
- `hardware_execution_authorized=false`.

The patch is intentionally **data-only**. It adds no function, ops table, MMIO primitive, IRQ operation, DMA operation or hardware-helper call. Object/module inspection finds the contract only as read-only data and no relocation references it.

Patch SHA-256: `962c8f6792b1ceb1649d6928df325ee1ed884f292342b0633b98c826a52cd7be`.

Inspector SHA-256: `e6c19ce210caf4e65b2fb18dcbf5230c9ef42846063644f6228f8a2d7b4ce1ca`.

Inspection JSON SHA-256: `e7251c0bd0f047473891c7b4011ed760e1821bebf8b7fea2e2602a29b9875625`.

Built `qcom-camss.ko` SHA-256: `15754a8529b12b65cc37adfd9135e10de4b30418613204488c7722c37c1e2b6d`, exact Golden vermagic `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`.

Forward/reverse patch reconstruction passes. Compiler diagnostics are empty. Strict checkpatch reports zero code/style checks; only mail-patch commit-description/Signed-off-by metadata is absent. CAMSS was not loaded and no `/dev/video*` or `/dev/media*` node exists.

## Next gate

The remaining steady-state parity blocker is no longer ownership. Windows Epoch0 consumes an RT-CDM BL batch, while the existing `0019/0020/0021` corpus covers the four **startup** IFE `0x803` command streams only. The next same-machine Windows oracle must capture multiple post-start queued/consumed RT-CDM BL descriptors and their command bytes, then classify invariant versus per-frame/request-dependent content. Until that closes, do not connect `0022/0023` to runtime and do not arm RT-CDM, VFE1 PIX, CSID1 IPP, MIPI, IMX681 transmission or a front frame.
