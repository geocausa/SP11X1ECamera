# E011IJ — second loop counter 1→0 to 0x6006DC frontier

PASS. E011IJ executes the exact `0x6006D4` decrement with current `w26=1`, obtains `w26=0`, confirms the `0x6006D8` loop-back branch is not taken, and stops before `0x6006DC` reads the caller local `[sp+4]`. No memory access occurs in this bounded step.

NEXT E011IK first traces the source-owned provenance/value of `[sp+4]`, then executes the read and branch. No camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
