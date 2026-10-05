# E011FJ: outer CAECF8 CRT2 return through CED2F0

Status: **PASS_CAECF8_CRT2_CED2F0_RETURN_TO_600454_FRONTIER**.

E011FJ resumes accepted E011FI at the second `0xCAECF8` entry. Under the rejoined same-thread authority, the original thread getter executes a fourth time and `CAECF8` returns the current-thread CRT-error pointer (`thread+32`). Original `0xCED33C` performs the exact 4-byte read and obtains CRT error `2`; the error epilogue then restores the retained `CED2F0` frame and returns with `w0=2` to the exact caller address `0x600454` at outer-entry `SP-1456`.

Four cases reject 1,680 current-path mutations plus 264 inherited thread-producer API mutations. The selected-object lock and retired 76-byte owner remain released with no later original reads. The caller branch at `0x600454` is deliberately not executed yet. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FK** qualifies the caller's nonzero-return branch and its exact output cleanup.
