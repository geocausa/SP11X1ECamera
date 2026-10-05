# E011FG: selected-object lock release to CED194 frontier

Status: **PASS_SELECTED_LOCK_RELEASE_TO_CED194_FRONTIER**.

E011FG resumes accepted E011FF at `0xCED190`. The original `CB3480` wrapper reads the `LeaveCriticalSection` import, translates the exact selected-object pointer to its `+0x30` critical-section field, and tail-calls the owned OS release contract with return site `0xCED194`. The logical selected-object lock therefore transitions from held to released while the exact E011FF cleanup image (including claim `0`) is preserved. Both lowIO locks remain released and the retired 76-byte Unicode owner is never read again.

Four cases reject 1,496 current-path mutations plus 264 inherited thread-producer API mutations. This checkpoint proves the source/owned release contract only; it does **not** qualify native critical-section bytes or concurrency semantics. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FH** propagates the zero result from `0xCED194` through the `0xCED110` epilogue and qualifies the enclosing return only to its exact caller.
