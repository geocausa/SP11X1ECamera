# E011FC: caller index-0 lowIO release

Status: **PASS_CALLER_INDEX0_LOWIO_RELEASE_TO_CFCCE4_FRONTIER**.

E011FC resumes accepted E011FB at `0xCFCC9C`. Across all four retained placement/slot cases, original source stores return `2`, reads cleanup flag `1`, follows the nonzero cleanup path, reads exact index `0`, resolves startup lowIO record 0 through global `0x16A2A90`, observes its active byte already cleared, performs the source-idempotent clear, and executes original `0xCC08C0` to the owned `LeaveCriticalSection(record0)` boundary. At `0xCFCCE4`, both the global7 and record0 lowIO lock depths are zero.

The 76-byte Unicode owner released by E011FA remains retired and is not read. Four cases reject 1,168 current-path mutations plus 264 inherited producer API mutations. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FD** qualifies the remaining `CFCC18` error-tail store and epilogue/return to caller `0xCFA9C0`.
