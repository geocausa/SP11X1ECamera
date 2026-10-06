# E011IZ — HwEnvLock critical section to publication frontier

PASS. E011IZ independently binds import slot `RVA 0xF7E0C8` to `KERNEL32!InitializeCriticalSection`, reuses the accepted E011DC logical owned-critical-section contract, and executes the imported void call on the new object at allocation `+8` across four distinct return-register residue axes. Native CRITICAL_SECTION bytes and concurrency semantics are intentionally not claimed. Execution returns to `0x5BE3CC` and stops before publishing the constructed pointer.

No new camera Start, reboot, rear runtime, or kernel build is used; native rear remains denied. NEXT E011JA publishes the object to source-owned global owner `RVA 0x1B30170 + 0x118` and stops before the first dereference of the preserved enumeration object.
