# E003h 0064 result — first complete Linux front-camera frame

**Accepted.** The single authorized 0064 run completed with helper RC=0 and returned automatically to Golden.

0064 replaced only the bounded runner's stale VFE VIDEO completion wait with the Windows-proven CSID1 `BUF_DONE_IRQ_STATUS (+0x8c) bit0` **generation** gate. The first bit0 is co-latched with first Epoch0, so the runner snapshots that generation after Epoch0, retains BUS slot1 retarget + replay2, and waits for the next generation. No hardware programming changed.

Result: the exact 0x76b000 QC10C surface is fully populated: **1440/1440 Y lines and 720/720 C lines**, with every Y/C metadata and data 4K page touched. 0063 had only 80 Y / 40 C lines. RT-CDM finished at fifo_seq=30 with error=0 and faulted=0. No runtime IOMMU/SMMU fault, Oops, SError, or camera panic was recorded.

This is the **first complete Linux front-camera frame** in the bounded diagnostic path. It does not yet mean normal camera applications work: the helper deliberately saves slot0 without ordinary V4L2 QBUF/STREAMON. The next boundary is to carry the proven lifecycle into the standard vb2/V4L2 streaming path and make frame retirement reusable for continuous capture, without changing the now-proven hardware programming.
