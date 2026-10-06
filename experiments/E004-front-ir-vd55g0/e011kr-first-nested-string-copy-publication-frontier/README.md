# E011KR — first nested string copy to publication frontier

PASS. E011KR executes the bounded `0x5B9A08 -> 0xCAE7C0` copy for the accepted 23-byte first nested string, reproduces the entire NUL-terminated span exactly, returns `w0=0`, preserves the owned destination in `x25`, and stops at `0x5B9A0C` before publication.

NEXT E011KS publishes the first nested element metadata, advances the source loop index to element 1, and stops before reading the second nested source element. No new camera Start, reboot, rear runtime, or kernel build is used.
