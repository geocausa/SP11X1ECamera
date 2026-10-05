# E011FK: caller nonzero return/output cleanup to 60046C

Status: **PASS_CALLER_NONZERO_RETURN_OUTPUT_CLEANUP_TO_60046C_FRONTIER**.

E011FK resumes accepted E011FJ at `0x600454` with `w0=2`. The original `cbz` takes the nonzero fallthrough, `x20` is cleared, and `0x60045C` executes the exact 8-byte zero store to the retained caller output slot at outer-entry `SP-1448`. The original branch at `0x600468` then falls through with `x20=0` to `0x60046C`.

Four cases reject 1,732 current-path mutations plus 264 inherited thread-producer API mutations. The `0x60046C` pointer-field read is deliberately not executed yet. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FL** qualifies the exact 8-byte dependency at RVA `0x160A218` before executing the following bit-16 branch.
