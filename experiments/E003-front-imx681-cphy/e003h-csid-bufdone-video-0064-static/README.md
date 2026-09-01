# E003h 0064 — CSID BUF_DONE VIDEO generation gate

Same-machine Windows reversing proved that qccamisp reads CSID1 `BUF_DONE_IRQ_STATUS` at `+0x8c` and maps **bit0** directly to IFE VIDEO event 3. The first VIDEO bit0 is co-latched in the same CSID interrupt record as first Epoch0, so an accumulated ever-seen latch would still retire too early.

0064 keeps every 0063 hardware operation unchanged. Linux already reads and clears `CSID +0x8c` in the ISR. 0064 only counts existing bit0 observations in software, snapshots that count immediately after first Epoch0, performs the already-existing BUS slot1 retarget + replay2, then waits for the **next** bit0 generation. No new MMIO read/write, register value, mask programming, sensor/CSIPHY/CSID setup, VFE BUS programming, RT-CDM payload, DT, or geometry change is introduced.

Static inspection: `0064-static-inspection.json` (`accepted=true`, `runtime_authorized=false`).
