# E004cu — Golden protected dma-buf ownership state/backing wrapper

## Result

**PASS: a protected ownership/lifetime wrapper can be compiled directly around Golden's existing system dma-heap without replacing its SG allocator. The staged exporter blocks HLOS CPU mappings while a sample is remotely owned, holds an extra dma-buf reference across the protected lifetime, supports the separate external `{CP_CDSP}` and internal `{CP_CDSP, CP_CAMERA}` owner sets, and fails closed into a retained `POISONED` state when ownership becomes uncertain. Heap registration is removed, so none of this is live.**

This gate is compile-only. No protected allocation, SCM assignment, FastRPC call, CPZ process, camera stream or module load occurred.

## 1. Reuse Golden's system-heap backing, add ownership state above it

E004ct removed the physical-contiguity blocker: Golden's existing MP/HYP_ASSIGN protocol can describe a bounded SG table.

E004cu therefore keeps the existing system-heap page allocator and SG backing model and adds only the state needed to stop treating the dma-buf as ordinary HLOS memory after ownership changes.

The staged states are:

`HLOS -> TRANSITION -> LENT -> ACTIVE -> DETACHED -> TRANSITION -> RECLAIMED`

with any uncertain ownership transition terminating in:

`POISONED`.

The wrapper also remembers whether the protected object is:

- **external**: `CP_CDSP` only;
- **internal camera target**: `CP_CDSP + CP_CAMERA`.

This preserves the two-buffer design proven from Windows instead of collapsing both objects into a camera-owned buffer.

## 2. Lend is allowed only after all HLOS access is quiescent

Before calling the E004ct SG ownership helper, the staged wrapper checks that the dma-buf has:

- no live userspace mmap;
- no live kernel vmap;
- no open CPU-access section;
- no mapped device attachment.

Userspace mmap lifetime is explicitly counted with VMA open/close callbacks. Kernel vmap and device-map state reuse Golden's existing counters/attachment records, while begin/end CPU access gets a small count.

This closes the dangerous race where physical ownership could be revoked while HLOS still has a legitimate mapped view.

## 3. HLOS CPU operations fail while protected

CPU visibility is allowed only in `HLOS` and `RECLAIMED` state.

While the object is transitioning, lent, active, detached or poisoned:

- `mmap()` returns `-EPERM`;
- `vmap()` returns `-EPERM`;
- `begin_cpu_access()` returns `-EPERM`;
- DMA mapping uses `DMA_ATTR_SKIP_CPU_SYNC` rather than implying ordinary HLOS CPU coherency.

Device/IOMMU mapping remains possible after a successful lend, because the CPZ secure FastRPC context will eventually need to import the dma-buf. E004cu does **not** yet select or activate that context.

## 4. The dma-buf cannot disappear during protected ownership

Immediately before the first physical ownership transition the wrapper takes an extra dma-buf reference and sets `cpz_hold`.

That reference remains held throughout the protected lifetime. Therefore closing the userspace fd cannot run the heap release path while CPZ or camera hardware owns the physical pages.

On successful reclaim:

1. the exact protected owner set is reassigned to HLOS RWX;
2. state becomes `RECLAIMED`;
3. the owner-kind tag is cleared;
4. `cpz_hold` is cleared;
5. the extra dma-buf reference is dropped.

Only then can ordinary release recycle the pages.

## 5. Ownership uncertainty leaks safely instead of freeing unsafely

E004ct proved SG ownership changes are batched and a later batch can fail after earlier batches succeed.

Therefore a failed lend or reclaim changes the object to `POISONED` and deliberately keeps the extra dma-buf reference. The release path also refuses to recycle backing unless state is HLOS-accessible and no protected hold exists.

This intentionally favors a memory leak over reuse of pages whose physical owner is unknown. A future recovery gate may add tracked-batch rollback; E004cu does not guess one.

## 6. Build-only boundary is mechanical

The staged source is generated from the exact Golden `system_heap.c` preimage:

`56b0db19f9e4999ec2144fd3d25bf370e2d15f1602447f8fd5b1c96eb321856d`

Both baseline and staged sources compile against the Golden runtime-v4 headers. The staged object adds 428 bytes of executable `.text` in this external-object build.

The object retains:

- `sp11_cpz_assign_sg` as an unresolved E004ct ownership dependency;
- `dma_buf_put` as the reclaim/ref-lifetime dependency.

The original heap `module_init()` is deliberately removed, and the object contains no `init_module` or `__initcall` symbol. There is no live heap registration or runtime callsite.

## 7. What is still missing

The backing/ownership lifetime is now bounded, but the worker-control side remains deliberately disconnected. Golden still needs a safe port of:

- the FastRPC process/session type ABI;
- privileged `CPZ_USERPD` selection;
- PD-typed secure context-bank matching;
- secure import classification for a remotely owned dma-buf;
- a provider-only control path that ordinary userland cannot abuse.

Until those are proven, this wrapper stays unreachable.

## Safety boundary

Golden FullIO v19c remained active with no one-shot armed. No staged heap or SCM module was loaded, no ownership transition occurred, no CPZ process was created, and no camera/SecureISP runtime was started.

## Next gate

**E004cv — Golden CPZ FastRPC session/context-bank port, compile-only and privilege-gated.**

Port the minimum already-authorized downstream contract without activating it:

1. remote process type field and `CPZ_USERPD = 6`;
2. session-info control ABI behind explicit trusted-caller validation;
3. PD-typed secure context-bank matching;
4. secure import classification hook for the E004cu protected dma-buf state;
5. no live DT `pd-type`, no CPZ process creation and no ordinary-user fallback.

The gate should prove the code compiles and that an untrusted/delegated caller cannot select CPZ before any runtime experiment is considered.
