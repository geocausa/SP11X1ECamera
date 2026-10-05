# E011GI — table byte 0x07 to CA9908 dispatch frontier

The exact pinned second table byte at image RVA `0xF8B2A2` is `0x07`. Four source-exact placements execute the original read at `0xCA95D8`, retain parser state `7`, pass the original `< 8` / `<= 7` range checks, and form jump-table base RVA `0xCA98EC` with index `7`.

Execution stops at `0xCA95F4` before the signed 4-byte dispatch entry read at RVA `0xCA9908`. E011GJ must source-qualify that exact signed entry before dispatch executes.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
