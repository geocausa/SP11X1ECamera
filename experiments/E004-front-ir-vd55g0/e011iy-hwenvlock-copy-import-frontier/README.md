# E011IY — HwEnvLock copy to imported critical-section frontier

PASS. E011IY source-qualifies `RVA 0x13DBC80` as NUL-terminated `HwEnvLock`, executes the bounded `0x5BE3B8 -> 0xCAE7C0` copy into allocation `+0x30`, copies exactly ten bytes including NUL, returns `w0=0`, and preserves the owned allocation in `x24`. Execution stops before the next import read/call. Source import metadata identifies slot `RVA 0xF7E0C8` as `KERNEL32!InitializeCriticalSection`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011IZ reuses the accepted logical critical-section contract, executes that import call on allocation `+8`, and stops before object publication at `0x5BE3CC`.
