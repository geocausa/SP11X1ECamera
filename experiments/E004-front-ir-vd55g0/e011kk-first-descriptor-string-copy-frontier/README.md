# E011KK — first descriptor string clear to bounded copy frontier

PASS. E011KK follows the nonzero 42-byte string allocation, clears exactly those 42 bytes through `0x5B991C -> 0xF5E600`, verifies adjacent redzones remain untouched, preserves the accepted 41-byte source name plus NUL at RVA `0x13D9678`, and forms the exact bounded-copy arguments `x0=owned buffer`, `x1=42`, `x2=RVA 0x13D9678`, `x3=-1`. It stops before executing `0x5B9940 -> 0xCAE7C0`.

NEXT E011KL executes that copy, publishes the string pointer into the destination descriptor, derives the source entry count `2 * 0x18 = 0x30`, and stops before the nested 48-byte allocator call. No new camera Start, reboot, rear runtime, or kernel build is used.
