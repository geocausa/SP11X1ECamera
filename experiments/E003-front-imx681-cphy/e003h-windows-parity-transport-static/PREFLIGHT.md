# E003h preflight — Windows-parity transport architecture, static only

Date: 2026-08-29

## Purpose

Close the remaining host/receiver/sensor lifecycle gaps under the project rule that the exact same-machine Windows stack is the behavioral oracle. E003h is not an RDI bring-up gate and does not authorize a frame.

## Windows facts now mechanically established

- physical path: `IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1`;
- sensor mode: 3840x2640 RAW10 VC0, one-trio C-PHY;
- CSID1 RX: `RX_CFG0=0x11300000`, `RX_CFG1=0x00000001`;
- CSID1 IPP: enabled RAW10 VC0, crop/measure 3840x2160;
- VFE1 Windows ISP output: FULL Y 2560x1440, FULL C 2560x720, DS4 320x180, DS16 80x45 plus statistics clients;
- VFE0 is inactive for the front WinRT stream;
- sensor stream-on/off is exactly `0x0100=1` / `0x0100=0`, zero delay; group hold `0x0104` is separate;
- Windows ISP internal start order is CDM -> IFE -> initial IFE/SFE/CSID packets -> CSID;
- Windows ISP internal stop order is CSID -> IFE -> CDM/remaining core;
- native front IFE command execution uses hardware RT_CDM1 v2.1 at physical `0x0ac26000`, FIFO0;
- RT_CDM1 registers as interrupt class 3 / instance 1 with firmware GSI `319` (`0x13f`), which maps to Linux `GIC_SPI 287` (`0x11f`) on this SP11;
- two independent dynamic cycles prove ISP start completion before sensor `0x0100=1`, and ISP stop completion before sensor `0x0100=0`.

## Linux gaps

1. CSID680 did not propagate the parsed C-PHY type into RX_CFG0 and omitted Windows' reproducible bit-28 field. `0009-...patch` fixes only that proven RX mismatch and builds successfully. It is not deployed.
2. CSID680 Linux streaming supports RDI paths only; the Windows path is IPP.
3. VFE680 Linux output supports RDI only. Its generic PIX line mapping is explicitly invalid for PIX and would map line 3 through `RDI_WM(3)` to WM27/LTM_STATS. Enabling PIX as-is would be wrong.
4. Windows uses VFE1 FULL Y/C and real ISP scaling from 3840x2160 to 2560x1440, not a raw RDI write master.
5. Linux generic stop ordering VFE -> CSID does not match Windows. Static-only `0010-x1e-windows-stop-order.patch` changes X1E teardown to CSID -> VFE -> existing remaining upstream tail, while non-X1E traversal is unchanged. The patch reproducibly builds to qcom-camss SHA-256 `b7c9ed932e2dccca4eaf73d085d2c5c8e6104d7cb807bafd00804051a9e82591`; it is not deployed.
6. Lifecycle placement is fully resolved. Four MIPI-instrumented Windows cycles prove strict ISP -> MIPI -> sensor start ordering and an unordered sensor-off/MIPI-stop tail after ISP teardown. `0010`'s current CSIPHY -> sensor tail is an observed-valid serialization, not a claimed Windows requirement.
7. Static `0015-sp11-rtcdm1-windows-static-recipe.patch` now compiles the exact Windows-derived RT_CDM1 preflight/init/start/FIFO0/stop recipe behind an unreachable private ops table. FE_CFG/FIFO0_CFG remain read-only validation targets, the optional CGC path is absent, no `CORE_EN=0` shutdown is invented, and no runtime code references the recipe.
8. Static `0016-x1e-vfe1-pix-qc10c-static-contract.patch` closes only the VFE1 PIX memory/completion representation: IFE1-only RAW10 -> fixed 2560x1440 QC10C, FULL WM0+WM1, exact surface offsets and Windows VIDEO completion contract. VFE1 PIX stream-on remains rejected before hardware setup; IFE0/Lite/RDI behavior remains unchanged.
9. The dynamic BUS-address path is now exact: Windows RVA `0x1dd20` writes `IMAGE_ADDR +0x04` and FULL `META_ADDR +0x40` in the nine-client order, with the initial set after BUS enable/before ISP start completion and later sets per frame. Static `0017` accepts Linux DMA IOVAs only and retains `prepare/update/stop` behind an unreferenced private table. Captured Windows IOVAs/ring strides are forbidden and VFE1 PIX remains stream-blocked.
10. Completion ownership is now static and fail-closed. Five live cycles show VIDEO -> AEC_BE_BHIST -> TINTLESS_BG -> AWB_BG -> RS, while exact helper RVA `0x26460` proves independent per-group FIFOs; Linux `0018` therefore does not require cross-group order. It retains two-slot QC10C/aux ownership behind an unreferenced private table and leaves BUS/ISR/VFE ops/runtime untouched.
11. Static `0019-x1e-rtcdm-corpus-materializer-unreachable.patch` closes command/data materialization only: four normalized local command inputs + 16 exact payload inputs become Linux-owned 4 KiB command slots and a compact DMI arena, with 46 Linux DMI-address patches and 20 explicit dynamic-value patches. Captured blobs/Windows allocation geometry are not embedded, and no MMIO/FIFO/VFE/runtime path references the private materializer.
12. Follow-up `0020-x1e-rtcdm-startup-dynamic-ownership-unreachable.patch` narrows that conservative 20-value boundary: independent startup corpora plus fresh KMD pass-through prove 16 formerly live-volatile words are invariant startup-template data, while only four `period_cfg +0x8c` words are start-dependent caller inputs. Live `+0x3d78..+0x3d84` still mutate after startup, so their template values are not live-state assertions. `0020` remains retained-only and adds no MMIO/FIFO/VFE/runtime path.
13. Static `0021-x1e-rtcdm-period-cfg-two-value-contract-unreachable.patch` narrows the four packet-local `period_cfg` holes to two opaque upstream start inputs: packet 0 has one value and packets 1/2/3 share the second in every accepted Windows start. It embeds no captured values, keeps four patch sites, and remains retained-only with no MMIO/FIFO/VFE/runtime connection.
14. A new Windows cross-order oracle pins packet0/1 -> VFE1 BUS static config/enable/initial addresses -> packet2/3 before `ISP_START_DONE`. Static `0022` records the full host ordering only as a private validator/contract: exact front tuple, two-value period map, and lifecycle stage identities, with hardware execution explicitly false and MIPI/sensor start excluded. It adds no hardware-helper call and leaves VFE1 PIX fail-closed.
15. Post-start scheduling is closed without arming Linux. Two same-machine Windows windows prove one complete nine-client bundle before `ISP_START_DONE`, a second complete bundle after start but before the first completion cycle, and a refill after that cycle. Exact KMD call graph pins IFE Epoch0 -> BUS address update -> RT-CDM queued-BL consume/program before completion dispatch. Static `0023` records this only as unreferenced read-only data; its original no-post-start-rewrite interpretation is historical and explicitly superseded by item 16/`0024`.
16. The clean Epoch0 selector-2 batch oracle supersedes only 0023's no-rewrite interpretation, not its scheduler order. Exactly 175 steady batches use five BLs and five main-list variants (`0x958/0x868/0x83c/0x6b8/0x5a4`); every varying command dword is a DMI address or register value. `+0x008c/+0x3b70/+0x3d78..+0x3d84` are queued per-frame CDM writes, while a separate direct-MMIO rewrite remains forbidden. Static `0024` records the corrected ownership/topology only as retained data and explicitly leaves DMI payload bytes/FIFO submission unclosed.
17. Representative steady-state DMI payload bytes are now hash-closed for all five variants from local Windows source-ring/slot evidence; raw payload bytes remain untracked. Exact KMD disassembly proves the five BL sizes are upstream IQ-packet shapes, not a hidden KMD selector. Frame-varying IQ values and the exact GEN_IRQ tag source remain upstream inputs; runtime stays blocked.

18. GEN_IRQ tagging is now exact for the accepted front stream: 245 consumed requests prove BL4 userdata equals `low32(requestId)` with `subRequest=0`; the first two tags are the already-proven primed batches. A second `0x83c` payload sample confirms only `4308/1` and `4308/2` vary. The remaining steady-state producer is upstream IQ packet content, not KMD tagging/selection.
19. The exact Surface camera INF registers `QcDeviceMFT8380.dll` as DeviceMFT; its CamX Titan680 builders own all 24 changing steady register fields and all eight DMI register identities. LSC/Gamma/GTM/DSX/PDPC/WB/Demux dependency families are statically named, while proprietary algorithm reproduction remains explicitly out of scope. The next Linux step is an unreachable consumer/materializer only.
20. Static `0025-x1e-epoch0-module-input-materializer-unreachable.patch` closes that consumer side without making it reachable. One of the five normalized main shapes plus exact named-module value/payload masks is copied into Linux-owned 4 KiB command and 12 KiB DMI arenas; all DMI IOVAs are repatched to Linux DMA and BL4 userdata derives from `low32(request_id)` with `subrequest=0`. Real normalized Windows samples plus synthetic module outputs decode to the exact five Windows command/write/DMI counts. No Windows template/payload/IOVA is embedded, the private recipe has no caller, and FIFO0 remains unauthorized. The next gate is module-input provider/priming ownership, not execution.

21. Bounded native transport runtime is now proven separately from parity: one disposable front-only candidate captured sequence 0 as a complete 12,672,000-byte 3840x2640 `pRAA` RAW10 frame through CSIPHY2 -> CSID1 RDI0 -> VFE1 RDI0. Raw SHA-256 `8e892cfe...e000ac`; offline preview visibly resolves scene geometry. STREAMOFF returned IMX681/CAMSS suspended with camera clock counts and regulator use counts zero. RT-CDM FIFO0 and VFE1 PIX were not used.
22. Static `0030-x1e-pix-hardware-order-contract-unreachable.patch` fixes cross-file Linux power, host-start, steady-loop, stop and reverse-rollback ownership without a caller. It reuses V4L2 pipeline PM, VFE1 `vfe_get/put`, CSID1 IPP and CSIPHY2 subdev operations, and keeps generic VFE1 PIX `s_stream` blocked. Two selector-2 placement relations remain explicit blockers, so PIX activation is still unauthorized.
23. The startup/priming interleave is now exact: packet0 -> replay0 -> packet1 -> BUS config/enable/initial addresses -> replay1 -> packet2 -> packet3 -> CSID1; after ISP done, MIPI/sensor start precedes replay2/3. Static `0031` records this as a 16-stage retained order with all closure bits true but still no callable runner or runtime reference.
24. Post-sensor first-frame pacing is exact: Epoch0 #0 -> complete nine-client BUS retarget -> replay2/request2 -> VIDEO, with replay3 deferred until Epoch0 #1 after another BUS retarget. A bounded first-PIX proof must not pre-submit replay3 before the first VIDEO.
25. Static `0032` now represents each selector-2 replay as its complete Windows `4/5/5/5` BL batch, not a main-BL-only shortcut; companion BL bytes are exact and Linux-owned. Static `0033` compiles one callable first-frame runner but retains it with zero runtime references. It submits only prime0/1/2, never prime3 or a steady batch before first VIDEO, and keeps generic VFE1 PIX `s_stream` forbidden. Runtime remains unarmed pending a separate one-shot caller/preflight gate.
26. Static `0034` adds that one-shot gate but still no external trigger. It burns an atomic latch before validation, requires the pinned local capsule identity, exact VFE1/RT-CDM resources and front-only graph, and accepts only two distinct DEQUEUED non-streaming QC10C buffers with exact size/stride and safe 32-bit DMA ranges. The gate has zero runtime references; actual capsule/module/DT hash verification is explicitly left to a future host preflight package.
27. `0035` prepares that disposable trigger/package but does not arm it. The qcom-camss module parameter defaults false and is read-only after load; only explicit `e003h_pix_runtime_arm=1` creates the write-only one-shot sysfs trigger. The helper uses REQBUFS/QUERYBUF/mmap only—no QBUF/STREAMON. Front-only DT, capsule, sensor, candidate module and helper hashes are pinned; a Golden-host preflight passes and the installed candidate GRUB entry leaves next_entry empty.
25. Two-cycle Windows cross-order now proves replay0/1 precede CSID1 start and replay2/3 follow MIPI completion plus sensor-on. The only remaining start-order ambiguity is the mutual interleave of replay0/1 with the separately proven packet0/1 -> BUS -> packet2/3 prefix before CSID1 start. PIX remains unauthorized until that final relation is closed.

26. Static `0032` closes selector-2 priming batch granularity: replay0..3 are complete `4/5/5/5`-BL batches. Linux companion BLs are byte-proven against Windows; BL1 reuses the Linux-repatched priming main and every FIFO length is `byte_count - 1`. The retained recipe has no callable runner or runtime reference.

## Policy consequence

An RDI frame can be useful later as a diagnostic transport proof, but **must never be called Windows parity or accepted as the production endpoint**. E003h remains static until the IPP/VFE1 pixel pipeline and lifecycle can be represented without inventing behavior.

## Safety state

- Golden remains saved default and byte-exact.
- One disposable RDI diagnostic captured exactly one front frame; it is explicitly not Windows parity.
- Scene bytes remain local/untracked; only hashes/statistics/filtered logs are retained in Git.
- Sensor and CAMSS are runtime-suspended after STREAMOFF; mutable links are disabled.
- Relevant camera clock counts and regulator use counts returned to zero; no kernel fault occurred.
- RT-CDM FIFO0 and VFE1 PIX remain unused by this diagnostic.

28. The first authorized VFE1 PIX one-shot was consumed and returned `-ETIMEDOUT` before any IMX681 stream-on message. No frame was produced; teardown/Golden return were clean and there was no same-boot retry. Runtime is blocked again until RT-CDM stage diagnostics distinguish reset/open from FIFO0 BL completion.

29. Static `0036` adds read-only RT-CDM failure telemetry: reset/core/FIFO stage, FIFO sequence/base/length, raw IRQ context/status/userdata and last ISR snapshot, plus semantic packet/BL error labels. It adds zero MMIO writes and no new runtime trigger. A second PIX attempt is not authorized.

30. Exact Windows RT-CDM IRQ handler disassembly proves no IRQ_CONTEXT_STATUS read and masked `0x00070007` FIFO status clears. Static `0037` removes the Linux context-bit prerequisite and clears only known masked status; runtime remains blocked pending a freshly inspected diagnostic package and separate authorization.

31. The disposable front-only package is refreshed to the 0036+0037 CAMSS module and package/preflight inspections pass while unarmed. No second RUN is authorized by the refresh itself.

28. The second instrumented PIX authorization is consumed. Its root invocation was followed by an unclean reset (no shutdown journal; next Golden boot EXT4 orphan cleanup), no QC10C output and no persisted RT-CDM stage result. Golden is restored. No third runtime is authorized; persistent stage observation is the next static gate.

29. Static `0039` adds only an arm-gated read-only RT-CDM stage sysfs snapshot and fsync-backed watcher. It publishes pre-write reset/core/FIFO software markers, adds zero MMIO writes, preserves `RUN` semantics, passes forward/reverse reconstruction and Golden-vermagic build. Runtime remains unauthorized. Patch `b4349284fabdba7be35a0973894e51e1d872ae8838724f9f68fc863df32aef8a`, module `cabc1851006f86e83f4086226342c11702aed6b8734d2f5144e9f51fb8042ed3`.

30. Exact Windows RT-CDM handler disassembly closes four-FIFO acknowledgement: FIFO0..3 status are read/masked by `0x00070007`, masked FIFO0 gates dispatch, and all four masked statuses/CLEAR_CMDs are acknowledged. Static `0040` mirrors only that behavior; FIFO0 remains the sole completion source, runtime remains unauthorized.

31. Static `0041` replaces the stale Linux eight-entry CAMSS IOMMU list with the public X1E five-entry S1 HLOS implementation set including `0x18a0/0`. Same-machine qcsmmu independently proves `0x18a0/0` is in VFE/IFE HLOS CB16, but exact RT-CDM1 requester->SID is still unproven. `0041` is Linux implementation only (`parity_claim=false`); no runtime is authorized.

32. Same-machine Windows now closes the command requester: qciommuext's five-member VFE HLOS aggregate explicitly includes Camera CDM IFE, live IORT maps the distinct aggregate member to SID 0x18a0, qcsmmu leaves 0x18a0 singleton in CB16 while masking the four IFE/SFE RD/WR 0x800-family members, and qccamisp independently proves the front command engine is RT-CDM1. Linux 0041 includes that SID in the CAMSS translation domain. Bounded provenance is no longer blocked by command-DMA visibility; runtime still requires a new authorization checkpoint.

33. Post-provenance package v3 is built and installed unarmed: CAMSS `7d8c8953...`, front-only DT `019c062a...`, exact five-entry IOMMU set including Windows-proven requester `0x18a0`, persistent RT-CDM observer required, and bounded provenance green. Golden remains saved/default with empty next_entry. Runtime still needs a fresh one-shot authorization checkpoint.

34. Static `0044` closes the common CSID1 lifecycle that 0042/0043 omitted. Exact same-machine Windows proves wrapper route `0x101` precedes software-only reset (`TOP=1`, `RESET_CFG=0x11`, `RESET_CMD=2`), followed immediately by the full Gen2 builder; each later IFE startup packet is followed by its exact CSID companion, and 0x804 path enable remains `CTRL -> IPP mask -> TOP`. Linux removes unowned `+0x328/+0x32c` replay and uses the Windows hardware-reset-only private stop, eliminating the teardown-only V4L2 bookkeeping warning. Patch `a96339ab...3340`, module `98b3252e...3cbc`, strict checkpatch and fail-closed inspection pass. Runtime remains unauthorized; the next gate is a distinct unarmed one-shot package inspection.
35. The distinct 0044 common-lifecycle package is installed and package-inspected while unarmed: CAMSS `98b3252e...3cbc`, front-only DT `019c062a...f77f`, package inspection `be15d0f...9128`, stable bounded provenance `5b016ae7...e78b`. Golden remains saved/default, `next_entry` is empty, no camera modules are loaded and no `AUTHORIZATION.json` exists. A hardware run still requires a separate authorization checkpoint.
