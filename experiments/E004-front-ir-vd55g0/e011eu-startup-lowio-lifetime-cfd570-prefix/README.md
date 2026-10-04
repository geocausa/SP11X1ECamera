# E011EU: startup lowIO lifetime join and CFD570 prefix

Status: **PASS_STARTUP_LOWIO_LIFETIME_JOIN_CFD570_PREFIX**.

E011EU closes the low-level-I/O state gap exposed after E011ET without manufacturing a cold runtime table. Source analysis ties subsystem pair eight to `0xCB5DD0 / 0xCB5E20`: the first member requires the original `0xCC06F0` producer during successful attach, while the reverse second-member walker is reached from the detach/finalization path. The accepted camera interval is before detach. The only direct original-code `0xCC08E8` call is the pending `0xCFD5E8` site.

Four placements independently regenerate the accepted attach-time lowIO state through the E011CM original producer contract, then join only that source-qualified table/count/block state into the retained camera context. The table contains 64 records of 72 bytes; its count is 64. The entire joined 4608-byte block and pointer/count remain unchanged through the already-qualified camera chain and into original `0xCFD570`.

Original `0xCFD570` now executes its prefix and the original `0xCFD0B0` parser returns under the exact E011ET arguments. Execution stops immediately before `0xCFD5E8 -> 0xCC08E8`. Across four placements 820 altered contracts are rejected. No camera Start, reboot, kernel build, production-C or PM change was required.

This does **not** claim native Windows lowIO record selection, native critical-section representation/concurrency, `0xCC08E8` effects, or complete `0xCFD570`/file behavior.

NEXT **E011EV** executes original `0xCC08E8` only under the joined source-qualified startup table and inherited owned lock contracts, then advances until the next unqualified dependency. Native rear runtime remains denied.
