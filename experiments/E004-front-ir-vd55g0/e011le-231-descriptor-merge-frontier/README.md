# E011LE — complete 231-descriptor merge

PASS. E011LE executes the accepted single enumeration entry at `0x5B8778 -> 0x5B9C80`. The original 62-descriptor source block at RVA `0x1617B40` is deep-copied after the accepted 169 runtime descriptors, producing a source-exact 231-entry / 7392-byte table. The superseded 169-entry ownership tree is destroyed, the one-entry enumeration allocation is freed, and global pair RVA `0x1766540/+8` plus caller `SP+0x50` are cleared. The closure covers 231 descriptor-copy calls, 982 owned allocations/clears, 750 bounded string copies and 790 superseded owned frees. Execution stops before `0x5B87F8`.

NEXT E011LF closes the descriptor-index/prefix/scalar-array derivation and stops at `0x5B8B68`. No new camera Start, reboot, rear runtime, or kernel build is used.
