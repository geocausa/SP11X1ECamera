# E011JC — published-buffer flag updates to x26 frontier

PASS. E011JC reuses the accepted zero-backed 18,832-byte enumeration-buffer authority, qualifies offsets `+0x20`, `+0x14`, and `+0x0C` as zero at this point, executes the exact clear/set sequence, and leaves `+0x20 = 0x08000000` while the other two remain zero. The published buffer is reloaded into `x20`; the nonzero branch is taken and `x8=0x442C` is prepared. Execution stops before `0x5BE424` reads `[x26+0x6C]`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JD qualifies the x26 local and buffer `+0x442C` dependencies before advancing.
