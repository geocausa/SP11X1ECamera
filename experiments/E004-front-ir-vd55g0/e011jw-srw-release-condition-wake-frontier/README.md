# E011JW — SRW release to condition wake frontier

PASS. E011JW consumes the E011JV TLS publication, source-qualifies the accepted `ReleaseSRWLockExclusive` import at RVA `0xF7E518`, executes `0xCE7AB0` against resource RVA `0x16A3738`, and proves the SRW lock released. It then forms `x0=RVA 0x16A3730` and stops before `0xCE7AC0` calls `WakeAllConditionVariable` through RVA `0xF7E410`.

NEXT E011JX executes that accepted wake, completes the publication-helper epilogue, returns to `0x5BE674`, and stops before the branch to `0x5BDEB8`. No new camera Start, reboot, rear runtime, or kernel build is used.
