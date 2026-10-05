# E011FD: CFCC18 error return to CFA9C0 frontier

Status: **PASS_CFCC18_ERROR_RETURN_TO_CFA9C0_FRONTIER**.

E011FD resumes accepted E011FC at `0xCFCCE4`. Original source takes the nonzero-return tail, restores the caller-visible result slot to `-1`, moves return `2` into `w0`, executes the `CFCC18` epilogue and original `ret`, and lands exactly at outer caller `0xCFA9C0` across all four retained placement/slot cases. The restored nonvolatile state and caller stack are exact. Both lowIO lock depths remain zero and the released 76-byte owner remains untouched.

Four cases reject 1,212 current-path mutations plus 264 inherited producer API mutations. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FE** qualifies the `0xCFA9C0` nonzero-return branch to `0xCFA99C` before broader outer cleanup/return is claimed.
