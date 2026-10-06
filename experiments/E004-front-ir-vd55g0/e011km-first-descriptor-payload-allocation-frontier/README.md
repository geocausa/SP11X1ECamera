# E011KM — first descriptor payload allocation frontier

PASS. E011KM executes `0x5B9968 -> 0xCAE740 -> 0xCB16C0` under the accepted process-heap contract for exactly 48 bytes, obtains a nonzero owned result in `x21`, preserves `x22=48` and descriptor source/destination state, and stops before the `0x5B9970` result branch.

NEXT E011KN follows the nonzero path, clears and publishes the 48-byte payload array, then enters the first nested source element. No new camera Start, reboot, rear runtime, or kernel build is used.
