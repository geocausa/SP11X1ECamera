# E011JG — second zero source copy to 0x1798508 frontier

PASS. E011JG source-qualifies zero at `buffer+0x3E28` and executes the second exact `0x5BE498 -> 0xCAE7C0` bounded copy to `x26+0x270`, again copying only the terminating NUL and returning zero. Execution stops before the global byte reads based at RVA `0x1798508`.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JH resolves bytes `0x1798509/0x179850A` before those reads.
