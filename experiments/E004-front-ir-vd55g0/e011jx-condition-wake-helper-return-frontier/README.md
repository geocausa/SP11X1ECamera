# E011JX — condition wake and helper return frontier

PASS. E011JX executes the accepted `WakeAllConditionVariable` call at `0xCE7AC0` through import RVA `0xF7E410` with `x0=RVA 0x16A3730` after the SRW lock is released. The source-exact epilogue restores the helper frame and returns through `0xCE7AD0` to caller RVA `0x5BE674`, where execution stops before the branch to `0x5BDEB8`.

NEXT E011JY follows that caller branch, reuses the accepted E011JP `x25` authority and zero at `x25+4`, qualifies the compare/branch at `0x5BDEB8..0x5BDEC0`, and stops at `0x5BE368`. No new camera Start, reboot, rear runtime, or kernel build is used.
