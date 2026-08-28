# E003h same-machine Windows RT-CDM1 stop/power oracle

Exact-binary + existing same-machine live-oracle checkpoint. No Linux RT-CDM MMIO write, IRQ arm, FIFO submission, sensor transmission, or frame occurred.

## Exact sources

- same-machine installed `qccamisp8380.sys`
  - bytes: `376560`
  - SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- prior same-machine HW-CDM live log `windows-ife-cdm/raw/E003H_HWCDM_ORACLE_20260828.log`
  - bytes: `27014`
  - SHA-256: `458b05c41718c7d01d0efb2921d1f6e2e4323e94e24447e379499544ca21cc1a`
- extractor: `extract_rtcdm_stop_power.py`
  - SHA-256: `3bf8189e2657fead2f7b1ee128e56f368d457e64618ebb1c732770c82d69f805`
- derived JSON: `windows-rtcdm1-stop-power-oracle.json`
  - SHA-256: `75711e2cf1bc1697db11e7415f23f71de1e12706d86d5fa55666bfd4ddfc39b8`

The extractor is fail-closed to both exact source hashes/sizes, stream-stop instruction RVAs, manager-delete dispatch, CDM vtable/close target, power-off paths, refcounted platform callback, and the prior live post-teardown sentinel.

## Stream-level DEVICE_STOP is not power collapse

The exact ISP-manager `0x805` path remains:

1. CSID stop;
2. IFE stop;
3. CDM stop.

Inside the RT-CDM `0x805` command handler, the exact direct mapped-MMIO store census contains only:

- `IRQ0_MASK +0x30 = 0` at RVA `0x28550`.

There is no proven `CORE_EN=0` write and no reset write in this stop block. Linux must not invent either one.

## Later manager/session delete is a separate lifecycle phase

Camera control `0x80e` dispatches to the routine mechanically tied to the diagnostic `DAL_ife_mgr_delete is failed with result 0x%x` at RVA `0x196f8`.

That manager-delete path performs the resource teardown after stream stop. Its relevant order is:

1. release per-block CDM associations;
2. close the CDM software object;
3. clear the manager CDM slot;
4. issue explicit CSID `POWER_OFF`;
5. close the CSID object;
6. issue explicit IFE `POWER_OFF`;
7. close the IFE object.

The CDM wrapper vtable is constructed with close method `0x140028a90` at method slot `+8`. The manager-delete path invokes that slot before entering the CSID/IFE power-off loops.

## CDM close contains no hidden RT-CDM shutdown write

The exact close routine `0x140028a90` decrements the CDM object reference count and, on final close, releases synchronization/parser/bookkeeping resources through cleanup `0x140028b80`.

A fail-closed scan over `0x28a90..0x28d10` finds **no access at all** to the CDM object's RT-CDM MMIO field `+0x48`. Therefore neither close nor cleanup hides a `CORE_EN=0`, reset, FE/FIFO configuration, or other RT-CDM register write.

This preserves the stream-stop result: the last mechanically proven RT-CDM register action during `0x805` is IRQ-mask zero.

## CSID and IFE POWER_OFF converge on reference-counted platform power collapse

The manager-delete CSID path issues command `3` (`IFE_CMD_ID_POWER_OFF` by the exact diagnostic) and the CSID implementation calls platform helper `0x140012fd0` with state `2`. Its success diagnostic is `CSID%d: CSID powered off and clocks disabled successfully`.

The IFE path likewise issues command `3`; its implementation resolves the IFE component and reaches the same helper `0x140012fd0` with state `2`. Its success diagnostic is `IFE%d: IFE powered off and clocks disabled successfully`.

The shared helper is reference-counted:

- atomically decrement the component use count;
- if the count remains nonzero, return without platform collapse;
- if it reaches zero, invoke the platform power-control callback at RVA `0x13080`.

Therefore the eventual hardware-off state belongs to the platform/component power-ownership layer, not an unobserved RT-CDM shutdown register sequence.

## Correct scope of the existing 0x80000000 live observation

The previously archived HW-CDM oracle performed the POST dump after the normal WinRT holder had completed `StopAsync` **and dispose/session teardown**. It showed the first `0x100` bytes of both RT-CDM mappings uniformly as `0x80000000`.

That observation is valid, but its timing scope is now tightened: it is **post StopAsync/dispose/session teardown**, not a sample taken exactly at the `0x805` DEVICE_STOP boundary. The sentinel is consistent with the later reference-counted platform power-collapse phase proven above.

The exact component transition that first changes RT_CDM1 to the sentinel has not yet been sampled dynamically. Do not claim it is specifically CSID power-off or IFE power-off without that timing oracle.

## Linux consequence

Parity must model two distinct layers:

- **stream stop:** preserve Windows `CSID -> IFE -> CDM`, with CDM IRQ-mask zero; do not add invented `CORE_EN=0` or reset writes;
- **final resource/runtime-power teardown:** release software/resource ownership, then collapse the relevant platform/power domain only through a proven equivalent refcount/ownership path.

The optional CGC write remains not-taken. `FE_CFG +0x20` and `FIFO0_CFG +0x5c` remain unwritten by Linux pending positive origin/timing proof.

## Remaining blockers before Linux RT-CDM MMIO

1. positive same-machine origin/timing of `FE_CFG +0x20 = 0x07ff000f`;
2. positive same-machine origin/timing of `FIFO0_CFG +0x5c = 0x01000000`;
3. if needed for exact Linux runtime-PM ordering, dynamically identify which post-delete component/power transition first produces the RT-CDM `0x80000000` sentinel.

Static `0014` remains the behavioral boundary.
