# SP11 front CSID1 common lifecycle — Windows oracle and Linux 0044

## Scope

This checkpoint addresses the failure boundary left by the consumed 0042/0043 Linux PIX diagnostics: clean IMX681/CSIPHY2 ingress reaches CSID1, but CSID1 does not produce the Windows CAMIF/RUP/Epoch progression needed by VFE1. It is static only. No Linux runtime is authorized by this record.

## Exact Windows common lifecycle

The accepted same-machine oracle `windows-csid1-common-reset-oracle.json` is fail-closed to the exact installed `qccamisp8380.sys` SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c` and the saved Ghidra decompilation identities. For the normal front CSID1 DEVICE_CONFIG path it proves:

`setInfo -> wrapper route 0x101 -> TOP_IRQ_MASK=1 -> RESET_CFG=0x11 -> RESET_CMD=2 (software only) -> reset completion -> full Gen2 builder`.

The reset callback itself writes only `+0x80`, `+0x0c`, `+0x10`. It does **not** prewrite `IRQ_CMD +0x14`. Windows writes `IRQ_CMD=1` later in the ISR acknowledgement path after status clear. Stream stop reuses the reset callback with argument `1`, giving hardware-only `RESET_CMD=1`.

Oracle SHA-256: `43a265f0cd63fa9e01406e8b5ff0b62c756dc2bc2f8c3a24df74a4f832b76996`.
Extractor SHA-256: `4ae58e9978852175ef06d0c10ffda480d370c93b88376a6f7f82ca527db113df`.

## Full-builder versus initial-packet ownership

The exact full Gen2 builder at RVA `0x1a870` runs immediately after the common reset during DEVICE_CONFIG, not as a later Linux-style prepare step. For the accepted front mode it owns RX CFG0/CFG1, RX and BUF_DONE masks, IPP drop/subsample/epoch/crop configuration, `CFG0=0x802b2000`, `CFG1=0x00007241`, `+0x324=0`, and the pre-start IPP mask `0x3c1c7004`.

The separately accepted CSID start oracle proves the CSID companion of each initial `0x803` packet is processed immediately after the matching IFE packet. Packet0 writes `+0x330=0`, IRQ subsample `1/0`, the 3840x2160 crop and format-measure values. Packets1..3 repeat only the crop. Later CSID `0x804` path-5 enable remains exactly `IPP_CTRL=1 -> IPP_IRQ_MASK=0x3cbc601c -> TOP_IRQ_MASK=1`.

The old Linux replay of live-final `+0x328/+0x32c=0xffff0000` has no proven software owner in either the exact full builder or captured companion packets. 0044 removes those writes rather than promoting a final readback to a software requirement.

## Linux 0044

`0044-x1e-csid1-common-lifecycle-windows-parity.patch` scopes the correction to the existing fail-closed X1E80100 front-mode0 predicate. Generic/non-front CSID680 reset remains unchanged. The bounded runner now relies on successful pipeline PM to complete CSID power/reset/full-config, submits each IFE startup packet followed by its exact CSID companion, retains the 0x804 enable order, and uses a private Windows-equivalent hardware-reset-only CSID stop. This removes the 0043 teardown-only V4L2 warning caused by calling public `s_stream(false)` after a private start that never set V4L2 stream bookkeeping.

Final identities:

- patch SHA-256 `a96339ab84094cfa0d103d73e6c04294dce5f211738fcbbe2bd370b9c5bb3340`;
- qcom-camss module SHA-256 `98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc`;
- module vermagic `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- `camss-csid-680.c` SHA-256 `59e07a1b8322c7279a051bc1255f8912452300aadbf9bf8086312aec4daca1d0`;
- `camss-csid.h` SHA-256 `e581e9a43a74a577aa535a7e33af4f5cd7e8c7af455d3c3fccd083dac2766f44`;
- `camss.c` SHA-256 `5eccf7c32a754ef97d19bafecb6a98cada393af57526d02835c9ff2176f90695`;
- build log SHA-256 `99ea98ba59b015b1111053654d8535b965723f88be827cb568ce2fa04fabbd8b`;
- strict checkpatch log SHA-256 `e6e2a7f1ef5193106f623889a6f3c6b7cb88bd15ec031f537e419af79f7a6e07`, with `0 errors, 0 warnings, 0 checks`;
- fail-closed inspector SHA-256 `cd8ef616050560c20bad94b39b74d335a73c9e5e6838c7992de5d54bc6d1bbe7`;
- inspection JSON SHA-256 `4d1dfc9d264e3b19d6e7e688b9c0d56f7db40a6f238b50856c26072fc9447ac7`.

The inspector proves patch reverse/forward byte identity, exact front reset/builder/companion/enable/stop order, no front pre-reset IRQ command, no front generic post-reset mask staging, retained ISR acknowledgement, and removal of public CSID `s_stream(false)` rollback. It also verifies that successful `v4l2_pipeline_pm_get()` means every enabled subdevice power callback completed or the graph was rolled back.

## Provenance and next gate

`provenance/front-parity.json` now carries both the Windows-reversed common-lifecycle fact and the Linux 0044 implementation equivalence. The bounded-first-PIX gate passes; production remains blocked only by `rtcdm.fe_fifo_ultimate_origin` and `iq.live_provider_algorithms`.

**No runtime is authorized.** The next mechanical step is to build a distinct 0044 one-shot package, inspect it against Golden and all pinned module/DT/sensor/capsule/helper identities, and leave it unarmed. A later runtime requires a separate explicit authorization checkpoint.
