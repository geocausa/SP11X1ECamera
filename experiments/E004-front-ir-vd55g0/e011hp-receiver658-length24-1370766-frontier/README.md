# E011HP — receiver+0x658 length-24 vararg to RVA 0x1370766 read frontier

The accepted `0x7AC38` layout source-qualifies receiver `+0x658` as image RVA `0x13F1F28`. The pinned image qualifies a NUL-terminated source block of length `24`. Across four opaque-cookie placements the original repeated helper executes through scan, both `CAD1F0` calls, the 24-byte `F5D480` copy, stream updates, and `CAB178` return.

Stream qword0 advances from receiver `+0x6b2` to `+0x6ca`, count from `2` to `26`, and receiver `+0x20` from `2` to `26`. Execution stops before `0xCA984C` reads source RVA `0x1370766`. E011HQ source-qualifies that byte and stops before the receiver `+0x468` termination-loop field is read.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
