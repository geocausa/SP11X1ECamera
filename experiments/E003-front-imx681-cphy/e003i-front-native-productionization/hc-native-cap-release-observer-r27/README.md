# E003i-HC — native cap-release observer R27 live candidate

Status: **CONSUMED LIVE PASS_NO_CAP_RELEASE / GOLDEN RESTORED / CANDIDATE RETIRED.**

HC is the first production-native post-G3 feedback observer. It adds no synthetic control delta. G1..G3 retain the proven startup path. For G4..G26, HA/HB inspect the native AEC result at the exact release boundary:

- while Short convergence is still preview-cap-censored, the source remains shadow-only;
- an unchanged native tuple remains shadow-only;
- if the native Short convergence is strictly below the preview cap, the cap output equals the unconstrained value, and the native tuple changed, exactly one later native tuple may reach the sensor;
- after that one later native write, every remaining source is shadow-only.


Live attempt 1 completed exactly one 27-frame stream on candidate head `8aee1d15179fd8b7c25d133d80bf8c4f02f78ee4`. The native controller remained preview-cap-censored for every eligible source G4..G24, so HC correctly performed **zero** post-G3 native sensor writes. G25/G26 were forced shadow by the evidence-horizon guard. Only bootstrap + startup native G1..G3 reached the IMX681 driver. STREAMOFF and kernel health passed. No same-boot retry occurred.

Archive: `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hc/attempt1-pass-no-cap-release-20260912T060723` (final manifest SHA256 `48444de6fafc7efbab9c71fa0947c193c6c4477a918846e6d787c8095c2c549d`). Candidate boot ID `5e74bde7-cd5e-49aa-ac2f-4852ef944119`; Golden return boot ID `f7758c89-cc63-462c-bf17-2bc459016757`. Candidate identity was retired after Golden return.

HC therefore validates the production-native **decision/lifecycle path** but does not yet prove a changed native post-G3 write, because the observed scene never released the preview cap. The next gate must establish a defensible cap-release observation strategy offline; do not rerun HC and do not manufacture a larger synthetic gain step.

The 27-frame stream has two valid outcomes: **PASS_NO_CAP_RELEASE** (safe observation, no new later write) or **PASS_CAP_RELEASE_ONE_NATIVE_WRITE** (one production-native later write). Either outcome consumes the one-shot and requires immediate archive, Golden return and candidate retirement. No same-boot retry.
