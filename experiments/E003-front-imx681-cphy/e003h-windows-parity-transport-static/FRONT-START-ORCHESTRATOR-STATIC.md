# E003h front-start orchestration contract — static/unreachable

Date: 2026-08-29

## Result

The front host-side startup layers can now be ordered without guessing the VFE1 BUS placement. A bounded same-machine Windows KD capture pins the initial pre-`ISP_START_DONE` sequence as:

`IFE803 packet0 -> IFE803 packet1 -> VFE1 BUS static config -> BUS enable -> initial dynamic addresses -> IFE803 packet2 -> IFE803 packet3 -> ISP_START_DONE`.

Combined with the already-accepted Windows manager oracle, the host-side lifecycle contract is:

`RT-CDM open/init -> RT-CDM start -> IFE resource start -> packet0 -> packet1 -> VFE1 BUS prepare -> packet2 -> packet3 -> CSID1 IPP start -> ISP_START_DONE`.

MIPI/CSIPHY start and IMX681 `0x0100=1` remain outside this contract and occur only after `ISP_START_DONE`. The exact upstream arithmetic for the two `period_cfg +0x8c` values is also intentionally outside the kernel transport contract; `0021` requires the two opaque values explicitly and maps them as packet0=value0, packets1/2/3=value1.

## Cross-order oracle

Raw capture:

- `windows-vfe1-dynamic-startup-fields/E003H_VFE1_BUS_CDM_CROSSORDER_20260829.log`
- bytes: `47032`
- SHA-256: `c32acebd61e0b2364450035c2b9e383a86e0ad355387760c149fb0e113342963`

Fail-closed extractor:

- `extract_vfe1_bus_cdm_crossorder.py`
- SHA-256: `e0cd5d690b60b8a9a18dc7a413a4bf0956b44ce25dc6d8e176218e80939913ad`

Derived oracle:

- `vfe1-bus-cdm-crossorder-oracle.json`
- SHA-256: `b495cc833c45e97b1467749bf094bb3035c5e6070bd0ea13d26a99ceec6acce6`

The extractor additionally hash-pins the accepted BUS-order, RT-CDM manager-order and sensor-lifecycle oracles. No post-start flood data is used to derive the startup contract; only the exact event prefix ending at the first `ISP_START_DONE` is accepted.

## Linux `0022`

`0022-x1e-front-start-orchestrator-unreachable.patch` is intentionally an **orchestration contract/validator**, not an execution function.

It adds to `camss.c`:

- the exact front tuple: X1E80100, CSIPHY2, one-trio C-PHY, CSID1 IPP, RAW10 3840x2640, IFE1/VFE1;
- the `0021` period packet map `{ 0, 1, 1, 1 }`;
- two Linux-only preparation markers: PIX ownership and RT-CDM corpus materialization;
- the exact ten-stage host startup ordering listed above;
- explicit `hardware_execution_authorized = false`;
- explicit `mipi_sensor_start_included = false`;
- a private validation helper which can call only the already-fail-closed RT-CDM corpus input validator.

The Linux preparation-marker order is an internal allocation/materialization choice only. It is **not** claimed as Windows hardware ordering and performs no MMIO.

The `IFE_RESOURCE_START` marker is likewise a lifecycle identity from the exact Windows manager order, not a newly invented Linux register sequence. No Linux hardware implementation is attached to that marker in `0022`.

## Binary/runtime isolation

`inspect_front_start_orchestrator.py` proves:

- the source stage order matches the cross-order oracle;
- the two-value period mapping remains exact;
- `0022` changes only `drivers/media/platform/qcom/camss/camss.c`;
- the patch contains no RT-CDM write helper call, VFE1 BUS helper call, CSID stream call, IRQ arm, FIFO submit, VFE stream call or MMIO write;
- the compiled private front-start recipe has exactly one ABS64 relocation to `camss_x1e_front_start_validate`;
- no compiled relocation references the private recipe itself;
- validator disassembly reaches `camss_rtcdm1_corpus_validate_input` but none of the hardware-writing helpers;
- the existing X1E VFE1 PIX `-EOPNOTSUPP` gate remains before stream lock/IRQ/output setup.

Inspection JSON: `front-start-orchestrator-inspection.json`.

## Build/static proof

- pre-0022 source SHA-256: `6b0b0fce4481b26620a3a1f4ae82157d87a309131da8b26747ce655b66cd4a0c`
- 0022 patch SHA-256: `1bf7d406e50bb3b57884d6f3a043d6c728327a8d8162f6ed9a678d2b8317e190`
- resulting source SHA-256: `2958909bae68cc6b459be39cf8abf8b4e8c19ba295feef4a8525504f3e1f6dff`
- `camss.o` SHA-256: `6dadb664c316fdb4aa440f4280e8a7348be1d3c0ec1674426e880cb2cd89d66b`
- `qcom-camss.ko` SHA-256: `d845b027f2c0ae70c47deb24d6cf08cf597cb02a1c4545b2a97a66508a8ac8c8`
- build log SHA-256: `8fab4200274b46f77105288316240075c47f7faab9f052126702030dfd837572`
- checkpatch output SHA-256: `5072302fa03c1771778d33dc4982627a932e138ca15c416dc9762ef2504de6eb`
- inspector SHA-256: `aa4348699216c7bdbb623a552f6e1b235249d115868a3f26f1874fd49358ba47`
- inspection JSON SHA-256: `dc4a86ae51cfc608074194d89874268d03cd52569591694b4e32c71dd3ec700a`
- Golden vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

Forward and reverse patch reconstruction are byte-exact. Checkpatch reports zero code/style checks; only mail-patch metadata (commit description / Signed-off-by) is absent. No CAMSS module was loaded and no `/dev/video*` or `/dev/media*` nodes were created.

## Boundary / next gate

The startup **ordering contract** is no longer the blocker. It remains deliberately non-executable.

The next static parity gate is post-`ISP_START_DONE` VFE1 ownership: distinguish software-owned per-frame updates (already proven BUS IOVAs) from hardware-live counters/state such as the changing `+0x3d78..+0x3d84` region, and prove which events require Linux action versus observation only. Until that is closed, do not turn `0022` into a caller, arm RT-CDM IRQ/FIFO0, start CSID1 IPP, enable VFE1 PIX, start MIPI/CSIPHY, transmit IMX681 or attempt a frame.
