# E011GC — first parser-table byte to second lookup frontier

The pinned `.rdata` byte at RVA `0xF8B21B` is exactly `1`. Four source-exact placements execute the original first table read and current index arithmetic, with parser state `0`, producing scaled state `9` and second lookup offset `18`.

Execution stops before `0xCA95D8 -> 0xF8B222`. No camera Start, reboot, rear runtime, or kernel build is used. NEXT is E011GD.
