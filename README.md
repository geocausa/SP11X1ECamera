# SP11X1ECamera

**Active workspace:** `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean` on
`experiment/e004-front-ir-vd55g0`; see [machine/workspace map](docs/MACHINE_MAP.md).

**Current engineering checkpoint — 2026-10-02 / E011CJ:** original post-attachment
baseline reset passes24 cases, including12 explicit poisoned-field fixtures.
Exact entire-inner/arena deltas check three clears,51 scalar store chunks and
an internal buffer link per case. Source-only; Golden unchanged. Next E011CK
qualifies remaining source producers and CRT state before final publication/return.
Native rear hardware ISP runtime remains denied pending remaining initialization
and DMA-retirement gates. See [current continuation](CONTINUE.md) and
[E011CJ result](experiments/E004-front-ir-vd55g0/e011cj-baseline-state-reset/RESULT.json).

Current product priority is a clean, controllable front/back native Linux
baseline; optional AI/effects/HDR/catalogue are deferred. Protected IR/Hello
records are retained historical work.

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

## Proven hardware milestones and limits

- E004ne passed bounded front 1080p/rear 4K RGB fallback sessions near 30 fps,
  controls, switching and neutral shutdown. It does not establish Windows ISP
  image-quality parity or an everyday default service.
- E003i front tests produced 27 native hardware VFE1 PIX QC10C frames.
  Windows-equivalent colour/detail and linear NV12 remain unproven.
- Rear native hardware ISP processed 4K capture remains unproven and
  runtime-denied; source qualification and safe DMA retirement remain necessary.
- Earlier IR transport/libcamera/processed-pattern evidence is retained.
  Native illumination remains off under its separate physical-evidence gates.

Golden FullIO v19c remains protected. Historical summaries below do not
supersede the latest continuation/state.

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

## Historical source updates

The following recorded updates are preserved for context; their NEXT statements
are superseded by the latest continuation and top-level project state.

## E011AI clean neutral scalar full integration — PRIVATE PARITY / ARM64 BUILD PASS

Recovered the original E011X input trace privately from SP11 Windows with exact trace/holder/corpus hashes; Windows NTFS was read-only and is unmounted. A strict parser verifies all 32 events/eight samples, coherent PDPC/WB AWB inputs and the cold/request1/request2/request3-hold ordering. New portable C11 L4 arithmetic is independent of Windows; both sanitizer compilers match 1,038 original ARM64 arithmetic cases / 10,380 scalar fields privately. PDPC near-zero denominator correctly yields minimum128, not unity4096. Only the clean C-produced results bind to L2, with source IDs0/1/2 and schedule[0,1,2,2]; caller IDs remain separate.

The actual E011AG/E011AH full composer matches all26 present scalar register instances (8/8/8/2). Remaining semantic differences are reduced from51 to25, by phase3/19/3/0, exclusively AEC_BE/AWB_BG/RS statistics. BF ROI/gamma, BPC and LSC/GTM/GIC comparisons remain exact. GCC+Clang ASan/UBSan each pass509,118 assertions with32 composition,61 AF,69 scalar binder and69 scalar producer negatives. New isolated integer-only ARM64 CAMSS W=1 build passes zero warnings; moduleSHAbe35b2da4905b63549a4fef65f89f0299f46f4bc79404c7a720a278648113c5b, not installed/loaded/called; no user-space float producer enters the kernel. Existing source/live provenance gates are not reopened.

NEXT lower the already established statistics geometry/threshold/weight/black-level/RS handoffs into portable bases and require full private parity. Cold gamma remains explicit unused host-only completion. Optional WB normalization/other Bayer policies are outside this bounded rear slice; no full AE/AWB/AF algorithm port is claimed. Complete source-produced E008o startup composition and independent WM16 safe retirement remainOPEN; native rear ISP DENIED. Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 stays idle; no camera/boot/sleep/MMIO/submission. See [E011AI](experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/README.md), SCALAR-SAFE, INTEGRATION-SAFE, BUILD-SAFE and RESULT. Recovered original authority is /home/geoca/Documents/SP11-PROJECT/06-camera/private/E011X-source-recovered; keep it private on SP11. Never rerun the consumed one-use builder.

## E011AH request AF/BF ROI full integration — PRIVATE PARITY / ARM64 BUILD PASS

The accepted source AF rectangle/BAF adjustment now runs through the actual E011AG four-packet composer. A new integer-only detached handoff validates all three normal request/phase tags and geometry before mutation; packet0, ROI IDs/flags/gamma and all other fields are preserved. GCC+Clang ASan/UBSan each pass508,760 assertions,32 inherited negatives and61 new AF negatives. All16,385 bounded one-fifth dimensions and18,157 odd/even maps agree with the original float source helper. Private full-path BF selector1 matches300/300 bytes in all4 phases; normal selector2 matches128/128 in all3 phases. Neutral first-zoom control remains250/300. New isolated ARM64 W=1 build haszero warnings; moduleSHA9f1de3bb49cbc47b8a8a8b52e8d8a59c97ea511781cd98107e0006aaa6ccf760, binder/recipe retained, not installed/loaded/called.

This closes the bounded request-specific BF ROI propagation/parity seam, not an AF algorithm or newly tagged live AF-to-RT-CDM identity. Replay uses existing independently measured E009e first-normal zoom0x3f7f3f0f, then1.0; upstream zoom calculation remains unproven. Neutral scalar/statistics bases still have11/27/11/2 semantic register differences by phase and need source-owned producer lowering; prior E011X/E010Z/E011A–R/E011T–W provenance remains closed. Cold gamma remains an explicit unused host completion (enable0, selector2 absent). Complete source-produced E008o composition and independent WM16 same-generation IRQ/DMA/IOMMU safe retirement remainOPEN; native rear ISP DENIED. Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 stayed idle, no camera/boot/sleep/MMIO/submission. See [E011AH](experiments/E004-front-ir-vd55g0/e011ah-rear-request-af-roi-full-integration/README.md), RESULT, INTEGRATION-SAFE and BUILD-SAFE. Never rerun the consumed one-use builder.

## E011AG full real-provider startup integration — OFFLINE / ARM64 BUILD PASS

The four-packet path now runs 34 actual provider/contract includes, actual recursive E008o validation, actual E008l layout and complete E007y materialization. GCC+Clang ASan/UBSan each pass 1,872 assertions and 32 negatives; all 2,268 register positions and 46 DMI identities match corpus shape. Source BPC retains all21 present words; four LSC/four GTM/three GIC payloads propagate exactly. New composer validates the full register-family union, rejects aliasing/exposed/submitted/malformed arenas, and clears all accepted-domain incomplete output. Caller request IDs100/101/102/103 are explicit fixtures, separate from source requests0/1/2. A fresh isolated ARM64 CAMSS W=1 build passes zero warnings; composer/recipe retained, module SHA6ed7738dcc2ba1a197e162e8b4cff1ca5fb98492ed90bde98703799ce9f4d488, not installed/loaded.

This closes integration mechanics, NOT complete source-produced startup bases. Neutral scalar/statistics inputs remain host fixtures (11/27/11/2 mismatched semantic words by phase); previously closed E011X/E010Z/E011A–R/E011T–W provenance gates are NOT reopened. Normal BF ROI still needs its accepted request-specific adjustment through the integrated DMI path. Cold BF gamma is disabled/selector2 absent, while generic validation needs an explicitly completed unused gamma state; host completion is not a Windows producer policy. Static flat GTM replay now proves grid independence and needs no private normal-TMC domain file. NEXT lower existing source-owned scalar/statistics handoffs into four portable bases, then full register/DMI parity. Independent WM16 same-generation IRQ/DMA/IOMMU retirement remains OPEN; native rear ISP DENIED. Idle Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534 is unchanged; no camera, boot, sleep, MMIO or submission. See [E011AG](experiments/E004-front-ir-vd55g0/e011ag-rear-full-provider-startup-integration/README.md), RESULT, INTEGRATION-SAFE and BUILD-SAFE. Do not replay the consumed one-use build.
