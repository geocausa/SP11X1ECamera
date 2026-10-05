# E011GD — second parser-table byte to jump-table frontier

The pinned `.rdata` byte at RVA `0xF8B222` is exactly `1`. Four source-exact placements execute the second table read, store parser state `1`, pass the current `<8` / `<=7` checks, and form the parser jump-table base `0xCA98EC` with index `1`.

Execution stops before the signed 4-byte read at `0xCA95F4 -> 0xCA98F0`. No camera Start, reboot, rear runtime, or kernel build is used. NEXT is E011GE.
