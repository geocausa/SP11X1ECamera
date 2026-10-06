# E011II — native 0x1608858 one to second 0x6006D4 frontier

PASS. E011II reuses the accepted E011FM same-boot Windows authority that `RVA 0x1608858 = 1`, executes the exact `0x600474` load and `0x600478` nonzero branch, and reaches `0x6006D4` with current loop counter `w26=1` and `x23=RVA 0x10F03B0` preserved. The decrement has not executed.

NEXT E011IJ executes the decrement/branch and stops before the local read at `0x6006DC`. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
