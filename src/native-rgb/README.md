# Native RGB driver integration

This is the current kernel-driver workstream for front IMX681 and rear OV13858.
Read [the engineering audit](../../docs/NATIVE-RGB-ENGINEERING-AUDIT-20261007.md)
for scope, evidence, architectural limits and delivery gates.

## What this builds

- Maintained front CAMSS, including the existing E004IK–IP NV12 negotiation and
  memory-layout planners and the physically exercised QC10C mapped-SG guard.
- 52 rear source fragments with original paths and hashes, including E011I's
  source-only post-stop reclaim candidate and E011Z's startup adaptive binder.
- IMX681 and OV13858 kernel modules rebuilt from source.

It builds no custom userspace product runtime. Python and compiler commands here
are developer tooling. The front bounded runner remains diagnostic; rear and
linear NV12 runtime gates remain denied. These modules are **not a completed
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

## Next implementation

Front hardware linear NV12, with a source-justified stopped-state compression
transition and private optical proof. Reuse the planners; do not rediscover them.
In parallel within this same workstream, inventory the precise missing rear
four-packet semantic producers and correlate CSID-delivered completion with
consumed IOVA/generation before enabling any reclaim or rear runtime.

Qualcomm VFE680 uses external CSID completion and does not advertise global
reset. Do not invent a separate-VFE-IRQ or reset prerequisite. Completion,
ownership and shutdown still require SP11 hardware evidence.
