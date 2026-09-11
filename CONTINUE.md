# Resume contract

If the user says **“continue the camera work on SP11”**, do not ask them to repeat the project context.

1. Read `HANDOFF.md`, `AGENTS.md`, and `state/project.yaml`.
2. Run `./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process` before meaningful mutation.
3. Compare local HEAD/origin and inspect the intended stage path before creating or changing it.
4. Treat machine state, Git history and immutable archives as authoritative over chat chronology. Audit unexpected existing work; do not repeat it.
5. Before a risky boot/runtime mutation, checkpoint and push the exact prepared candidate.
6. One fresh candidate identity, one candidate boot, one camera stream. No same-boot retry.
7. After any live result: archive evidence, reboot Golden, verify Golden, retire candidate, then commit/push.

Current durable live frontier: **GO R5..R27 consumed PASS / Golden return PASS / candidate retired**. GL/GM/GN are the closed offline prerequisites and GJ/GK close content authority through R27.

Next action: **continuous delayed sensor-control feedback**, starting offline/read-only. Use GO's immutable G1..G27 statistics/control evidence to prove control-to-statistics timing, design the scheduler extension beyond the three startup writes, and build deterministic offline regressions before authorizing another runtime candidate.

Do not resume the +3-frame bounded ladder mechanically. Any future live control experiment needs a fresh identity, explicit authority, one-shot boot and no same-boot retry.
