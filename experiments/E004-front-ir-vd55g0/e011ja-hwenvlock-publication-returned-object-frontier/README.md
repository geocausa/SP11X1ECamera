# E011JA — HwEnvLock publication to returned-object frontier

PASS. E011JA executes the source-owned publication at `0x5BE3CC`, storing the constructed nonzero `HwEnvLock` object pointer to `RVA 0x1B30170 + 0x118 = 0x1B30288`. It then materializes the next source page in `x24`, confirms the preserved enumeration return object in `x20` is nonzero, follows the nonzero branch, and stops before `0x5BE3D8` reads `[x20+0x10]`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JB must source-qualify the returned object `+0x10` pointer before executing that read.
