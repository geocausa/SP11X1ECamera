# E008a — rear VFE1 BUS-stop and CSID1 IRQ-drain contract

Status: **BUILD-ONLY PASS**.

## Purpose

E007z proves which Linux-owned IOVA each of the ten measured rear VFE680 write
masters may retire. E008a closes the two hardware teardown predicates E007z
requires before those mappings can ever be released or reused:

1. the CSID1 IPP producer is reset/quiesced and its Linux IRQ is fully drained;
2. all ten rear VFE1 write-master CFG registers are exactly zero.

This remains unreachable code. It does not install or invoke either helper.

## CSID1 quiescence

The helper reuses the accepted SP11 CSID680 immediate hardware-reset completion
mechanism already exercised by the front PIX path. Before reset it masks
BUF_DONE/IPP/RX/RDI interrupts while retaining only the reset-completion TOP
interrupt. After reset completion it masks all CSID interrupt banks, clears all
latched status banks, calls synchronize_irq on the real csid->irq twice around
the final clear, and requires TOP/RX/BUF_DONE/IPP/RDI status to read zero.

An explicit exact_rear_owner precondition is required; the helper does not infer
ownership from mutable hardware state.

## VFE1 BUS stop

Pinned Qualcomm BUS-v3 stop_wm writes 0 to each write-client CFG. E008a therefore
uses the stronger zero-CFG postcondition rather than the older front helper's
enable-bit clear. It writes zero to physical rear WM0/1/2/3/11/12/13/14/16/18,
masks the VFE TOP/BUS IRQ banks, orders the MMIO writes, synchronizes vfe->irq,
and requires all ten CFGs plus all four IRQ masks to read zero.

VFE680's ISR is a no-op in the accepted SP11 tree, so frame/DMA completion
retirement remains external-CSID-driven. The VFE IRQ barrier is retained as
teardown hygiene, not as the completion identity fence.

## Safety boundary

No call site, DMA release, buffer requeue, RT-CDM submit, camera activation,
module install or runtime authorization is added here. Any timeout or nonzero
postcondition fails closed. Integration with E005y owner state, E007z retirement
and RT-CDM stop/close is a separate later checkpoint.

## Build result — PASS

A fresh isolated CAMSS copy built against the protected Golden-v4 headers.

- PiMaster verifier: PASS;
- independent Fabric verifier/hash/vermagic check: PASS;
- successful identity: `e008a-rear-vfe1-bus-stop-csid-drain-build-fix1`;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,630,728 bytes;
- SHA-256: `9842c6e33f60b38aef5fff68081845ccf2a9f0c17e7685338c5db21aa7457a77`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained symbols: `csid680_e008a_rear_quiesce`, `vfe680_e008a_rear_bus_stop`;
- install/load/camera/DMA release/RT-CDM submission: none.

The first isolated build identity compiled but emitted two
`-Wmissing-prototypes` warnings. It was rejected and left consumed. Fix1 adds
explicit declarations and tightens the warning gate; it is the accepted build.
