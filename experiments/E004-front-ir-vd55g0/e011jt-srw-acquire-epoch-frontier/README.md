# E011JT — SRW acquire to epoch-read frontier

PASS. E011JT executes the accepted `AcquireSRWLockExclusive` dependency at `0xCE7A70` for resource RVA `0x16A3738`, returns to `0xCE7A74` with logical SRW ownership held, and stops before the epoch read at `0xCE7A78` / RVA `0x1607B04`. The accepted inherited epoch is `0x80000042`.

NEXT E011JU consumes that epoch, publishes `0x80000043` to the global cell and guard RVA `0x1B302D0`, and stops before loader-index RVA `0x16A3740`. No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied.
