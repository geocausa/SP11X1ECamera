# E011IG — second-iteration nonzero cleanup to 0x60046C frontier

PASS. Starting from the accepted E011IF return at `0x600454` with `w0=2`, current loop counter `w26=1`, and `x23=RVA 0x10F03B0`, the original caller takes the nonzero-result path, clears `x20`, zeros the output slot, and reaches `0x60046C` without executing its global read.

NEXT E011IH reuses the accepted E011FL native authority for `RVA 0x160A218 = 0`, executes the load/bit16 test, and stops before the `0x600474` read. No new camera Start, reboot, rear runtime, or kernel build is used. Native rear remains denied.
