# E011FN: loop-counter decrement and second `x23` post-index

Status: **PASS_LOOP_COUNTER_SECOND_X23_TO_600424_FRONTIER**.

E011FN resumes the exact E011FM branch frontier. Across four retained placements, original `0x6006D4` sees `w26=2` and decrements it to `1`; original `0x6006D8` therefore loops back to `0x600418`. The carried `x23` is exactly image RVA `0x10F03A8` on second-iteration entry.

Original `0x600420` then reads the next 8-byte entry from read-only `.rdata` RVA `0x10F03A8`. Its source-qualified value is image RVA `0x1370780`, and the post-index advances `x23` to RVA `0x10F03B0`. The replay stops at `0x600424`, before any second-iteration helper call. Four cases reject 1,904 altered current-path contracts plus the inherited 264 producer-API mutations.

No new camera Start, reboot, kernel build, or rear runtime was needed. SP11 remains on verified Golden Linux.

NEXT **E011FO** qualifies the exact second-iteration formatter/helper call setup through the `0x60043C -> 0x7AC38` boundary before executing that helper. Native rear runtime remains denied.
