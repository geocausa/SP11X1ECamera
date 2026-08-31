# E003h 0056 runtime result — CAMNOC 300 MHz parity reached; VFE1 stall unchanged

The single authorized 0056 run executed exactly once and returned immediately to FullIO Golden. There was no retry.

The CCF correction worked at the hardware boundary: Linux transitioned to CAM_CC CAMNOC RT `CFG=0x00000203`, branch enabled, decoded 300 MHz, exactly matching the repeated stock-Windows measurement. The watcher observed this state throughout the active interval (`seen_live_300=1`).

The camera failure did not advance. CSID1 remained healthy at 3840x2160 with no line-count error, RT-CDM completed FIFO 25 without fault, but VFE1 raw Epoch0 remained absent, BUS raw status remained zero, and QC10C output was absent. The VFE1 timeout snapshot is identical to 0054 despite CAMNOC rate parity.

Therefore Linux's prior 19.2 MHz CAMNOC RT state was a real Windows-parity bug, but it is **not causal for the remaining VFE1 ingress/Epoch0 stall**. Retain the 300 MHz correction and move the next gate deeper into VFE1 input/core activation semantics.

**0056 authorization is consumed. No 0056 rerun is permitted.**
