# E011JF — first zero source copy to +0x3E28 frontier

PASS. E011JF source-qualifies the zero first byte at `buffer+0x3C28`, forms that pointer at `0x5BE47C`, and executes the exact `0x5BE480 -> 0xCAE7C0` bounded copy with destination `x26+0x70`, capacity 512 and count -1. The helper copies only the terminating NUL and returns zero to `0x5BE484`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JG handles the second source at `buffer+0x3E28`.
