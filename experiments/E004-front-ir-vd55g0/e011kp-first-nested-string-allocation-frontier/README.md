# E011KP — first nested string allocation frontier

PASS. E011KP executes the accepted `0x5B99CC -> 0xCAE740 -> 0xCB16C0` process-heap allocator chain for exactly 23 bytes, obtains a nonzero owned result in `x25`, preserves `x26=23` and the first nested source-element selection, and stops before the `0x5B99D4` result branch.

NEXT E011KQ follows the nonzero path, clears the 23-byte buffer, forms the bounded source-copy call for the first nested string, and stops before executing `0x5B9A08 -> 0xCAE7C0`. No new camera Start, reboot, rear runtime, or kernel build is used.
