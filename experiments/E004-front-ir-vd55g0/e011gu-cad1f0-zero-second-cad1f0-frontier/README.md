# E011GU — CAD1F0 zero-count return to second CAD1F0 call frontier

Four source-exact placements execute the first `0xCAB3EC -> 0xCAD1F0` call with `x2=0`. The helper takes its zero-count fast path at `0xCAD214` and returns without reading receiver `+0x460` or the receiver-owned stream object. The caller then takes the clear-bit-3 path from receiver `+0x28 = 0` and the zero path from receiver `+0x4c = 0`.

Execution stops at the second `0xCAB58C -> 0xCAD1F0` call with `x0=receiver+0x460`, `x1=RVA 0x1370780`, `x2=1`, `x3=receiver+0x20`, and `x4=receiver+0x4c0`. Accepted E011GA construction qualifies the pointer stored at receiver `+0x460` as receiver-relative `-0x20`. E011GV executes only through that pointer load and stops before the object-field pair read at `0xCAD21C`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
