# E003h 0051 — suppress Linux-only post-RUP REG_UPDATE_CMD write

0050 localizes the first Windows/Linux geometry divergence to the interval after the matching first IPP RUP_DONE IRQ and by the immediately following Epoch0/1 IRQ. The exact installed Windows qccamisp IRQ reader/handler then closes ownership: Windows acknowledges the IPP status but does not test RUP_DONE and does not write CSID `REG_UPDATE_CMD +0x18` from the IRQ path.

Linux currently does more. Its generic CSID680 RUP_DONE bookkeeping calls `csid_reg_update_clear()`, which clears the Linux `reg_update` software shadow and writes that shadow to `+0x18`. On the bounded SP11 front PIX path the actual RUP/AUP command was already submitted by RT-CDM as exact `0x01f501f5`; the Linux software shadow does not own that hardware command lifecycle.

0051 is the smallest fail-closed representation of the Windows ownership model. In the existing IPP RUP_DONE ISR branch only, when the exact X1E80100 front mode0 IPP predicate is true, Linux clears `reg_update_ipp()` from its software shadow and does not call the generic MMIO-clearing helper. All other IPP/RDI/non-front paths still call the existing helper unchanged.

Properties:

- no new MMIO read or write;
- no new register value;
- suppresses exactly the Linux-only post-RUP front-IPP `+0x18` write;
- preserves the existing IPP IRQ clear at `+0xb4` and global IRQ clear;
- preserves generic `csid_reg_update_clear()` and all RDI RUP_DONE handling;
- no crop/CFG/mask/RT-CDM/VFE/CSIPHY/sensor/DT change;
- runtime is not authorized by this static checkpoint.
