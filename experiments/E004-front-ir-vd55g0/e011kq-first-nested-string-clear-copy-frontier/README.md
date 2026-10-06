# E011KQ — first nested string clear/copy frontier

PASS. E011KQ follows the nonzero `x25` path, clears exactly 23 owned bytes through `0x5B99E0 -> 0xF5E600`, preserves redzones and the source span at RVA `0x1362948`, and forms the exact bounded copy arguments for `0x5B9A08 -> 0xCAE7C0` without executing the copy.

NEXT E011KR executes that source-exact copy, requires a zero return, and stops at `0x5B9A0C` before nested pointer/scalar publication. No new camera Start, reboot, rear runtime, or kernel build is used.
