# E004da — external CPZ protected-sample backing implementation

## Result

**PASS: the external protected-sample backing/lifetime side is now implemented as compile-only Golden code around an ordinary dma-buf plus the E004cz protected system-heap state machine. The external object is lent to CP_CDSP only, keeps HLOS CPU visibility false throughout protected ownership, retains backing and worker references across the future FastRPC mapping lifetime, enforces detach-before-reclaim and reclaim-before-release, and links cleanly with the E004cz protected stack. The actual FastRPC fd/import control-plane handoff remains deliberately unresolved and no runtime path is registered.**

No protected ownership call was executed.

## 1. External and internal backing remain different objects

The external provider accepts a dma-buf plus the existing 16-byte opaque sample identity, request ID and allocation extent.

It deliberately calls:

`sp11_cpz_system_heap_lend(dmabuf, false)`

The `false` argument is security-significant. In E004cz's system-heap implementation:

- every protected lend starts with `CP_CDSP` as destination;
- `CP_CAMERA` is added only when `camera_target == true`.

Therefore this external provider can request only:

`HLOS -> CP_CDSP`

while the separate internal capture-target path remains:

`HLOS -> { CP_CDSP, CP_CAMERA }`.

This preserves the Windows two-buffer architecture rather than turning the external consumer sample into an IFE/CAMSS target.

## 2. Backing identity and lifetime are concrete

`sp11_cpz_external_bind()`:

- takes a dma-buf reference;
- copies the 16-byte opaque identity;
- records request ID and allocation extent separately;
- rejects an extent larger than the dma-buf;
- starts with HLOS CPU visibility recorded as true because no ownership transition has happened yet.

The actual system-heap identity is enforced when protected ownership is requested: `sp11_cpz_system_heap_lend()` rejects a dma-buf whose exporter is not the staged system heap.

Thus a wrong backing type fails before it can become a protected external sample.

## 3. HLOS exclusion is reflected immediately and failures stay closed

After a successful CP_CDSP lend, the provider immediately records normal-HLOS CPU visibility as false.

It then requires the provider-authoritative query:

`sp11_cpz_dma_buf_is_protected(dmabuf)`

before proceeding toward worker import.

If the underlying ownership transition fails after entering the E004cu POISONED/uncertain state, the same query remains true. E004da then:

- records HLOS visibility as false;
- moves the external contract into a non-releasable reclaiming/uncertain phase;
- keeps the backing reference.

It never converts an uncertain ownership failure back into an ordinary HLOS buffer by metadata alone.

## 4. Worker import lifetime now has an explicit backing reference

Before the actual FastRPC import, `sp11_cpz_external_begin_worker_import()`:

- verifies CP_CDSP ownership is active;
- verifies the dma-buf is still provider-authoritatively protected;
- takes an additional dma-buf reference;
- returns the dma-buf to the future import layer.

The provider-held worker reference is intentionally redundant with the reference FastRPC itself takes. That gives the provider a local fail-closed lifetime invariant even before the final control-plane wiring exists.

`sp11_cpz_external_commit_worker_import()` is only the **post-import commit point**. It marks the system-heap buffer active and records trusted-worker visibility after the caller has successfully established the real protected mapping.

If the import fails before commit, `abort_worker_import()` drops the extra provider reference and the still-LENT backing may be reclaimed directly.

## 5. Windows metadata distinctions remain preserved

Payload completion records independently:

- allocation extent;
- captured extent;
- serialized extent;
- payload offset.

The implementation additionally requires:

`payload_offset <= serialized_extent <= captured_extent <= allocation_extent`.

Thus the external mapping is not collapsed into a raw pixel buffer beginning at offset zero.

## 6. Detach happens before reclaim

`sp11_cpz_external_worker_detached()` is documented and coded as a post-FastRPC-detach operation.

Only then does it:

- move the system-heap state from ACTIVE to DETACHED;
- clear trusted-worker visibility;
- record detach-before-reclaim;
- drop the provider-held worker reference.

`sp11_cpz_external_reclaim()` rejects a still-mapped or still-referenced worker object.

For the failed-import path, no mapping was ever committed; a WORKER_OWNED/LENT object with no worker reference may reclaim directly.

## 7. Reclaim must precede final backing release

Successful reclaim restores HLOS ownership and records `ownership_reclaimed_before_free`.

`sp11_cpz_external_release()` accepts only:

- untouched `BACKING_READY`, where ownership never left HLOS; or
- `RECLAIMED`, with reclaim-before-free explicitly proven.

It refuses active, detached-but-not-reclaimed, reclaiming/uncertain, or worker-referenced objects.

If reclaim fails, the provider intentionally keeps the base dma-buf reference so the backing cannot disappear under unknown secure ownership.

## 8. Compile/link closure

The provider builds against Golden as an ARM64 object with nonzero executable text and no registration symbols.

Before integration it references the expected E004cz APIs:

- protected-state query;
- CPZ system-heap lend;
- active marker;
- detached marker;
- reclaim.

A partial link with the E004cz integrated protected stack resolves all `sp11_cpz_*` dependencies. No init/module registration appears in the combined object.

## 9. Remaining boundary: actual FastRPC handoff

E004da does **not** fake a kernel-internal FastRPC import API.

The current Golden FastRPC mapping path is fd/ioctl-oriented. E004da therefore stops at a precise handoff:

`protected dma_buf + retained provider worker ref`

A future layer must establish the real protected FastRPC mapping and call `commit_worker_import()` only after success. Likewise, it must unmap/detach FastRPC before calling `worker_detached()`.

This boundary is preferable to inventing a direct-kernel FastRPC API that the Qualcomm implementation does not provide.

## Safety boundary

SP11 remained on Golden FullIO v19c with no one-shot armed. The provider object was compiled and partially linked only. No object/module was loaded, no dma-buf was lent or reclaimed, no SCM ownership transition ran, no FastRPC request or CPZ process ran, and no camera or Linux SecureISP runtime occurred.

## Next gate

**E004db — external protected-sample FastRPC handoff authority**, static/compile-only first.

Resolve the real control-plane bridge from the retained protected dma-buf to FastRPC without inventing an API:

1. determine whether the Linux userspace ABI can receive/export the external dma-buf fd without temporarily reopening HLOS CPU access;
2. determine which FastRPC ioctl/process setup owns the fd mapping and unmapping lifetime;
3. bind import success/failure to E004da's begin/commit/abort transitions;
4. bind FastRPC unmap completion to `worker_detached()`;
5. keep CB9 disabled and do not issue an ioctl or ownership transition.
