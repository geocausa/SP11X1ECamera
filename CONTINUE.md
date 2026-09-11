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

**GW minimal changed-post-G3 authority PASS and GX helper integration PASS. GY is PREPARED / UNARMED / prearm PASS.** GY permits exactly one new changed post-G3 sensor transaction: source G4 only, and only if native G4 still equals last-applied G3; it then changes digital gain 1471→1472 (+1 LSB, +0.06798%) with no frame-timing change. G5..G26 remain shadow-only.

Next action: commit/push the exact GY candidate, rerun prearm, then one fresh GY boot and one stream maximum. Archive immediately, return Golden and retire. No same-boot retry.
