# E004bm — compile-only CAMSS protected-sample scaffold

## Result

**PASS: a protected-sample API/lifetime contract now compiles against the current SP11 CAMSS source while adding zero executable runtime behavior.**

This checkpoint is intentionally non-operational. It introduces no backend, no feature selector, no control, no ioctl, no SCM call, no protected-memory assignment and no QCOMTEE dependency.

## What was added

A new header, `camss-protected-sample.h`, defines only the future object contract:

- a stable 16-byte sample identifier;
- up to three protected device-visible addresses;
- per-plane sizes;
- an opaque backend handle;
- a prepared state;
- `prepare` / `release` operation signatures.

It also defines backing type names for normal and protected samples.

There is deliberately **no implementation object** of those ops and no way to select protected backing.

## Compile-only integration hook

`camss-video.c` includes the new header and invokes only:

`camss_protected_sample_compile_contract()`

That inline helper contains compile-time `BUILD_BUG_ON` assertions and no executable operation.

No existing VB2, DMA, VFE, stream, sensor or queue behavior was modified.

## Mechanical no-runtime proof

Two modules were built from the same current CAMSS source snapshot:

1. unmodified baseline;
2. scaffold source.

Both build successfully with the Golden kernel headers and have the same vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

The complete module files differ because source/debug metadata changed, but their extracted **`.text` sections have the exact same SHA-256**:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`

and compare byte-for-byte identical.

That proves this checkpoint adds no executable runtime code.

## Safety checks

The scaffold source was scanned for implementation-sensitive symbols including:

- Qualcomm SCM;
- QCOMTEE;
- memory assignment;
- VMID handling;
- secure DMA heap allocation.

The scan is empty.

The current production CAMSS source hashes remain unchanged after the build.

No camera/SecureISP modules are loaded and no media/video nodes appeared.

No module produced here was installed or loaded.

## Why this shape is useful

E004bl established that protected-sample lifetime belongs above VFE, at the CAMSS video/VB2 boundary.

E004bm makes that contract compiler-visible without committing prematurely to the eventual secure-memory primitive.

Future implementation work can now fill in the backend behind a stable API while preserving these constraints:

- ordinary VB2/SG capture remains unchanged;
- protected samples own a separate identifier and backing lifetime;
- VFE remains only the device-address consumer;
- protected sample lifetime remains separate from secure-lane ownership;
- SecureISP's internal CP_CAMERA allocation remains separate again.

## Files

- `CAMSS-PROTECTED-SAMPLE-SCAFFOLD.patch` — minimal patch against the current production CAMSS source.
- `scaffold/camss-protected-sample.h` — generated contract header.
- `make-scaffold.py` — deterministic scaffold generator.
- `evidence/BASELINE-BUILD.log`
- `evidence/SCAFFOLD-BUILD.log`
- `evidence/SCAFFOLD-GENERATE.txt`
- `evidence/BUILD-AND-NO-RUNTIME-DIFF.txt`
- `evidence/POST-BUILD-STATE.txt`

## Next gate

Extend the **compile-only** scaffold to model the three lifecycle seams identified in E004bl:

1. queue-policy selection;
2. per-buffer prepare/release;
3. stream-level secure-lane acquire/release as a separate interface.

Keep all implementations unavailable and fail-closed. The next checkpoint should still have no secure backend, no runtime activation route and no module load.
