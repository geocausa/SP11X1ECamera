# E011FP: formatter wrapper chain to `0x6BDD0`

Status: **PASS_FORMATTER_WRAPPERS_TO_6BDD0_FRONTIER**.

E011FP executes the accepted `0x60043C -> 0x7AC38` call and the original `0x7AC38 -> 0x7ACA0` nested wrapper. The wrapper-local argument saves and variadic-list pointer remain confined to the exact active stack-frame range, with no writes outside it.

At original `0x7ACD8`, four retained placements expose the exact untouched `0x6BDD0` dependency tuple: `x0=outer-SP-1392`, `x1=0x280`, `x2=-1`, `x3=base+0x1370760`, and `x4=outer-SP-1496`. The replay stops before executing `0x6BDD0` and rejects 2,004 altered current-path contracts plus the inherited 264 producer-API mutations.

No new camera Start, reboot, kernel build, or rear runtime was needed. NEXT **E011FQ** enters `0x6BDD0` only far enough to qualify its `0x6BE08 -> 0x6BD48` dependency call. Native rear runtime remains denied.
