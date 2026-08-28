# E003h same-machine Windows RT-CDM1 init/order oracle

Static oracle only. No Linux RT-CDM MMIO write, IRQ arm, FIFO submission, sensor transmission, or frame occurred while producing this checkpoint.

## Exact source

- installed same-machine Windows `qccamisp8380.sys`
- bytes: `376560`
- SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- PE image base: `0x140000000`
- fail-closed extractor: `extract_rtcdm_init_order.py`
- extractor SHA-256: `399a7a6ecd412d652fcce1bad469514c87a0e696ad7bf4e68a55c51f148e6629`
- derived JSON: `windows-rtcdm1-init-order-oracle.json`
- JSON SHA-256: `489f47f45465603260a06f8aa2083cc417fff816478be9b6c8f68233bb0be927`

The extractor rejects a binary hash/size mismatch, missing diagnostic strings, instruction/RVA drift, command-opcode drift, loss of expected mapped-base write classes, or appearance of a direct mapped-base `FE_CFG +0x20` / `FIFO0_CFG +0x5c` store inside its bounded CDM-driver sweep.

## Open / initialization order

Exact direct-write sequence in the installed Windows driver:

1. `IRQ0_MASK +0x30 = 0x00000001`
2. `RST_CMD +0x10 = 0x00000009`
3. wait for reset completion, bounded by the driver to 500 ms
4. `DMB SY`
5. `CORE_CFG +0x18 = 0x0000011f`

The diagnostic path is mechanically tied to `DAL_cdm_init`; this is not inferred from a public Qualcomm implementation.

## DEVICE_START order

The ISP manager's exact `0x804` path establishes the full order:

1. **CDM start**
2. **IFE start**
3. initial configuration packet command `0x803` to the active IFE/SFE/CSID resources
4. **CSID start**

The RT-CDM start command itself performs:

1. `IRQ0_MASK +0x30 = 0x00070007`
2. `DMB SY`
3. `CORE_EN +0x1c = 0x00000001`

This corrects the earlier abbreviated lifecycle statement that began at IFE. The accepted Windows ISP-internal start order is now **CDM -> IFE -> initial packets -> CSID**.

## Dynamic FIFO0 commit

The hardware-CDM commit routine writes, in order:

1. `FIFO0_BASE +0x50 = <dynamic request base>`
2. `FIFO0_LEN +0x54 = <dynamic encoded length/tag/arbitration>`
3. `FIFO0_STORE +0x58 = 1`

The base and length are request/command-buffer state. They must never be hard-coded from a Windows live capture.

## IRQ clear behavior

For each FIFO, Windows reads status, masks it with `0x00070007`, writes the resulting status to the corresponding CLEAR register, then writes `1` to CLEAR_CMD. The Linux `0014` status model remains disabled behind its unreachable `irq_armed` gate.

## DEVICE_STOP order

The ISP manager's exact `0x805` path is:

1. **CSID stop**
2. **IFE stop**
3. **CDM stop**

The RT-CDM stop command directly writes `IRQ0_MASK +0x30 = 0`. No direct `CORE_EN=0` write has been mechanically established on this path. Final hardware/power teardown semantics after the mask-zero operation therefore remain unresolved and must not be invented.

A separate diagnostic flush/reset path performs a pause-preserving `CORE_EN` read/modify/write followed by `RST_CMD=9`; its use by the accepted front runtime has not been established.

## FE_CFG / FIFO0_CFG ownership: bounded negative only

A deterministic mapped-base store sweep over the exact CDM-driver region follows RT-CDM base loads from context `+0x48` and records direct `STR/STUR` stores before the base register is clobbered. It finds the expected software-written offsets including reset, core, IRQ, FIFO commit, and clear registers, but finds **no direct mapped-base store** to:

- `FE_CFG +0x20`, whose same-machine live value was `0x07ff000f`;
- `FIFO0_CFG +0x5c`, whose same-machine live value was `0x01000000`.

This is deliberately only a bounded static negative. It does **not** prove those values are reset defaults or hardware-owned. Linux must not write either value until same-machine evidence establishes ownership and timing.

## Remaining blockers before Linux RT-CDM writes

- origin/ownership and timing of live `FE_CFG +0x20 = 0x07ff000f`;
- origin/ownership and timing of live `FIFO0_CFG +0x5c = 0x01000000`;
- whether the conditional `CGC_CFG +0x14 = 7` path applies to the accepted front RT_CDM1 instance;
- exact hardware/power semantics after CDM stop masks IRQ0 to zero.

Therefore `0014` remains the behavioral boundary: no RT-CDM MMIO init/arm/submit path is authorized yet.

## Golden return

After the bounded Windows one-shot, SP11 returned normally to the saved FullIO v19c Golden. Verified:

- kernel SHA-256 `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- initrd SHA-256 `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`
- DTB SHA-256 `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`
- `saved_entry=sp11-audio-fullio-v19c`
- empty `next_entry`
- canonical branch/origin divergence `0 0` at pre-oracle HEAD `2bc013ec543fe231c1dfc7564e62a52824303d85`.
