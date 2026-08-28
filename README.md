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

Front IMX681 E003g route resolution is complete. A two-pass same-machine Windows/KD oracle proves the active front path is **IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1**. CSID1 IPP receives RAW10 VC0 and the Windows ISP path measures/crops the established 3840x2640 sensor mode to 3840x2160. Linux VFE680 currently supports RDI output only, so the next experiment is a bounded **CSID1 -> VFE1 RDI** transport build; no Linux front-frame result is claimed yet. See [`docs/runbooks/2026-08-28-e003g-route-resolved.md`](docs/runbooks/2026-08-28-e003g-route-resolved.md).

## Start here

If resuming after a new chat/session, read in this order:

1. [`CONTINUE.md`](CONTINUE.md)
2. [`AGENTS.md`](AGENTS.md)
3. [`PROJECT_STATE.md`](PROJECT_STATE.md)
4. [`state/project.yaml`](state/project.yaml)
5. latest entry under [`experiments/`](experiments/)

Then run:

```bash
./tools/project-status.sh
```

The repository is deliberately structured so the instruction **“continue the camera work on SP11”** is enough to recover the project state without reconstructing prior chat context.

## Ground rules

- Keep the deployed audio/FullIO v19c Golden untouched while camera experiments are unproven.
- Reuse upstream X1E80100 CAMSS/CCI/V4L2 infrastructure where technically correct.
- Surface-specific topology and sensor behaviour are evidence-derived from Windows on the actual machine.
- One major unknown per experiment.
- Every candidate gets an `E###` identity, evidence log, hashes and rollback path.
- Do not commit Microsoft/Qualcomm proprietary binaries. Store filenames, hashes, decoded observations and reproducible extraction instructions only.

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for the experiment/checkpoint protocol.
