# SP11X1ECamera

> **Current frontier — 2026-09-17 / E004fo consumed, E004fp prepared:** Front IR VD55G0 remains live-proven on Linux through stock libcamera and 16/16 processed monochrome frames. E004fn proved the normal Windows 700 mA LED1 request and selector-0 hardware/level/active-high trigger sequence. E004fo then consumed one Windows identity on an idle KD parser error; recovered diagnostics exposed incorrect PRE-byte and POST-register observer assumptions, so none of that boot is accepted as register-level authority. The observer is mechanically corrected under fresh identity E004fp. Native illumination remains OFF until a clean fresh Windows PMIC trace and later sensor exposure/pulse-policy gates are closed.


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

The project has closed bounded rear/front RGB production authority while the brighter-scene post-G3 feedback proof remains separately parked. **Front IR has since advanced through native Linux transport, stock-libcamera capture, controls and 16/16 processed monochrome frames (E004fe); E004fn proves the normal Windows flash request sequence.** The active frontier is safe register-level PMIC/pulse authority before any native IR-emitter activation.

Rear OV13858 E002k-D R3 remains accepted with 16/16 normal frames and clean Golden return. Front IR / VD55G0 capture is now proven on Linux; illumination, longer lifecycle/desktop integration and final upstream consolidation remain open.

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
