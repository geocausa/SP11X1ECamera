# E011HI — RVA 0x1370763 byte 0x73 to F8B2B7 first-lookup frontier

The pinned image source separately qualifies RVA `0x1370763 = 0x73` / decimal `115`. Four exact placements execute the signed read, advance receiver `+0x10` to RVA `0x1370764`, store `0x73` at receiver `+0x39`, and re-enter the parser loop with receiver `+0x20 = 1` and parser state `1`. The loop arithmetic derives first-table RVA `0xF8B2B7`.

Execution stops before `0xCA95B8` reads that table byte. E011HJ separately source-qualifies it and derives the second lookup.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
