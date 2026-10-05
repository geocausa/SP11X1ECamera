# E011HJ — F8B2B7 byte 8 to F8B2A2 second-lookup frontier

The pinned image source separately qualifies first parser-table RVA `0xF8B2B7 = 8`. Four exact placements execute the first table read and combine scaled value `72` with parser state `1`, producing second lookup offset `146` and RVA `0xF8B2A2`.

Execution stops before `0xCA95D8` reads that byte. E011HK separately source-qualifies it and reuses the accepted index-7 `+20` dispatch entry to stop at `0xCA9838` before the case body.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
