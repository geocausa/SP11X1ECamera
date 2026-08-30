# E003h 0048 — CSID1 IPP IRQ-history one-shot candidate

Distinct Golden-safe diagnostic package built from the accepted 0047 transport state. Relative to 0047, only `qcom-camss.ko` changes. The 0048 CAMSS delta is software-only telemetry: the existing CSID680 ISR OR-latches the IPP status value it already read before the existing clear, stores last/count, and the existing timeout dump prints that history.

There are zero new MMIO reads/writes and no changes to IRQ masks/clears, RT-CDM bytes/order, VFE/BUS programming, CSID programming/start, CSIPHY or sensor behavior. The purpose is to determine whether CAMIF/RUP/Epoch bits occurred earlier and were consumed by the normal CSID ISR before the final timeout snapshot.

This package does not contain authorization or prior runtime evidence. Installation does not arm `next_entry`. Runtime activation requires a separately committed `AUTHORIZATION.json`, exactly one candidate boot and one root helper invocation, no same-boot retry, and immediate Golden return.
