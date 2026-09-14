# E004cr — compile-only external CPZ sample provider contract

## Result

**PASS: the E004cq external protected-sample authority is now encoded at the CAMSS boundary as a compile-only lifecycle contract. The contract preserves opaque identity, generic backing, worker-only protected ownership, HLOS CPU exclusion, trusted import, worker-held lifetime, detach-before-reclaim, reclaim-before-free, no camera-HW ownership requirement and no HLOS fallback. The resulting CAMSS module has byte-identical executable `.text` to the untouched baseline.**

This checkpoint adds no runtime implementation and selects no concrete VMID, heap, ownership service, FastRPC operation, DSP process, context bank, ioctl, DT property or secure backend.

## Why a second provider contract is necessary

E004cp encoded the whole protected-camera provider gate. At that point the external sample was intentionally unresolved.

E004cq then proved a separate protected external object can use a generic mem-buf-aware backing with worker-only protected ownership and can be reclaimed safely after the trusted worker detaches.

E004cr turns that proof into a lifecycle shape that future code must satisfy without prematurely binding a backend.

## External sample capability set

The compile-only provider requires ten independent capabilities:

1. `OPAQUE_IDENTITY` — the sample keeps its stable 16-byte logical identity rather than treating an fd as identity.
2. `GENERIC_BACKING` — external backing is not a CAMSS hardware target by construction.
3. `WORKER_ONLY_OWNERSHIP` — active protected ownership can exclude camera hardware as well as HLOS.
4. `HLOS_CPU_EXCLUDED` — no ordinary HLOS CPU image mapping while protection is active.
5. `TRUSTED_IMPORT` — the trusted worker can import/map the object.
6. `WORKER_REF_HELD` — worker mapping keeps the backing alive even if a transport handle closes.
7. `DETACH_BEFORE_RECLAIM` — trusted mapping is removed before ownership is returned.
8. `RECLAIM_BEFORE_FREE` — backing cannot be released while protected ownership remains active.
9. `NO_CAMERA_HW_OWNER` — external sample is not silently collapsed into the internal camera target.
10. `NO_HLOS_FALLBACK` — no memcpy or ordinary CPU fallback path is permitted.

All ten form:

`CAMSS_CPZ_EXTERNAL_REQUIRED_CAPS = 0x3ff`.

## Lifecycle phases

The external provider state machine is explicitly ordered:

`DETACHED`
→ `IDENTITY_BOUND`
→ `BACKING_READY`
→ `WORKER_OWNED`
→ `WORKER_IMPORTED`
→ `PAYLOAD_READY`
→ `WORKER_DETACHING`
→ `RECLAIMING`
→ `RECLAIMED`
→ `RELEASING`.

The key parity invariants are visible in the structure itself:

- `normal_hlos_cpu_visible` must remain false while protected ownership is active;
- `camera_hw_owner_required` must remain false for the external object;
- `worker_detached_before_reclaim` and `ownership_reclaimed_before_free` are separate checks;
- `hlos_transfer_fallback_allowed` is represented explicitly so a future backend cannot silently enable it.

## Callback boundary

The provider operations are declarations only:

- bind logical identity;
- prepare generic backing;
- activate protected worker ownership;
- import trusted worker mapping;
- mark payload extents/offset ready;
- detach worker mapping;
- reclaim ownership;
- release backing.

No callback is invoked by production code in this experiment.

## Zero-runtime build proof

Production preimage remains:

- `camss-video.c` SHA-256 `2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4`;
- `camss-video.h` SHA-256 `69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982`.

Both untouched baseline and compile-only scaffold build against Golden runtime-v4 headers with vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`.

Executable `.text` is byte-identical:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`.

No module was installed or loaded.

## What remains deliberately absent

The contract contains no implementation of:

- protected dma-buf allocation;
- ownership lend/reclaim;
- secure FastRPC mapping;
- process-type selection;
- context-bank selection;
- concrete owner IDs or permissions;
- user ioctl or runtime selector;
- DT parsing;
- QTEE/QSEE/Gunyah/SCM calls.

Thus the architecture is encoded without creating an accidental partially-live secure path.

## Safety boundary

Golden FullIO v19c stayed active. No module load, protected ownership change, DSP process creation, FastRPC operation, camera runtime or SecureISP runtime occurred.

## Next gate

**E004cs — Golden CPZ host-port source delta, static/compile-first.**

Now that both internal and external protected objects have complete contracts, determine the minimum source delta needed to bring the already-proven downstream host primitives into the Golden 7.1.5 tree without activating them:

1. mem-buf-aware dma-heap/exporter surface;
2. remote process-type/session-info ABI;
3. PD-typed secure context-bank selection;
4. ownership query used to classify imported dma-bufs as protected;
5. provider-facing wrappers that can be compiled but remain unreachable without an explicit future authorization gate.

Do not add live DT policy, create a CPZ process or perform an ownership transition.
