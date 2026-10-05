# E011GV — second CAD1F0 stream-pointer load to object-field frontier

Four source-exact placements execute the second `0xCAB58C -> 0xCAD1F0` call under the accepted E011GU tuple. The nonzero-count path reaches `0xCAD218`, where receiver `+0x460` is read and selects the accepted E011GA stream object at receiver-relative `-0x20`.

Execution stops at `0xCAD21C` before its 16-byte read of object fields at receiver-relative `-0x18/-0x10`. Those field values are not claimed by GV. E011GW reuses the accepted E011FZ CA6280 final-frame construction to source-qualify the object qwords, execute the unequal-field path, and stop before `0xCAD25C -> 0xF5D480`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
