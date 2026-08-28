# E003h RT_CDM1 Windows static recipe — unreachable Linux candidate

Date: 2026-08-28

Same-machine Windows remains the behavioral oracle. Public Qualcomm RT-CDM v2.1 material is used only for register naming/layout; all values and sequencing encoded here are same-machine Windows observations already closed by the E003h oracles.

## What `0015` encodes

`0015-sp11-rtcdm1-windows-static-recipe.patch` builds on `0014` and adds a private, retained, **unreachable** RT_CDM1 recipe in `camss.c`:

- read-only preflight: `HW_VERSION=0x20010000`, `FE_CFG=0x07ff000f`, `FIFO0_CFG=0x01000000`;
- open/init: `IRQ0_MASK=1 -> RST_CMD=9 -> reset-done wait <=500 ms -> DMB SY -> CORE_CFG=0x11f`;
- start: `IRQ0_MASK=0x00070007 -> DMB SY -> CORE_EN=1`;
- FIFO0 commit: dynamic 32-bit base, Windows low-20 request field with observed high field `0x00100000`, then `BASE -> LEN -> STORE=1`, followed by bounded BL-done wait;
- stream stop: `IRQ0_MASK=0` only.

The reset wait is event/IRQ driven, matching the exact Windows KMD reset signal path. The ISR completion condition is narrowed so reset-done and BL-done complete the private wait; inline remains informational.

## Explicitly forbidden behavior

The candidate contains no write to `FE_CFG` or `FIFO0_CFG`. The two-cycle Windows oracle proves those values are restored before the front CDM object's first MMIO write after a powered-off interval, so Linux may only validate them. It also contains no `CGC_CFG=7` path and no invented `CORE_EN=0` shutdown.

There is no public arm, init, start, submit, or stop API for this recipe. The five helpers are retained only by a private `__used` data table. Binary relocation inspection proves the helpers have exactly the five table relocations and the compiled module has **no relocation/reference to the table itself**. Therefore no probe, media, stream, or teardown path can reach the recipe in `0015`.

## Build and compiled-code proof

- patch SHA-256: `32661bf7e6eae864d857cd96bcfccdf01e820fbfbc3a2c2d9bf5cfa8f5ad9514`;
- source SHA-256: `ee7d14e191c1c3803437ab26d82a7c9fb33d47665419ac8f0a0330b2f76f32be`;
- `camss.o` SHA-256: `167bcd1897a4bf688fe6a4e6a433d1580e36d3c8165ab746c87663528ce40a67`;
- `qcom-camss.ko` SHA-256: `0c2f3df7423310c3384b02f6465b5ecb4b91ce73391b1f7fc10adca7157440d9`;
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- build: PASS, zero compiler warning/error diagnostics;
- compiled `open_init`: stores `+0x30`, `+0x10`, emits `dmb sy`, then stores `+0x18`;
- compiled `start`: stores `+0x30=0x00070007`, emits `dmb sy`, then stores `+0x1c=1`;
- compiled FIFO0 commit: constructs the observed `0x00100000` high field and stores `+0x50 -> +0x54 -> +0x58`;
- inspector SHA-256: `07338c3751c4d0cc53a6cb813b4f3fb43af9f9af26c27e9e0d65b8f31e3ad72a`;
- inspector JSON SHA-256: `23f9f601f0e9b8880e447d17685585bbdc1e0058a8be60fcf330172e366aa346`;
- build log SHA-256: `2e11d7ee50ed0b13c6d6bc2b80a7c5e568efd751c0b1a83d9942456cff520efc`.

Forward and reverse patch dry-runs pass, and application to the saved pre-`0015` `camss.c` reconstructs the current source byte-for-byte. Checkpatch reports only missing mail-patch description/Signed-off-by metadata, with no code/style defect.

## Isolation / safety

`0015` modifies only `drivers/media/platform/qcom/camss/camss.c`. It does not modify Denali DT, CSIPHY, CSID, VFE, sensor code, or any rear-camera path. The Denali DTB remains the `0013`/`0014` image SHA-256 `bbe48a77c5bc23f1c155ddc87b9a5b2ed56497656f06cab1a2db8e6346f0304b`.

No module was loaded, no Linux RT-CDM IRQ was enabled, no RT-CDM MMIO recipe ran, no DMA command list was submitted, no sensor transmission occurred, and no frame was attempted.

## Next architecture gate

The RT_CDM1 execution mechanics are now statically representable without guessed FE/FIFO configuration. The next blocker is the actual VFE1 PIX/ISP output architecture: implement a fail-closed Windows-derived 3840x2160 IPP input -> 2560x1440 QC10C/TP10-UBWC FULL path, including only Windows-proven BUS/DS/statistics/IQ state, while preserving rear D-PHY/RDI behavior. `0015` remains unreachable until that complete path and its rollback/runtime gates are closed.
