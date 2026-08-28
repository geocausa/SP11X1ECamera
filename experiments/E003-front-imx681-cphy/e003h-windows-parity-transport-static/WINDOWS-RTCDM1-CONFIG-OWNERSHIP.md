# E003h same-machine Windows RT-CDM1 configuration-ownership oracle

Static exact-binary oracle only. No Linux RT-CDM MMIO write, IRQ arm, FIFO submission, sensor transmission, or frame occurred.

## Exact source and deterministic artifacts

- same-machine installed `qccamisp8380.sys`
- bytes: `376560`
- SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- extractor: `extract_rtcdm_config_ownership.py`
- extractor SHA-256: `d25da738a827d81439d426b4de828300af0c6544d2e3d1d0dab78bb8a981b1e7`
- derived JSON: `windows-rtcdm1-config-ownership-oracle.json`
- JSON SHA-256: `4c01a85709d9442953cfd5692219c04b57db5683312f788082e18b5aa6677b7c`

The extractor is fail-closed to the exact binary hash/size, object-allocation and zeroing RVAs, RT-CDM resource mapping, resource-getter call census, CGC guard path, bulk-memory call census, mapped-base store classes, and separation of the command-parser aperture from the RT-CDM aperture.

## CDM object and RT-CDM mapping

Windows allocates the CDM object as exactly `0xa40` bytes and immediately zeroes the entire object:

- allocate size `0xa40`;
- `memset(object, 0, 0xa40)` at RVA `0x1839c`;
- RT-CDM resource lookup at RVA `0x18494`;
- returned RT-CDM MMIO VA stored at object `+0x48` at RVA `0x1849c`.

The exact executable has only one resource-getter call in this CDM-object initialization range. The later command-list parser performs its own resource lookup, but stores that target aperture at object `+0x838`, not RT-CDM object `+0x48`. It is therefore not an alias for RT-CDM configuration registers.

## CGC_CFG +0x14 = 7 is statically not taken

The conditional write is:

1. read object byte `+0xa38`;
2. if zero, skip;
3. otherwise write `7` to RT-CDM `CGC_CFG +0x14`.

Mechanical facts from the exact binary:

- the full `0xa40` object is zeroed before initialization;
- `+0xa38` has exactly one fixed-offset access in the executable: the guard `ldrb` at RVA `0x28f5c`;
- there is no direct store whose byte range overlaps `+0xa38` in the CDM object code;
- init/runtime bulk-memory operations after the initial full zero target other subobjects/bookkeeping, including runtime `+0x890`, not `+0xa38`;
- the known reset/wait/commit helpers do not reload or modify `+0xa38`.

Therefore the normal in-binary Windows lifecycle leaves the guard at zero and the `CGC_CFG +0x14=7` write is **not taken**. Linux must not emit this optional write for the accepted front path.

## FE_CFG +0x20 and FIFO0_CFG +0x5c

Same-machine live Windows values remain:

- `FE_CFG +0x20 = 0x07ff000f`;
- `FIFO0_CFG +0x5c = 0x01000000`.

The ownership oracle strengthens the earlier bounded negative substantially:

- RT-CDM MMIO is mapped once into object `+0x48`;
- the exact runtime mapped-base write census includes reset/core/CGC/IRQ/FIFO commit/clear classes but no `+0x20` or `+0x5c` write;
- no second in-binary RT-CDM mapping path was found;
- reset/wait helpers do not hide RT-CDM MMIO writes;
- the command-list parser uses a distinct aperture at object `+0x838`.

Thus **no in-binary CPU software write path was found** for either live register. This does not yet positively prove that either value is a reset default or hardware-owned. Their origin/timing remains blocked pending positive same-machine evidence or an equivalent proof.

## Remaining blockers before Linux RT-CDM MMIO

1. positive same-machine origin/timing of `FE_CFG +0x20 = 0x07ff000f`;
2. positive same-machine origin/timing of `FIFO0_CFG +0x5c = 0x01000000`;
3. exact hardware/power semantics after Windows CDM stop masks IRQ0 to zero.

The optional `CGC_CFG=7` path is no longer an active blocker and must not be imported into Linux. Static `0014` remains the behavioral boundary.
