# SP11X1ECamera

Evidence-driven native Linux camera bring-up for the Microsoft Surface Pro 11 (Denali, X1E80100).

The project goal is **not** to cargo-cult an existing Surface patchset. We use Windows on the same SP11 as the hardware oracle, preserve useful upstream Qualcomm infrastructure, and independently derive the Surface-specific camera topology, power sequencing, sensor behaviour, CSI configuration and image pipeline.

## Current target hardware

| Function | Windows identity | Silicon | Surface subsystem |
| --- | --- | --- | --- |
| Front RGB | `ACPI\\SONY0681` | Sony IMX681 | `MSHW0490` |
| Rear RGB | `ACPI\\OVTID858` | OmniVision OV13858 | `MSHW0491` |
| Front IR / Hello | `ACPI\\SMO55F0` | ST VD55G0 | `MSHW0492` |
| Camera platform | `ACPI\\QCOM0C32` | Qualcomm Spectra 695 / X1E camera stack | `MSHW0495` |

## Current milestone

Front IMX681 now has a consumed bounded Linux live PASS through **R27**, backed by combined Windows AWB + Tintless/LSC differential authority through R27 and deterministic offline composition authority.

The final bounded chain is now closed through **R27**. GL G1..G24 publisher, GM R5..R27 producer and GN 27-frame transport passed offline, and **GO completed a consumed one-shot 27-frame Linux live PASS with clean Golden return and candidate retirement**.

The project has now pivoted to continuous delayed sensor-control feedback. GP closed GO timing authority, GQ added a fail-closed two-slot continuous scheduler, GR integrated it into the live-capable helper, and **GS then passed a consumed live shadow run across all R27 boundaries**. GS kept physical writes bounded to G1..G3 while proving 23 later shadow releases. The next step is a tiny identical-control repeated-write gate before allowing changed post-G3 controls.

Rear OV13858 E002k-D R3 remains accepted with 16/16 normal frames and clean Golden return. Front IR / VD55G0 remains unproven on Linux.

SP11 is on protected FullIO v19c Golden. Bounded success does **not** yet claim unrestricted continuous AEC or full Windows camera parity. See [current handoff](HANDOFF.md).
## Start here

If resuming after a new chat/session, read in this order:

1. [`CONTINUE.md`](CONTINUE.md)
2. [`AGENTS.md`](AGENTS.md)
3. [`PROJECT_STATE.md`](PROJECT_STATE.md)
4. [`state/project.yaml`](state/project.yaml)
5. latest entry under [`experiments/`](experiments/)

Then run:

```bash
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
./tools/project-status.sh
```

The repository and live machine state, not visible chat chronology, are the durable continuity source.

## Ground rules

- Keep the deployed audio/FullIO v19c Golden untouched while camera experiments are unproven.
- Reuse upstream X1E80100 CAMSS/CCI/V4L2 infrastructure where technically correct.
- Surface-specific topology and sensor behaviour are evidence-derived from Windows on the actual machine.
- One major unknown per experiment.
- Every candidate gets an `E###` identity, evidence log, hashes and rollback path.
- Do not commit Microsoft/Qualcomm proprietary binaries. Store filenames, hashes, decoded observations and reproducible extraction instructions only.

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for the experiment/checkpoint protocol.
