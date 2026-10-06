# E011JK — source path search to 0x5D0C0 frontier

PASS. E011JK source-qualifies the 97-byte NUL-terminated path at RVA `0x13DBCB0` and executes `0x5BEC84 -> 0xCE7C98` for byte `0x5C`. The helper returns the final backslash at source offset 74; caller `CSINC` selects the basename beginning at offset 75 for logging. Execution stops before `0x5BEC98 -> 0x5D0C0` with `x0=0x20000`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JL qualifies the `0x5D0C0` return before reaching the logger call.
