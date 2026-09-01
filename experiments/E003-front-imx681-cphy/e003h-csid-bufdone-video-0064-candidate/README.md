# E003h 0064 — CSID BUF_DONE VIDEO generation candidate

One-shot Golden-safe candidate. Hardware programming is identical to 0063. The only behavioral change is software pacing: after first CSID Epoch0, snapshot the already-latched CSID `BUF_DONE +0x8c bit0` generation, retain the existing BUS slot1 retarget + replay2, and wait for the next VIDEO generation before retiring slot0.

Runtime remains unauthorized until package inspection and a separate committed authorization record exist. Same-boot retry is forbidden; the runner always reboots to Golden.
