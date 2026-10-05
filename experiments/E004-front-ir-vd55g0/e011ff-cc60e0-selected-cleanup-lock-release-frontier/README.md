# E011FF: CC60E0 selected cleanup to lock-release frontier

Status: **PASS_CC60E0_SELECTED_CLEANUP_TO_LOCK_RELEASE_FRONTIER**.

E011FF resumes accepted E011FE at `0xCED188 -> 0xCC60E0`. It joins the already source-qualified process-runtime atomic feature word `0x80000000` from E011EJ/E011CN (a verifier state handoff, not native startup replay), executes the original `CC60E0` stores and the exact `0x12D0` fallback atomic exchange, and proves the selected object claim changes from `0x2000` to `0` while the remaining cleanup image is exact. The separate critical-section region at `+0x30` is unchanged and its owned lock remains held. Original execution returns to `0xCED18C`, reloads the same selected pointer, and stops at `0xCED190 -> 0xCB3480` before lock release.

Four cases reject 1,440 current-path mutations plus 264 inherited thread-producer API mutations. No new camera Start, reboot, kernel build, production change, or rear runtime is used. E011FF does not qualify the native LSE branch or native mutex bytes/concurrency semantics.

NEXT **E011FG** executes the exact `CB3480`/`LeaveCriticalSection` release and resumes the outer caller only while ownership remains exact.
