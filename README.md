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

Front IMX681 E003h is now the active **Windows-parity architecture** gate. Same-machine Windows proves **IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1**, CSID1 IPP RAW10 VC0 with 3840x2160 crop/measurement, and a VFE1 ISP pipeline whose FULL output is 2560x1440 Y/C with DS4/DS16 and statistics clients. Lifecycle placement is closed: start is **ISP -> MIPI/CSIPHY -> sensor**, while stop completes ISP teardown first and then schedules sensor-off and MIPI-stop with no fixed relative order. Static-only `0011` now gives X1E a dedicated CSID1 IPP/VC0 path and reproduces the Windows IPP register state in a clean Golden-vermagic build; it is not deployed. The Windows VFE1 FULL surface is also now mechanically identified as **2560x1440 QC10C/TP10 UBWC**, one contiguous `Y_META -> Y_TP10 -> C_META -> C_TP10` allocation. The Windows IFE startup byte corpus and DMI payloads are now complete, and native execution is mechanically pinned to **RT_CDM1 v2.1 at `0x0ac26000`**, FIFO0, with dedicated firmware GSI `319` -> Linux **`GIC_SPI 287`**. Static `0013` gives Denali an inert exact RT_CDM1 MMIO/IRQ resource representation, and static `0014` adds a disabled-at-probe IRQ handler plus caller-sized 32-bit coherent-DMA arena while still exposing no IRQ-arm, configuration, reset or FIFO-submit path. The same-machine Windows RT_CDM1 initialization/start/commit/stop ordering is now statically pinned, and the optional `CGC_CFG=7` path is mechanically closed as not-taken by the zero-initialized Windows CDM object. An exact mapping/alias/helper/parser census finds no in-binary CPU write path for live `FE_CFG`/`FIFO0_CFG`, and a two-cycle same-machine oracle now closes their positive timing: after a proven `0x80000000` powered-off interval, both exact literals are already restored at RT_CDM1 map-return before the front CDM object's first MMIO write and survive reset/core-config unchanged. Linux must validate them read-only, never synthesize them. Stream stop is separately closed from later session-delete/platform power collapse: `0x805` only masks CDM IRQ0 after CSID/IFE stop, while `0x80e` later closes software ownership and reference-counts CSID/IFE power off; no `CORE_EN=0` or reset write is imported. Generic Qualcomm defaults remain non-authoritative; only after those same-machine gaps close may the captured command/data corpus be integrated with an armed VFE1 PIX/ISP path. Linux VFE680's current RDI-only path is **not** the parity target; RDI may be used only as a clearly-labelled diagnostic. No Linux front-frame result is claimed yet. See [`docs/runbooks/2026-08-28-e003h-windows-parity-static.md`](docs/runbooks/2026-08-28-e003h-windows-parity-static.md).

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
