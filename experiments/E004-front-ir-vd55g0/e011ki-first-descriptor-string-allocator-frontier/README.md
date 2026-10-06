# E011KI — first descriptor prefix to string allocator frontier

PASS. E011KI executes the first `0x5B8344 -> 0x5B9888` descriptor-copy entry, source-qualifies descriptor 0 without exporting raw OEM material, derives a 41-byte NUL-terminated name (safe span hash retained), initializes the destination entry fields, and computes the exact 42-byte nested allocation. It stops before `0x5B9908 -> 0xCAE740`.

NEXT E011KJ executes only that 42-byte owned allocation and stops before the result branch. No new camera Start, reboot, rear runtime, or kernel build is used.
