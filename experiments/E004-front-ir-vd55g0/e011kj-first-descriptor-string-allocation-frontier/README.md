# E011KJ — first descriptor string allocation frontier

PASS. E011KJ executes the accepted `0x5B9908 -> 0xCAE740 -> 0xCB16C0` allocator chain for exactly 42 bytes, uses the qualified owned process heap/HeapAlloc contract, obtains a nonzero pointer, moves it to `x21`, and preserves the descriptor source/destination state. It stops before the `0x5B9910` result branch.

NEXT E011KK follows the nonzero path, clears the 42-byte string buffer, forms the bounded source-copy call, and stops before executing `0x5B9940 -> 0xCAE7C0`. No new camera Start, reboot, rear runtime, or kernel build is used.
