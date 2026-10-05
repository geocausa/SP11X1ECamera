# E011FI: CED330 zero store/branch to CAECF8 frontier

Status: **PASS_CED330_ZERO_STORE_BRANCH_TO_CAECF8_FRONTIER**.

E011FI resumes accepted E011FH at `0xCED330`. The original source executes the 8-byte `x0=0` store through the exact caller output pointer at outer-entry `SP-1448`, then the original `0xCED334` zero branch falls through to the `0xCED338` call of `0xCAECF8`. Before allowing that call boundary, the retained same-thread authority is rechecked: OS error remains `3`, CRT error remains `2`, the selected-object lock is already released, and the retired 76-byte UTF-16 owner remains released with no subsequent original reads.

Four cases reject 1,620 current-path mutations plus 264 inherited thread-producer API mutations. The new outer `CAECF8` entry is reached with exact return link `0xCED33C`, but its body is deliberately not executed in this checkpoint. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FJ** executes that outer `CAECF8` invocation and qualifies the returned CRT-error pointer/value before carrying the original `CED2F0` epilogue farther.
