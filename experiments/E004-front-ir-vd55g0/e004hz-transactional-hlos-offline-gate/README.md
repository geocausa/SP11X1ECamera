# E004hz — offline all-or-nothing commit boundary around original native HLOS C stream

**PASS on unprivileged real SP11 ARM64 protected Golden Linux, 2026-09-20.**
No camera, PMIC, SPMI, emitter, BIOS, Windows, KD, PAM, login, face
recognition, installation, or firmware operations.

E004hi's original maintained HLOS C streaming transport returns provisional
processed frames *before* it can validate a final DONE marker, stdout EOF,
or child exit zero. A future caller could accidentally use a provisional
frame even if the rest of the stream fails. E004hz adds the separately named,
UNINSTALLED offline-only src/sp11-camera-hlos-worker/sp11-offline-transaction.py
wrapper which deliberately returns **no processed outputs at all** to its
caller until the unchanged original E004hi stream finishes successfully.
It requires a concrete tuple of exactly 1..16 immutable 644x604 neutral
NV12 frames, prevalidates all frames, and runs the actual existing HLOS C
streaming executable in a disposable /tmp directory. It collects outputs
internally; on a later child failure, incorrect/missing DONE, extra output,
nonzero exit, bad frame, deadline or missing executable it returns a
content-free TransactionFault, not a partial tuple. It never retries or
rearms the original one-shot stream.

The already-existing native C/stream Python client and maintained eight-file
HLOS pixel core were NOT modified. Existing E004hi hashes are checked
before this experiment runs. The new wrapper is neither a trusted
authenticator nor an independent watchdog. It holds transient processed
pixels in ordinary Python bytes/heap memory; dropping the references
is NOT secure erasure, and the calling process owns its source/return
buffers. No fresh camera provenance, consent, NIR, liveness, biometric
identity, optical measurements or fault-independent emitter shutoff is
established by this offline IPC improvement.

## Executed synthetic ARM64 verification

- Compiled actual original maintained C core + unchanged native streaming
  sidecar and original one-shot binary into a disposable /tmp directory.
- Distinct synthetic neutral NV12 luma values 40 and 90 processed with
  original one-shot native HLOS core. Actual original stream path then
  produced EXACT identical per-frame bytes with count 1, 2, 8 and 16.
- Four adversarial user-owned disposable child programs deliver a valid
  first provisional OUT1 frame followed by a *late failed second frame*,
  wrong DONE index, correct DONE with extra stdout byte, or nonzero process
  exit. All fail without returning provisional data to caller.
- Eight malformed input container/count/type/shape/chroma cases and two
  missing binary/invalid deadline cases also fail, total **14 fail-closed
  negative scenarios**. No frames, hashes, embeddings or identity data
  are retained in result JSON. Source/evidence digest validation passes.

Reproduce on protected Golden SP11:

    python3 experiments/E004-front-ir-vd55g0/e004hz-transactional-hlos-offline-gate/verify_transaction.py
    python3 experiments/E004-front-ir-vd55g0/e004hz-transactional-hlos-offline-gate/verify_result.py

A session is NOT safe to use for unlocking a desktop merely because the
transaction committed. Next production work requires actual authorized
sensor provenance, appropriate biometric/privacy design, independent
physical emitter cutoff/current/irradiance/pulse evidence, and repeated
real-hardware reliability tests before any native IR emitter or PAM use.
