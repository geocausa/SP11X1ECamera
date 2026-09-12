# E003i-HC — native cap-release observer R27 live candidate

Status: **PREPARING / UNARMED / NO HC CAMERA RUNTIME YET.**

HC is the first production-native post-G3 feedback observer. It adds no synthetic control delta. G1..G3 retain the proven startup path. For G4..G26, HA/HB inspect the native AEC result at the exact release boundary:

- while Short convergence is still preview-cap-censored, the source remains shadow-only;
- an unchanged native tuple remains shadow-only;
- if the native Short convergence is strictly below the preview cap, the cap output equals the unconstrained value, and the native tuple changed, exactly one later native tuple may reach the sensor;
- after that one later native write, every remaining source is shadow-only.

The 27-frame stream has two valid outcomes: **PASS_NO_CAP_RELEASE** (safe observation, no new later write) or **PASS_CAP_RELEASE_ONE_NATIVE_WRITE** (one production-native later write). Either outcome consumes the one-shot and requires immediate archive, Golden return and candidate retirement. No same-boot retry.
