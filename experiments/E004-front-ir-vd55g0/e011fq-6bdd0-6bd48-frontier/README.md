# E011FQ: `0x6BDD0` argument reshape to `0x6BD48`

Status: **PASS_6BDD0_TO_6BD48_FRONTIER**.

E011FQ executes the accepted `0x7ACD8 -> 0x6BDD0` dependency. Original `0x6BDD0` preserves the current formatter tuple in its local frame, reloads it with `x4=0`, carries the variadic-list pointer in `x5`, and reaches untouched callsite `0x6BE08`.

Across four retained placements, the exact `0x6BD48` tuple is `x0=outer-SP-1392`, `x1=0x280`, `x2=-1`, `x3=base+0x1370760`, `x4=0`, `x5=outer-SP-1496`. The replay stops before executing `0x6BD48` and rejects 2,040 altered current-path contracts plus the inherited 264 producer-API mutations.

No new camera Start, reboot, kernel build, or rear runtime was needed. NEXT **E011FR** enters `0x6BD48` only far enough to qualify its first `0x6BD6C -> 0xEDD0` dependency. Native rear runtime remains denied.
