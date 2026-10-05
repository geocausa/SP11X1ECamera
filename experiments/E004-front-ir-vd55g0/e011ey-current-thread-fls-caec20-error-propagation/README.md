# E011EY: current thread/FLS join through CAEC20 error propagation

Status: **PASS_CURRENT_THREAD_FLS_CAEC20_ERROR_PROPAGATION**.

E011EY resumes the accepted E011EX `GetLastError=3` frontier and joins the already-qualified CRT slot/thread producer into the **same current owned CRT arena**: for all four retained placements, the 968-byte thread owner lands exactly at the current bootstrap next-allocation pointer. The original Windows `FlsGetValue2` implementation then retrieves that exact owner twice while original `0xCAEC20` executes and commits thread OS error `3` and CRT error `2`. Four current-path cases reject 1,020 altered contracts; the inherited producer rejects another 264 invalid API requests.

The important ownership distinction remains explicit: the current UTF-16 owner is **76 bytes and remains live**. E011CW's older 74-byte `HeapFree` geometry is not imported or treated as equivalent. The thread/FLS state handoff is a source-qualified owned single-thread join, not a claim that live Windows loader/FLS allocation/setter/concurrency was replayed inside this verifier. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011EZ** follows `0xCFD704 -> 0xCFD5DC`, qualifies the `0xCAECF8` current-thread CRT-error pointer/value, and advances the original CFD570 error return only while the 76-byte owner stays live.
