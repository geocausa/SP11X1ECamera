# E003h IFE startup base wrapper — Windows root cause and Linux 0045

## Result

The Linux 0043/0044 CSID1 `BUF_DONE_IRQ_MASK +0x90 = 0x00000001` drift is explained by a missing RT-CDM register-base wrapper on the IFE startup main BLs, not by a missing late CSID mask write.

Exact qccamisp reversal proves `DAL_ife_process_iq_packet` (RVA `0x26838`) queues one special four-byte KMD BL through the IFE CDM handle before it enters the ordinary descriptor-BL loop. The captured startup main streams contain zero `CHANGE_BASE` commands, while same-machine Windows MMIO effects prove those streams execute relative to VFE1 (`0x0ac71000`).

The required wrapper bytes are independently pinned. The little-endian dword `0x0800f000` (`CHANGE_BASE 0x0000f000`) has SHA-256 `18608790dc8901f9d1f17ad4d0ed33032309e5344be7abfab71a78c918f571a6`, exactly equal to the independently captured same-machine Windows four-byte VFE1 CHANGE_BASE BL0 in the steady RT-CDM oracle.

## Why the Linux history changes at 0043

Startup packet3 contains a VFE-relative `+0x90 = 0x00000001` write. With no startup CHANGE_BASE wrapper, a prior companion `CHANGE_BASE 0x00057000` can leave RT-CDM targeting CSID space, so packet3's VFE `+0x90=1` aliases CSID1 `+0x90=1`.

- 0042 staged the Windows CSID masks later during CSID stream start, after startup2/3, so the later `0x0001ffff` write hid the earlier malformed packet3 write.
- 0043 moved Windows-style CSID prepare/masks before startup2/3, so the malformed packet3 write became visible as final `0x00000001`.
- 0044 retained that order and reproduced the same final `0x00000001`.

This prediction matches all three bounded Linux runs. No speculative late CSID repair write is required.

## Linux 0045

`0045-x1e-ife-startup-change-base-wrapper.patch` adds a dedicated 16-byte coherent startup-wrapper arena: four independent four-byte `0x0800f000` BLs, one per startup packet. The bounded runner now submits `wrapper -> unchanged startup main` for packets 0..3.

Unchanged by 0045:

- captured startup main bytes and DMI patching;
- selector-2 priming batch materialization;
- CSID implementation/header and CSID companion ordering;
- steady Epoch0 batch materialization;
- no late `BUF_DONE_IRQ_MASK` repair.

Static validation:

- strict checkpatch: 0 errors, 0 warnings, 0 checks;
- reverse/forward patch reconstruction: byte-identical;
- CAMSS source SHA-256: `2b7930869bfe2a263a4242393536188f3f97249d3d76806bf19b4f955da291b0`;
- Golden-ABI qcom-camss.ko SHA-256: `cfdd66c9d2c56533993f5f73831d77b3f5018c1d552183da634971378aa06923`;
- module vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- fail-closed Linux inspection SHA-256: `bacbb046f5442b0542393302df42e4cbb2f2e2ca544c716d1c43434b9f2d9937`;
- reproducible Windows wrapper oracle SHA-256: `93b793d4bb13bc9d0abc09b667502466681f1a3e81d39bc837700d50ada96d03`.

**Runtime is not authorized by this static record.** The next gate is a distinct 0045 one-shot package, installed unarmed with Golden preserved as saved default and empty `next_entry`.
