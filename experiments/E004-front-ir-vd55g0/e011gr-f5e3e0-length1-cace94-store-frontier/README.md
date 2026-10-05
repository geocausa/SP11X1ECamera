# E011GR — F5E3E0 source-backed length 1 to CACE94 store frontier

The first 16-byte block consumed by `0xF5E3E0` is source-qualified at image RVA `0x1370780`; its first byte is `0x2e` and its first zero byte is at offset `1`. Four placements execute the original call at `0xCACE90` and the source-backed vector scan. The helper returns exact length `1` and execution stops at `0xCACE94` before receiver `+0x48` is written.

E011GS will execute that store and the `0xCACDF8` epilogue/return only far enough to reach the helper continuation and the first `x22` write frontier.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
