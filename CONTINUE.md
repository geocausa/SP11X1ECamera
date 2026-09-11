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

The continuous-control pivot has now closed three offline gates: **GP** GO timing authority PASS, **GQ** two-slot fail-closed continuous scheduler PASS (100,000-generation stress), and **GR** live-helper integration compile PASS with exact DQBUF boundary checks preserved.

A fresh **GS continuous-scheduler shadow candidate** is now PREPARED / UNARMED / prearm PASS. GS releases the continuous scheduler at every G2..G27 boundary but permits real sensor ioctls only for the already-proven G1..G3 sources; G4..G26 are shadow-log only.

Next action: install GS unarmed, rerun prearm, arm exactly one GRUB one-shot, run at most one 27-frame stream, archive immediately and return Golden. No same-boot retry. A GS PASS proves live continuous boundary ownership, not continuous physical writes.
