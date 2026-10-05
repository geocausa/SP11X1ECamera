# E011FO: second-iteration formatter/helper call arguments

Status: **PASS_SECOND_FORMATTER_ARGS_TO_60043C_FRONTIER**.

E011FO continues the accepted second-iteration state from E011FN and executes original setup `0x600424..0x600438`. At the untouched `0x60043C` callsite, four retained placements agree on the exact call tuple: `x0=outer-SP-1392`, `x1=0x280`, `x2=base+0x1370760`, `x3=base+0x1370780`, `x4=base+0x10F03B0`, and `x5=base+0x13F1F28`, with loop counter `w26=1` and retained `x23=base+0x10F03B0`.

The replay stops before executing the `0x7AC38` helper and rejects 1,940 altered current-path contracts plus the inherited 264 producer-API mutations. No new camera Start, reboot, kernel build, or rear runtime was needed.

NEXT **E011FP** executes the original `0x7AC38 -> 0x7ACA0` wrapper chain and stops at the nested `0x6BDD0` dependency unless its current contract is exact. Native rear runtime remains denied.
