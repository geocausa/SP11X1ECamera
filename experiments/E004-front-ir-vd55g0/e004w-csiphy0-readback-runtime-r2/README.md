# E004w — CSIPHY0 8 KiB receiver readback retry candidate

E004w is a fresh one-shot successor to E004u.

E004u proved that the native VD55G0 state, graph and receiver precheck were correct, then faulted in CSIPHY0 reset because the disposable DT mapped only 4 KiB while the X1E common register block begins at offset 0x1000.

E004v mechanically corrected only that resource cell:

- CSIPHY0 old: 0x0ace4000 + 0x1000
- CSIPHY0 new: 0x0ace4000 + 0x2000
- CSIPHY1 remains: 0x0ace6000 + 0x2000
- parent/output DTB differ by one byte only

E004w uses the exact same sensor, CAMSS and receiver-readback binaries as E004u. The only behavioral input change is the E004v DTB.

Acceptance remains receiver-only:

1. dynamically resolve the physical VD55G0 by compatible + address 0x60;
2. load E004k CAMSS and E004l native sensor;
3. wait for the sensor to return to runtime suspend after exact 596-write Windows-state initialization;
4. require the immutable sensor -> CSIPHY0 graph;
5. invoke E004t, which powers/programs CSIPHY0 only;
6. require the E004J Windows-parity programming marker;
7. require 96/96 same-machine Windows CSIPHY0 register readback;
8. switch the receiver off and power it down;
9. require the sensor still suspended;
10. reboot immediately to Golden and retire.

No sensor stream callback, CSID/VFE stream callback, capture or illumination is authorized.

One attempt only. No same-boot retry.
