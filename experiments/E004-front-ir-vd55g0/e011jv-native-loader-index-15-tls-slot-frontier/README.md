# E011JV — native loader index 15 to TLS publication frontier

PASS. The bounded Windows oracle measured loader-index RVA `0x16A3740` as `15` before a front reader Start and again after a successful `NV12 1920x1080` Start in the same process/module context. Source-exact continuation then executes `0xCE7A90..0xCE7AA4`: `x18+0x58` selects the TLS array, slot `15` selects the current block, and the accepted epoch `0x80000043` is stored at block offset `+0x10`.

NEXT E011JW qualifies and executes `ReleaseSRWLockExclusive` through import RVA `0xF7E518`, then stops before `WakeAllConditionVariable` at `0xCE7AC0`. One bounded front Start was used for the oracle; rear runtime remains denied. The machine is back on Golden Linux.
