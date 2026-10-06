# E011IW — 0xB0 allocator return to 0x5BEA0C frontier

PASS. E011IW executes `0x5BEA08 -> 0xCAE740 -> 0xCB16C0` under the already accepted E011ES process-heap/HeapAlloc contract, requests exactly 176 bytes, obtains a nonzero owned allocation, restores allocator nonvolatiles, preserves the enumeration object in `x20`, and returns to `0x5BEA0C` without executing its result branch.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011IX follows the accepted nonzero branch, source-qualifies the allocation zero-initialization loop, and stops before `0x5BE3B8 -> 0xCAE7C0`.
