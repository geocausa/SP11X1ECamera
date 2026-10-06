# E011KB — returned-object store to +0xC0 read frontier

PASS. E011KB resumes the accepted caller at `0x5B826C`, source-qualifies `x26` as the caller `SP` from `0x5B80D0`, preserves returned object RVA `0x17A70D0`, and executes the `0x5B8270` store at caller `SP+0x70`. Execution stops before `0x5B8274` reads returned-object offset `+0xC0`.

NEXT E011KC consumes the accepted E011JJ zero function-slot authority for object `+0xC0`, forms the dispatch arguments, and stops before the indirect dispatch call at `0x5B8288`. No new camera Start, reboot, rear runtime, or kernel build is used.
