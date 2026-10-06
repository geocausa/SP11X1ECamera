# E011IH — native 0x160A218 zero to second 0x600474 frontier

PASS. E011IH reuses the accepted E011FL same-boot Windows authority that `RVA 0x160A218 = 0`, executes the original `0x60046C` load and the `0x600470` bit-16 test, confirms the branch is not taken, and stops before `0x600474` reads `RVA 0x1608858`. Current second-iteration state `w26=1`, `x23=RVA 0x10F03B0` is preserved.

NEXT E011II reuses accepted E011FM authority for `RVA 0x1608858 = 1`. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
