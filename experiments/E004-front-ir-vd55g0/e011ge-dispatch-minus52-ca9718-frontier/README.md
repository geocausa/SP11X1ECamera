# E011GE — parser dispatch to selected-case frontier

The pinned signed 4-byte jump-table entry at RVA `0xCA98F0` is exactly `-52`. Four source-exact placements execute the original `0xCA95F4..0xCA9600` dispatch and select case entry `0xCA9718`, stopping before the selected case body executes.

Static source shape shows that case rejoins at `0xCA9848`; E011GF will qualify the owned receiver mutations and stop before the next signed source-byte read at `0xCA984C -> 0x1370761`. No camera Start, reboot, rear runtime, or kernel build is used.
