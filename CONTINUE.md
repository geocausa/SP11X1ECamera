# Resume contract

If the user says **“continue the camera work on SP11”**, do not ask them to repeat the project context.

1. Read `HANDOFF.md`, `AGENTS.md`, and `state/project.yaml`.
2. Run `./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process` before meaningful mutation.
3. Compare local HEAD/origin and inspect the intended stage path before creating or changing it.
4. Treat machine state, Git history and immutable archives as authoritative over chat chronology. Audit unexpected existing work; do not repeat it.
5. Before a risky boot/runtime mutation, checkpoint and push the exact prepared candidate.
6. One fresh candidate identity, one candidate boot, one camera stream. No same-boot retry.
7. After any live result: archive evidence, reboot Golden, verify Golden, retire candidate, then commit/push.

Current durable live frontier: **GO R27 PASS, GS continuous-shadow PASS, and GV redundant-ioctl-dedupe PASS; all consumed, Golden-restored and retired.**

GV executed exactly one 27-frame stream. The helper made six successful control ioctls G1..G6, but Linux V4L2 correctly suppressed the exact-equal G4..G6 clusters before the IMX681 driver `.s_ctrl`. Kernel evidence therefore contains bootstrap + G1..G3 only: **zero new post-G3 sensor hardware writes**. The original verifier incorrectly expected every successful ioctl to create a hardware transaction; that was corrected offline after Golden return, with no retry.

The continuous scheduler is live-proven through G26, redundant control-ioctl lifecycle is live-proven, and unchanged-cluster dedupe is now explicit authority. **Changed post-G3 sensor feedback remains unproven.**

**GY minimal changed post-G3 sentinel live PASS is consumed/retired.** One fresh R27 stream applied exactly one changed post-G3 sensor transaction at G4: digital gain 1471→1472 (+1 LSB, +0.06798%) after completed G5 for expected effect G7. Kernel evidence shows exactly bootstrap + G1..G3 + sentinel G4; G5..G26 remained shadow-only. STREAMOFF, kernel health, Golden return and retirement all PASSed with no retry.

GY closes changed post-G3 **transport/lifecycle**, but not production-native feedback: the synthetic +1-LSB perturbation did not move any later native AEC tuple (G5..G27 stayed saturated at the G3 controls).

**GZ response-threshold analysis PASS:** the +0.06798% GY sentinel is below ordinary luma variability, and exact replay proves native Short output is hard-censored by the Windows-derived preview cap from G3 through G27. At G7 unconstrained Short is ~8.40x the cap. A larger synthetic sentinel is explicitly not authorized.

**HA one-native-write policy PASS; HB exact-boundary integration PASS; HC consumed live PASS_NO_CAP_RELEASE.** HC executed one 27-frame stream with no retry. Every eligible G4..G24 native request remained cap-censored, G25/G26 were evidence-horizon shadow-only, and exactly zero post-G3 native writes reached hardware. Only bootstrap + G1..G3 transactions occurred. STREAMOFF, kernel health, Golden return and candidate retirement all PASSed.

**HD real-scene cap-release envelope PASS.** Exact replay of GO/GS/GV/GY/HC shows every Linux R27 run remains cap-active through G27 and ends >8× above the preview cap. Windows DM independently proves ordinary preview can be below cap through R7 before clamping at R8. Therefore a real below-cap regime exists, but these different captures do not provide a defensible numeric lux threshold.

The post-G3 native feedback proof is now **environment-blocked**: it needs a fresh identity under a substantially brighter diffuse real scene, using the existing HA/HB gate and no synthetic control delta. Do not rerun HC, do not just wait longer in the same dark/static scene, and do not guess a larger sensor step.

**HE/HF/HG/HH/HI/HJ production consolidation remains PASS; HK repeated-stream candidate is now prepared offline.** HK uses a fresh identity `sp11-camera-e003i-hk-repeat-shadow-r27-one-shot`, the reproducible HJ package, exactly two sequential 27-frame streams, and explicit `shadow` post-G3 policy with **zero later native writes authorized**. Prearm closes Golden/origin/package/module hashes and no camera runtime has occurred. The candidate is not installed or armed at this checkpoint.

Next action: commit/push this exact HK prep, install the disposable boot entry **unarmed**, re-run the same prearm gates, then create a separate installed-unarmed checkpoint before any one-shot arm/reboot. The brighter-scene native-feedback gate remains parked.
