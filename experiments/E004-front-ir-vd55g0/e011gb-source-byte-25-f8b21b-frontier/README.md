# E011GB — exact `0x1370760` source byte to parser-table frontier

The pinned image byte at RVA `0x1370760` is exactly `0x25` (37) in `.rdata`. Four source-exact placements execute `0xCA984C` and the selected nonzero parser path. The owned source pointer advances to `0x1370761`, the byte is retained in the receiver, and the parser computes lookup RVA `0xF8B21B`.

Execution stops before the one-byte table read at `0xCA95B8 -> 0xF8B21B`. No camera Start, reboot, rear runtime, or kernel build is used. NEXT is E011GC.
