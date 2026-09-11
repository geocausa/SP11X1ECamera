# Resume contract

If the user says **“continue the camera work on SP11”**, do not ask them to repeat the project context.

1. Read `HANDOFF.md`, `AGENTS.md`, and `state/project.yaml`.
2. Run `./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process` before meaningful mutation.
3. Compare local HEAD/origin and inspect the intended stage path before creating or changing it.
4. Treat machine state, Git history and immutable archives as authoritative over chat chronology. Audit unexpected existing work; do not repeat it.
5. Before a risky boot/runtime mutation, checkpoint and push the exact prepared candidate.
6. One fresh candidate identity, one candidate boot, one camera stream. No same-boot retry.
7. After any live result: archive evidence, reboot Golden, verify Golden, retire candidate, then commit/push.

Current durable live frontier: **GO R5..R27 consumed PASS / Golden return PASS / candidate retired**.

The continuous-control pivot has now closed **GP timing authority**, **GQ continuous ring scheduler**, and **GR helper integration** offline.

**GS shadow live validation also PASSed and is consumed/retired.** In exactly one 27-frame stream the continuous scheduler released G1..G26 at the correct live boundaries. Only G1..G3 performed physical sensor ioctls; G4..G26 produced 23 shadow releases. Kernel evidence shows exactly one bootstrap + three real sensor transactions, clean STREAMOFF, Golden return, and no retry.

Next action: build **GT limited redundant-write authority offline**. Permit only a very small number of post-G3 physical writes and only when the control tuple is byte-equivalent to the last proven applied tuple; any changed control remains no-write/fail-closed. Prove this policy and helper integration offline before preparing another candidate.
