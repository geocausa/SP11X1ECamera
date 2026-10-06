# E011KH — zero prior count to first descriptor copy frontier

PASS. E011KH resumes at `0x5B82E0`, source-qualifies the E011DS caller count as zero, takes the zero-existing-entry branch, consumes the accepted native descriptor table pointer `RVA 0x1624140` and count `0xA4`, and forms the first 32-byte copy arguments. It stops before `0x5B8344 -> 0x5B9888`.

NEXT E011KI source-qualifies descriptor entry 0 and enters the copy helper only through its first nested string-allocation frontier. No new camera Start, reboot, rear runtime, or kernel build is used.
