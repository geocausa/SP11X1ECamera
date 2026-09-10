# Resume contract

If the user says **“continue the camera work on SP11”**, do not ask them to repeat the machine access, project goal, hardware list or workflow.

1. Read `AGENTS.md`, the current continuation at the top of `PROJECT_STATE.md`, `state/project.yaml`, and the `handoff.latest` file named there before historical experiment records.
2. Run `tools/project-status.sh` on SP11 Linux when that OS is online.
3. Discover current PiMaster client status. SP11 Linux and SP11 Windows are the same physical machine and are normally mutually exclusive; SP7 is the Windows debugger/oracle companion.
4. Compare live state with the repository state before modifying anything.
5. Resume the `next_action` in `state/project.yaml` unless fresh evidence makes it obsolete.
6. Before a risky boot/kernel/DT experiment, create/update the experiment record and preserve the current Golden rollback.
7. When stopping or when context becomes unreliable, update `PROJECT_STATE.md`, `state/project.yaml`, and the current experiment record, then commit/push the handoff.

The repository, not chat history, is the durable source of project continuity.

Current checkpoint: [DN internal cap handoff](experiments/E003-front-imx681-cphy/e003i-front-native-productionization/dn-native-aec-internal-cap/HANDOFF.md). The saved G4 failure now passes offline; bind the remaining cap branch input before a fresh bounded live candidate.
