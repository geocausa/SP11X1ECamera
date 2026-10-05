# E011EX: exact GetLastError return to CAEC20 frontier

Status: **PASS_EXACT_GETLASTERROR_TO_CAEC20_FRONTIER**.

E011EX resumes the accepted E011EW invalid-handle branch without another Windows run. The original `0xCFD6FC` imported `GetLastError` call executes under the already-qualified same-boot Win32 authority and returns exactly `3` (`ERROR_PATH_NOT_FOUND`). Four retained placements preserve the inherited 76-byte UTF-16 owner, lowIO table and lock state and stop at `0xCFD700` before the internal `0xCAEC20` error-propagation helper. 984 altered contracts reject.

No new camera Start, reboot, kernel build or production change is used. The older E011CU/E011CW error-cleanup work is relevant source authority, but its 74-byte Unicode-owner geometry is deliberately **not** joined into this current 76-byte path.

NEXT **E011EY** establishes the current thread/TLS authority needed by `0xCAEC20` and advances error propagation only where the present ownership geometry remains exact. Native rear runtime remains denied.
