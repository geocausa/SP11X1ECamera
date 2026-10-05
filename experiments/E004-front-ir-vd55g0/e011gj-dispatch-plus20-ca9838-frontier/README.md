# E011GJ — signed +20 dispatch to CA9838 case frontier

The exact pinned signed 4-byte dispatch entry at RVA `0xCA9908` is `+20`. Four source-exact placements execute original `0xCA95F4..0xCA9600`, selecting exact case entry RVA `0xCA9838` while deliberately stopping before the case body executes.

Private source inspection shows the selected case begins by moving the receiver to `x0` at `0xCA9838`, then calls helper `0xCAB178` at `0xCA983C`. E011GK therefore executes only the case prefix and stops before that helper call. No helper result, downstream branch, or next source read is claimed here.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
