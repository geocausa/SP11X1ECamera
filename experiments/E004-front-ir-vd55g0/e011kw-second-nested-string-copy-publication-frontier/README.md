# E011KW — second nested string copy to publication frontier

PASS. E011KW executes the bounded `0x5B9A08 -> 0xCAE7C0` copy for the accepted 16-byte second nested string, reproduces the complete NUL-terminated span, returns zero, preserves `x25`, and stops at `0x5B9A0C` before publication.

NEXT E011KX publishes the second nested element, closes the two-element payload loop, and stops at the success epilogue frontier. No new camera Start, reboot, rear runtime, or kernel build is used.
