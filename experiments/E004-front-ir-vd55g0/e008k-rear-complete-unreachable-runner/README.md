# E008k — complete rear two-slot unreachable runner

Status: **BUILD-ONLY PASS**.

## Goal

Compose the rear native ISP control plane end-to-end without creating any
runtime call site.

The runner consumes caller-owned, already DMA-mapped E007y command buffers and
composes the accepted contracts in their now source-locked order:

1. validate the exact rear media route and materialize all four E007y packets;
2. acquire the E005y shared CSID1/VFE1 owner as REAR;
3. allocate two complete E008d output sets and bind both E007z ledgers with
   E008j's zero-MMIO path;
4. power the existing media pipeline and seed the E008i rear observer;
5. start RT-CDM1;
6. submit packet0;
7. only then configure/preload BUS slot0 disabled, enable the live E008f WM
   set and rewrite/read back slot0;
8. submit packet1;
9. enable CSID1 IPP, then start CSIPHY1 and OV13858;
10. on first Epoch0 retarget all ten WMs to slot1, then submit packet2;
11. on second Epoch0 submit packet3;
12. consume E008i CSID BUF_DONE/ADDR_STATUS0 records until both E008h
    exact-consumed-IOVA ledgers are complete;
13. quiesce CSID1 once, stop VFE1 BUS/IRQ once, prove both ledgers retireable,
    stop/close RT-CDM1, stop CSIPHY1 then sensor, release both ledgers, drop
    pipeline PM and release the shared REAR owner.

E008j is essential here: E008h's older convenience allocator performs a
disabled BUS preload before return, whereas E008g proves packet0 precedes BUS
configuration. E008k uses only E008j's zero-MMIO allocation/bind path before
packet0.

The runner intentionally does **not** call the E004ns final-state prepare
helper. E007y packet0/packet1 own the captured rear startup transport. E004ns
is used for the exact rear mode predicate and final IPP enable, avoiding an
unobserved CPU-MMIO replay order.

## Fail closed

Before any hardware MMIO, allocation failures free only never-exposed DMA and
release the owner cleanly. Once RT-CDM/BUS/source hardware has been touched,
any error faults both E007z ledgers, performs best-effort CSID/BUS/RT-CDM/source
stop, and releases the shared owner with hardware_teardown_safe=false so
ownership remains pinned until reboot. DMA and the PM reference are not freed
on that fault path.

Even on a successful two-frame teardown, output DMA mappings remain
intentionally pinned. A later checkpoint must close safe post-teardown DMA
free/reuse before ordinary persistent runtime.

## Safety boundary

There is no module parameter, probe hook, V4L2 callback or call site to the
runner. The standalone authorization symbol still returns -EOPNOTSUPP.
Building this checkpoint must not install/load a module, activate a camera or
reboot the machine.

## Build result

The first isolated build identity failed before a module because the bridge used a non-existent RT-CDM IRQ-mask macro. The second failed at compile time because the integrated providers were injected before native VFE helper declarations and because pipeline-PM calls crossed translation-unit visibility. Both failures were source/build-only and caused no runtime action.

Fresh build v3 passes W=1 against the protected Golden headers: qcom-camss.ko is 14,636,992 bytes, SHA-256 `389efc9b4f01c2cbb4d30be28d233ffffd212515083799ab858902c5c326cd46`, with exact Golden vermagic `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`. PiMaster and independent Fabric verification both pass. No install, load, camera activation, RT-CDM runtime submission or reboot occurred.

## Remaining gate

The orchestration itself is now mechanically complete, but it still requires caller-owned Linux command DMA backing for the four E007y MAIN/DMI/wrapper/dynamic objects. Successful output-DMA post-stop free/reuse also remains deliberately unimplemented; E008k pins exposed output mappings instead. Those lifetimes must be closed before wiring a real runtime call site.
