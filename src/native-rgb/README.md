# Native RGB driver integration

The approved architecture also includes [libcamera](libcamera/README.md).
The kernel-only builder below remains the hardware source build; it does not
implement the libcamera pipeline.

This is the current kernel-driver workstream for front IMX681 and rear OV13858.
Read [the engineering audit](../../docs/NATIVE-RGB-ENGINEERING-AUDIT-20261007.md)
for scope, evidence, architectural limits and delivery gates.

## What this builds

- Maintained front CAMSS, including the existing E004IK–IP NV12 negotiation and
  memory-layout planners and the physically exercised QC10C mapped-SG guard.
- 52 rear source fragments with original paths and hashes, including E011I's
  source-only post-stop reclaim candidate and E011Z's startup adaptive binder.
- IMX681 with measured read-only timing controls and OV13858 with the actual
  SP11 board-power/runtime-PM source, rebuilt with W=1 and -Werror.

Hardware identity 03 verified the front timing ABI during 240 sequential RAW
frames, then captured 120 rear RAW frames. All STREAMOFF checks, sensor standby,
neutral routing and protected Golden asset hashes passed. This establishes
sensor/RDI transport, not native processed output or Windows image-quality parity.
See docs/NATIVE-RGB-TIMING-03-20261007.json.

It builds no custom userspace product runtime. Python and compiler commands here
are developer tooling. The front bounded runner remains diagnostic; rear hardware ISP runtime remains denied; current front linear NV12 evidence
is described in the engineering audit. These modules are **not a completed
camera stack or an installation authorization**.

## Build

Use a new output path outside the repository:

```sh
python3 src/native-rgb/build.py \
  --out /home/geoca/Documents/SP11-PROJECT/02-kernel/native-rgb-NEW-IDENTITY \
  --kernel-source /home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src \
  --kernel-output /home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826 \
  --jobs 4
```

Omit the two kernel arguments to stage and audit sources without compilation.
Existing output directories are refused. Source hashes are checked before
creating output. Only manifest-listed kernel sources are admitted.

The builder applies the reviewed retained NV12/DMA overlays, copies the original
rear fragments, and applies the rear integration patch with zero fuzz.
E011I replaces the earlier E008K runner without adding a runtime caller.
E008T's BF composer is adapted from mock-only packet/bootstrap types to the real
E008O packet/set types. All packet identities are admitted before BF mutation;
ready or sealed sets are refused. This does not close BF ROI adjustment/parity.
E011Z is included after the real E008O definitions; its unused binder declaration
is annotated only in staging so W=1 can check it in the actual kernel translation
unit. Its nonadaptive semantic inputs are still required.

E004IO's added DMA include temporarily moves around a context line while applying
the pinned rear patch and is restored before compiling. Every final source digest
is written to source-manifest.json. The build produces build-result.json with
module digests and vermagic. Absolute build/debug paths may change module bytes;
the reproducibility guarantee here is deterministic source composition.

```sh
python3 src/native-rgb/test_composition.py
```

The checks cover changed/outside source rejection, identical independently staged
sources, refusal to overwrite an existing candidate, include integration and
retained DMA/runtime gates. Kbuild separately checks actual ARM64 types, calls
and module dependencies.


## Rear source validation

After a fresh kernel source build, run the hosted actual allocator, command-layout,
validator and scalar-binder checks against its staged sources:

```sh
python3 src/native-rgb/test-rear-prepared-commands.py \
  --staged /absolute/fresh-build/camss \
  --report /absolute/fresh-build/hosted-handoff.json
```

GCC and Clang use address/undefined-behavior sanitizers. Semantic materialization
and hardware callbacks are explicit mocks; this checks ownership, packet separation,
atomic failure cleanup and validation, not complete register semantics or DMA.
The private scalar verifier separately links actual built libipa with the actual
C kernel binder and E006Z register packer. Its inputs stay on SP11 and its report
contains only aggregate counts. Neither test authorizes a hardware submission.

## Current next implementation — rear first

User2026-10-07 deferred front calibration until rear finished. Fresh rear-only
Windows screen/light-OFF baseline PASS; see rear-windows-reference/README.md
and docs/NATIVE-RGB-WINDOWS-REAR-SCREEN-01-20261007.json. Optical originals
remain PRIVATE on same SP11; healthy upper-screen ROI registration still needed.

Front linear NV12, continuous queue, metadata/typed parameters, standard
pipeline/IPA and full-rate manual request controls/lifecycle are physically
qualified in the current audit. Front meter/AE/AWB/IQ remains incomplete.

The prepared-command consumer and integer scalar binding are now source-qualified.
Each rear phase is materialized once into an independent arena; the runner validates
and consumes those outputs without rebuilding them. The existing libipa scalar
producer supplies an internal 208-byte envelope, validated atomically against all
four kernel packet identities. This is not a published ABI or a connected rear
runtime. See docs/NATIVE-RGB-REAR-COMMAND-HANDOFF-20261007.json and
 docs/NATIVE-RGB-REAR-SCALAR-BINDING-20261007.json for the exact evidence limits.

Next compose the remaining geometry, statistics, BPC/ABF, BF and DMI inputs into
four complete packet-isolated semantic states. Reuse the precise composition-gaps
table in the audit and52 gathered fragments, measured OV13858 RAW/power and
validated NV12 planners. Physical exact-generation completion, serialized owner
and shutdown evidence precede any reclaim/activation; rear ISP runtime remains
denied until those contracts are independently established.

Qualcomm VFE680 uses external CSID completion and does not advertise global
reset. Do not invent a separate-VFE-IRQ or reset prerequisite. Do not revisit
optional OEM metadata/names or promote compilation to processed-frame proof.
