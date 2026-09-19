# Resume contract

> **Current frontier — 2026-09-19 / E004fr bounded Windows exposure-write trace PASS, Golden restored; E004fs offline emitter timing/timeout review next:** Native Linux IR remains unilluminated. E004fr recorded 114 contiguous sensor register writes during one 12-frame Windows IR preview, including 16 coarse-exposure programming groups (32 through 1955 lines) and frame-length values of 1955/2000 lines. KD and Windows original reports are archived with hash-checked offline verification. This is software write-observation evidence, not an electrical pulse-width/current measurement or proof of PMIC fail-safe timeout. E004fq remains a separately consumed, aborted attempt. The unsigned HLOS IR worker has only offline pixel-processing and archived-pattern format-bridge validation, not face authentication.


**Parallel unprotected IR processing frontier — 2026-09-19:** Commit `75005b2` introduced an ordinary Linux/HLOS offline adapter for the maintained protected-worker pixel core. The subsequent `src/sp11-camera-hlos-worker/` RGB888-to-NV12 bridge has been tested end to end on all 16 archived E004fe sensor-pattern frames (frame format/hash verified), with byte-exact independently constructed NV12, a deterministic processed output and ASan/UBSan pass. This is **offline format + pixel-processing proof only**, not an illuminated optical capture, face identification, liveness, authentication or system login. The original protected worker and Golden are unchanged. Continue HLOS functional development separately from the **still-open E004fs emitter timing/timeout review after the E004fr exposure trace** for native IR illumination; do not treat this experiment as authorizing emitter activation or a SecurePD trust workaround.

**E004fq Windows one-shot disposition — 2026-09-19:** One fresh Windows BootNext entered KD and passed idle register-filter validation. The live `arm.kd` was rejected by KD (`Malformed string` from unescaped nested `.printf` quotes), **before invoking capture.ps1 or collecting any IR frames**. The breakpoint list was cleared, Windows resumed, and SP11 rebooted to Golden with unchanged BootOrder, empty GRUB next_entry and camera-idle overlap guard PASS. The entire E004fq identity is consumed; its original KD log and abort record are archived. E004fr subsequently used a separate fresh boot and passed: corrected KD observer accepted, 12 Windows IR frames acquired, 114 sensor writes recorded, breakpoints cleared, Golden restored. See E004fr RESULT.json; native emitter remains OFF pending E004fs independent timing/current/timeout review.

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

**RGB bounded production authority remains accepted, and front IR has now advanced through E004fe/E004fn.** Linux VD55G0 transport, stock-libcamera capture, controls and processed monochrome are live-proven; E004fn proves Windows' normal 700 mA LED1 request plus selector-0 hardware/level/active-high trigger arm/disable sequence. Native illumination itself remains deliberately disabled while PMIC register state and pulse policy are closed.

Next action: **E004fs offline emitter timing/current/timeout authority review** using the completed E004fp and E004fr evidence. E004fp, E004fq and E004fr are consumed and must not be reused. Prefer offline/static closure first; use a fresh Windows identity only for a bounded observer that answers a specific remaining timing question. Do not activate the Linux emitter until the exposure/pulse envelope and timeout policy are mechanically justified.
