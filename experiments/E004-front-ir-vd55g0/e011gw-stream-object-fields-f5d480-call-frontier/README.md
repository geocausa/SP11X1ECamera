# E011GW — stream-object fields to F5D480 copy-call frontier

Accepted E011FZ source placement qualifies the receiver-owned object at `receiver-0x20`: qword0 selects `receiver+0x6b0`, object `+0x8 = 640`, and object `+0x10 = 0`. Four exact placements execute `0xCAD21C`; the unequal-field branch at `0xCAD224` is taken, the qword0 buffer pointer is loaded at `0xCAD248`, and the selected copy count is exactly `1`.

Execution stops at `0xCAD25C -> 0xF5D480` with `x0=receiver+0x6b0`, `x1=RVA 0x1370780`, and `x2=1`. E011GX reuses E011GR source authority for leading byte `0x2e`, executes exactly the one-byte copy, and stops at `0xCAD260` before stream pointer/count updates.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
