# E003h Linux VFE1 Epoch0 CDM batch contract — static only

Date: 2026-08-29

## Purpose

`0024-x1e-epoch0-cdm-batch-contract-unreachable.patch` records the newly closed same-machine Windows steady-state Epoch0 RT-CDM topology without adding a command materializer, FIFO submission path or camera runtime.

It also corrects the retained 0023 data object so the repository no longer claims that `+0x008c/+0x3b70/+0x3d78..+0x3d84` are absent from post-start software programming. They are present in queued per-frame CDM lists; **direct MMIO rewrite remains unauthorized**.

## What 0024 records

The contract is data-only and records:

- five BLs per steady batch;
- BL length layout `{ 4, variant-main, 4, 0x10, 0x14 }`;
- `CHANGE_BASE 0x0000f000` for the main VFE1 list;
- `CHANGE_BASE 0x00057000` for the companion list;
- five main-list variants and their exact command/write/DMI/dynamic-register counts;
- 175 observed steady-state batches;
- queue encoded length = byte count minus one;
- main DMI address words are per-batch state;
- main register values include per-frame state;
- observed GEN_IRQ userdata tracks the batch tag;
- DMI payload bytes are **not yet closed**;
- direct-MMIO rewrite is false;
- FIFO0 submission authorization is false.

It embeds no captured Windows IOVA and no raw Windows command/payload byte array.

## Build/static proof

- patch SHA-256: `4b234a789b25bb1f37d703d2cbfdf8824c0443466523b3d4484e06457689f095`;
- oracle SHA-256: `3bcf4efe34c891dcc6bc78c3cefc94d916ffd71e27dab81e75493f9ed320dce4`;
- inspector SHA-256: `193eddc9a3dc4fb95dcdc02119d641724f0721450935b8d8093c9da319538afb`;
- inspection JSON SHA-256: `2f7bab800b36d9fc1529b4f08552b069c0d8bd6163025306d553ba62c0a8f90a`;
- candidate `camss.c` SHA-256: `fd1baf78bcba6f3cf926f66ea7fcb8b212e0659048a9187ed67011a5066c20c5`;
- `camss.o` SHA-256: `6e218d223ffe62ee6b3592efbec06086932bbdf9cf7795146da56447f222357d`;
- `qcom-camss.ko` SHA-256: `1f88683b72263db8a425d2ef54627c5e9ce7db7e4c6f66e71463fa01c9fdd9ad`;
- build log SHA-256: `59bbe45ed0a88ba231e11a50a3cb6705e1a27c804f26006894b0090ea0ade00c`;
- Golden vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- forward reconstruction: PASS;
- reverse reconstruction: PASS;
- compiler diagnostics: none;
- strict checkpatch: zero code/style checks; only non-mail-patch metadata warnings/errors;
- object/module retain both the corrected post-start contract and the new Epoch0 batch contract as read-only symbols;
- no relocation references the new contract;
- VFE1 PIX still fails with `-EOPNOTSUPP` before stream lock/IRQ/output setup.

CAMSS was not loaded. No `/dev/video*` or `/dev/media*` nodes were created.

## Next gate

Do not build a steady-state Linux RT-CDM materializer yet. First recover, on same-machine Windows:

1. exact DMI payload source CPU aliases/bytes for each steady main-BL variant;
2. the upstream rule selecting the five main-BL variants;
3. the producer/source of the GEN_IRQ batch tag if Linux cannot use its own request sequence directly.

Only then can a new unreachable materializer normalize a representative template per variant and repatch Linux-owned DMI IOVAs/per-frame values without freezing Windows addresses.

No Linux FIFO0 submit, VFE1 PIX/CSID1/MIPI enable, IMX681 transmission or frame is authorized.
