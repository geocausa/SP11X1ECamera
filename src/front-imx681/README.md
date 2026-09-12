# Front IMX681 stable source bundle

This tree is the first **stable, non-experiment-path source snapshot** of the proven SP11 front RGB stack. HF intentionally makes no algorithmic or runtime change.

It contains:

- `kernel/camss/`: the SP11 CAMSS production base with the final R27 `camss.c` authority substituted directly;
- `kernel/imx681/`: the CW atomic clustered IMX681 driver authority and mode register table;
- `userspace/runtime/`: the final HC capture helper, native AEC/CQ stack, continuous scheduler, gain-feed publisher and fail-closed cap-release policy;
- `userspace/iq/`: the exact GM R5..R27 IQ producer source snapshot. Its experiment-local Python dependencies are intentionally still unresolved here and are the next hermeticization gate.

`build-offline.sh` compiles the C helper and both kernel modules without touching camera hardware. The production post-G3 sensor-write path remains fail-closed: this bundle does not claim the HD brighter-scene native-feedback gate is complete.

`PROVENANCE.json` is generated and verified by the HF experiment and pins every copied authority by source path and SHA256.
