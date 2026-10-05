# E011FV: current `0xCAD868` x0=36 prefix to `0x16A2A84` frontier

Status: **PASS_CAD868_X0_36_PREFIX_TO_16A2A84_FRONTIER**.

E011FV continues from the accepted E011FU call contract and enters original `0xCAD868` with the native-qualified `x0=36` and the exact retained formatter tuple. Across four placements, the current path executes 18 original instructions per case through the `x5==0` branch, performs 12 exact stack-write chunks per case, and reaches untouched `0xCAD8B8`.

The first new dependency is the 4-byte writable runtime cell at RVA `0x16A2A84`. The older E011DY zero for that cell remains only a loader/owned-model assumption and is not treated as native authority. Execution stops before the read; 2,584 altered current-path contracts plus the inherited 264 producer-API mutations are rejected.

No new camera Start, reboot, kernel build, or rear runtime was needed for FV. NEXT **E011FW** resolves the current/native `0x16A2A84` value before executing `0xCAD8B8`. Native rear runtime remains denied.
