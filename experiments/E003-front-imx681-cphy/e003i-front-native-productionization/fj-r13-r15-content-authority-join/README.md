# E003i-FJ — R13–R15 content authority join

Status: **PASS_OFFLINE_R13_R15_CONTENT_AUTHORIZED.**

FJ closes the authority gap identified by FG without performing camera runtime.

Authority join:
- FG: deterministic R13–R15 composition from immutable FF G10/G11/G12 continuation inputs, while reproducing live FF R5–R12 8/8 byte-exact.
- FH: recovered same-stream Windows AWB/GainAdj authority through R18, 15/15 bit-exact.
- FI: fresh one-stream Windows Tintless/LSC oracle through R15, 12/12 byte-exact clean-room replay.
- EB: Windows GTM post-R6 stable output law.

This authorizes the existing production component algorithms for bounded R13–R15 composition. It does not claim a same-scene whole-capsule Windows byte oracle and does not claim unrestricted continuous streaming.
