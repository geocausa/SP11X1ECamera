# E011HF — CA9590 state-7 first lookup to F8B230 frontier

Four exact placements execute the parser loop from `0xCA9590` using source byte `0x25`, receiver `+0x20 = 1`, and parser state `7`. The already-qualified first table byte at RVA `0xF8B21B = 1` is read at `0xCA95B8`. Combining scaled first-table value `9` with state `7` yields second lookup offset `32`, selecting RVA `0xF8B230`.

Execution stops before `0xCA95D8` reads that byte. E011HG separately source-qualifies `0xF8B230`, then reuses the accepted `-52` dispatch entry to reach `0xCA9718` without executing the case body.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
