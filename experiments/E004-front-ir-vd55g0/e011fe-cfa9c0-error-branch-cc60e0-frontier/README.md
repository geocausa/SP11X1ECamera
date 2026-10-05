# E011FE: CFA9C0 error branch to CC60E0 frontier

Status: **PASS_CFA9C0_ERROR_BRANCH_TO_CC60E0_FRONTIER**.

E011FE resumes accepted E011FD at `0xCFA9C0`. With the exact incoming CFCC18 return `2`, original source takes the nonzero branch to `0xCFA99C`, sets `x0=0`, bypasses the selected-object mutation path, executes the original CFA968 epilogue/`ret`, and lands at `0xCED178`. The outer caller stores the zero result, takes its zero-result cleanup branch, reloads the exact retained selected-object pointer, and reaches `0xCED188 -> 0xCC60E0`. The selected object is still byte-exact and its owned lock remains held; `CC60E0` is deliberately not executed yet. The already-released 76-byte Unicode owner is never read again, and both lowIO lock depths remain zero.

Four cases reject 1,236 current-path mutations plus 264 inherited producer API mutations. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FF** qualifies the exact `0xCC60E0` selected-object cleanup path before any selected-object lock release or broader outer return is claimed.
