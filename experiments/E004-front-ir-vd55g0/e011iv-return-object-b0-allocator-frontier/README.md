# E011IV — return object to 0xB0 allocator-call frontier

PASS. E011IV resumes at `0x5BEA00`, preserves the accepted enumeration return object in `x20`, places the exact allocation size `0xB0` (176 bytes) in `x0`, and stops before `0x5BEA08 -> 0xCAE740`. Source shows `0xCAE740` is a direct thunk to the already-qualified allocator at `0xCB16C0`; no allocation is executed in this checkpoint.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011IW reuses the accepted E011ES owned process-heap allocator contract for the 176-byte allocation and stops at `0x5BEA0C` before its result branch.
