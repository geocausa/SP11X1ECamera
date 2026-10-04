# E011ET: post-conversion parent to CFD570 call frontier

Status: **PASS_POST_CONVERSION_CFD570_CALL_FRONTIER**.

E011ET resumes the original parent at the accepted E011ES `0xCFD4E8` boundary. The completed 76-byte UTF-16 owner is loaded from the parent local state, the success branch is taken, and the original instructions reshape the retained parent registers into the exact seven-argument call for `0xCFD570`.

Across four placements the call setup is exact: argument0/1 are the retained parent locals, argument2 is the qualified owned UTF-16 pointer, scalars are 0/128/384/1, and SP is unchanged at the retained parent frame. 772 altered contracts are rejected. `0xCFD570` itself is deliberately not executed here.

No camera Start, reboot, kernel build, production-C or PM change was made. The selected lock remains held and the index-8 global lock remains released.

NEXT **E011EU** enters original `0xCFD570` and stops at the first dependency that is not already source-qualified. Native rear runtime remains denied.
