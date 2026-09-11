# Resume contract

If the user says **“continue the camera work on SP11”**, do not ask them to repeat the project context.

1. Read `HANDOFF.md`, `AGENTS.md`, and `state/project.yaml`.
2. Run `./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process` before meaningful mutation.
3. Compare local HEAD/origin and inspect the intended stage path before creating or changing it.
4. Treat machine state, Git history and immutable archives as authoritative over chat chronology. Audit unexpected existing work; do not repeat it.
5. Before a risky boot/runtime mutation, checkpoint and push the exact prepared candidate.
6. One fresh candidate identity, one candidate boot, one camera stream. No same-boot retry.
7. After any live result: archive evidence, reboot Golden, verify Golden, retire candidate, then commit/push.

Current durable frontier: **GK R25-R27 offline authority closed at `6985bb6`**.

Next action: offline-only **GL publisher -> GM producer -> GN 27-frame transport**. Only after all pass and Golden is clean should fresh **GO R5-R27 one-shot live** be prepared.

After GO PASS, pivot to continuous delayed sensor-control feedback and robustness; do not keep extending the bounded ladder mechanically.
