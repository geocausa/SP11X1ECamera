## E011AG full real-provider startup integration — OFFLINE / ARM64 BUILD PASS

The four-packet path now runs 34 actual provider/contract includes, actual recursive E008o validation, actual E008l layout and complete E007y materialization. GCC+Clang ASan/UBSan each pass 1,872 assertions and 32 negatives; all 2,268 register positions and 46 DMI identities match corpus shape. Source BPC retains all21 present words; four LSC/four GTM/three GIC payloads propagate exactly. New composer validates the full register-family union, rejects aliasing/exposed/submitted/malformed arenas, and clears all accepted-domain incomplete output. Caller request IDs100/101/102/103 are explicit fixtures, separate from source requests0/1/2. A fresh isolated ARM64 CAMSS W=1 build passes zero warnings; composer/recipe retained, module SHA6ed7738dcc2ba1a197e162e8b4cff1ca5fb98492ed90bde98703799ce9f4d488, not installed/loaded.

This closes integration mechanics, NOT complete source-produced startup bases. Neutral scalar/statistics inputs remain host fixtures (11/27/11/2 mismatched semantic words by phase); previously closed E011X/E010Z/E011A–R/E011T–W provenance gates are NOT reopened. Normal BF ROI still needs its accepted request-specific adjustment through the integrated DMI path. Cold BF gamma is disabled/selector2 absent, while generic validation needs an explicitly completed unused gamma state; host completion is not a Windows producer policy. Static flat GTM replay now proves grid independence and needs no private normal-TMC domain file. NEXT lower existing source-owned scalar/statistics handoffs into four portable bases, then full register/DMI parity. Independent WM16 same-generation IRQ/DMA/IOMMU retirement remains OPEN; native rear ISP DENIED. Idle Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 is unchanged; no camera, boot, sleep, MMIO or submission. See [E011AG](experiments/E004-front-ir-vd55g0/e011ag-rear-full-provider-startup-integration/README.md), RESULT, INTEGRATION-SAFE and BUILD-SAFE. Do not replay the consumed one-use build.

# SP11X1ECamera

> **Current rear ISP frontier — 2026-09-30 / E011AF live source binding PASS:** Startup AEC/context inputs now bind to the actual BPC shared object and source-produced outputs;705 Windows4K handles and exact startup/C packet comparisons pass. Remaining work is complete E008o packet composition and independent WM16 safe retirement. SP11 is idle on protected Golden. See [current handoff](HANDOFF.md).

> **Earlier IR checkpoint — 2026-09-17 / E004fp PMIC trace PASS, E004fq timing authority next:** Front IR VD55G0 remains live-proven on Linux through stock libcamera and 16/16 processed monochrome frames. E004fp completed one fresh bounded Windows IR preview with a clean corrected PMIC observer: seven paired read/modify/write records all returned success, trigger registers `ee4a..ee4d` were observed, LED1 sources 1 and 4 reached low-three-bit value `0x05` (the E004fl hardware/level/active-high encoding), and common `ee67` bit 0 was live-proven `1 -> 0`. No `ee3e..ee41` timer access appeared in this 12-frame session; that bounded absence does not prove the timer is globally unused. SP11 returned cleanly to protected Golden. Native illumination remains OFF while actual VD55G0 exposure/strobe timing and any required PMIC timer policy are closed.


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

The project has closed bounded rear/front RGB production authority while the brighter-scene post-G3 feedback proof remains separately parked. **Front IR has since advanced through native Linux transport, stock-libcamera capture, controls and 16/16 processed monochrome frames (E004fe); E004fp now live-proves the normal Windows PMIC trigger/common-register writes.** The active frontier is actual sensor exposure/strobe-envelope and timeout authority before any native IR-emitter activation.

Rear OV13858 E002k-D R3 remains accepted with 16/16 normal frames and clean Golden return. Front IR / VD55G0 capture is now proven on Linux; illumination, longer lifecycle/desktop integration and final upstream consolidation remain open.

SP11 is on protected FullIO v19c Golden. Bounded success does **not** yet claim unrestricted continuous AEC or full Windows camera parity. See [current handoff](HANDOFF.md).
## Start here

If resuming after a new chat/session, read in this order:

1. [`CONTINUE.md`](CONTINUE.md)
2. [`AGENTS.md`](AGENTS.md)
3. [`docs/CAMERA-STACK-PORT-MAP.md`](docs/CAMERA-STACK-PORT-MAP.md) — pinned Windows behaviour → native Linux L0–L6 ownership map; run `python3 tools/verify-camera-stack-port-map.py` before redirecting engineering work.
4. [`PROJECT_STATE.md`](PROJECT_STATE.md)
5. [`state/project.yaml`](state/project.yaml)
6. latest entry under [`experiments/`](experiments/)

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
