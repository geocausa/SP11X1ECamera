# E011KF — 0x1480 allocator return to x24 frontier

PASS. E011KF executes `0x5B82C8 -> 0xCAE740 -> 0xCB16C0` under the already-qualified process-heap contract, requests exactly `0x1480` bytes, receives a nonzero owned allocation, preserves `x23=0x1480`, moves the result into `x24` at `0x5B82CC`, and stops before the `0x5B82D0` null-result branch.

NEXT E011KG follows the nonzero path, clears the complete `0x1480` allocation through `0xF5E600`, and stops at `0x5B82E0`. No new camera Start, reboot, rear runtime, or kernel build is used.
