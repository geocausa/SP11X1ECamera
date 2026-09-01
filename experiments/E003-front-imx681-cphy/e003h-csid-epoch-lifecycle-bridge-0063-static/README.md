# E003h 0063 — CSID Epoch lifecycle bridge (static)

Windows authority changed the event boundary: on the tested X1E front path, successful streaming advances IFE Epoch lifecycle from the CSID IST message bit21 while the active VFE status-reader callback is not executed. The dual-event trace observed 0 true VFE raw-Epoch hits, but 44 BUS retargets and 44 Epoch RT-CDM consumes.

Linux already receives and software-latches the corresponding CSID1 IPP bit21 in `x1e_ipp_irq_seen_or` before clearing the IRQ. 0063 changes only the bounded runner's Epoch0 wait source from the obsolete VFE BUS status1 MMIO poll to a 500 ms `READ_ONCE` poll of that existing CSID software latch. No new MMIO read, MMIO write, register value, IRQ mask programming, state field, sensor/CSIPHY/CSID programming, VFE BUS programming, RT-CDM payload, DT, or geometry change is introduced.

The existing post-Epoch lifecycle remains unchanged: BUS slot1 retarget -> prime/replay2 -> VFE VIDEO wait -> frame retirement.

Static inspection: `0063-static-inspection.json` (`accepted=true`, `runtime_authorized=false`).
Base Linux runtime authority: 0062r1 analysis SHA256 `e1fc64c2baa82047e4844be1af6254798f7097e22441a84e2c1b4e3615740be3`.
