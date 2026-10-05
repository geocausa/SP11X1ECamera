# E011HM — receiver+0x650 backslash vararg to RVA 0x1370764 read frontier

The accepted `0x7AC38` vararg layout source-qualifies receiver `+0x650` as image RVA `0x10F03B0`. The pinned image qualifies that string as one byte `0x5c` followed by NUL. Across four opaque-cookie placements the original repeated helper executes through `CA65A8`, `F5E3E0`, both `CAD1F0` calls, the one-byte `F5D480` copy, stream updates, and the `CAB178` cookie/epilogue return.

The stream pointer advances from receiver `+0x6b1` to `+0x6b2`, stream count from `1` to `2`, receiver `+0x20` from `1` to `2`, and receiver `+0x6b1` receives byte `0x5c`. Execution stops before `0xCA984C` reads source RVA `0x1370764`. E011HN source-qualifies that byte and reuses the accepted `%` parser chain.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
