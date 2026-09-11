# Resume contract

If the user says **“continue the camera work on SP11”**, do not ask them to repeat the project context.

1. Read `HANDOFF.md`, `AGENTS.md`, and `state/project.yaml`.
2. Run `./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process` before meaningful mutation.
3. Compare local HEAD/origin and inspect the intended stage path before creating or changing it.
4. Treat machine state, Git history and immutable archives as authoritative over chat chronology. Audit unexpected existing work; do not repeat it.
5. Before a risky boot/runtime mutation, checkpoint and push the exact prepared candidate.
6. One fresh candidate identity, one candidate boot, one camera stream. No same-boot retry.
7. After any live result: archive evidence, reboot Golden, verify Golden, retire candidate, then commit/push.

Current durable offline frontier: **GL G1..G24 publisher PASS, GM R5..R27 producer PASS, GN 27-frame transport PASS**. GO is now **PREPARED / UNARMED / prearm PASS**; no GO camera runtime has occurred.

Next action: install GO unarmed, rerun prearm, arm exactly one GRUB one-shot, reboot the fresh candidate and perform at most one camera stream. On any result preserve/archive evidence and immediately return Golden. No same-boot retry.

After GO PASS, pivot to continuous delayed sensor-control feedback and robustness; do not keep extending the bounded ladder mechanically.
