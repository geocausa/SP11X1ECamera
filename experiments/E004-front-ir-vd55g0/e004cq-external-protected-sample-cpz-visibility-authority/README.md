# E004cq — external protected-sample CPZ visibility authority

## Result

**PASS: the separate external protected sample now has a mechanically supported Qualcomm/Linux representation. A generic mem-buf-aware dma-buf can be lent from HLOS to `CP_CDSP` alone, eliminating HLOS CPU permissions while remaining importable through FastRPC's secure context-bank path. Same-machine QHEE explicitly authorizes both the forward `HLOS -> CP_CDSP` transition and the reverse `CP_CDSP -> HLOS` reclaim. The dma-buf reference/lifetime model also guarantees reclaim before backing release.**

This closes the external-sample architecture hole left by E004cp. It is still a static/read-only authority result: Golden does not yet contain the downstream mem-buf/CPZ host implementation, and no protected runtime operation was executed.

## 1. The external sample does not need CP_CAMERA ownership

The Windows oracle keeps external and internal protected objects separate:

- internal capture target: camera hardware ownership plus trusted-worker mapping;
- external sample: trusted-worker-visible protected section, but no CP_CAMERA assignment.

The same-machine QHEE access-control rule table has the exact Linux-equivalent distinction.

It contains an active single-owner rule:

`HLOS -> CP_CDSP (0x2a)`

and a matching active reverse:

`CP_CDSP -> HLOS`.

Separately, the internal camera-target rule remains:

`HLOS -> { CP_CAMERA, CP_CDSP }`.

Therefore an external sample can be protected for the CDSP worker without becoming an IFE/CAMSS hardware target.

## 2. Generic Qualcomm dma-heaps can supply the per-sample backing

The Qualcomm system and CMA dma-heaps create ordinary per-allocation dma-bufs and wrap them with mem-buf ownership state using:

`mem_buf_vmperm_alloc()` → `mem_buf_dma_buf_export()`.

This is important: the external sample need not be allocated by the camera driver or inherit camera-target semantics.

The initial state is ordinary HLOS ownership. Before exposing the sample to protected processing, the provider can lend that backing to a remote owner set.

## 3. `mem_buf_lend({CP_CDSP})` removes HLOS by construction

The generic mem-buf LEND operation explicitly rejects a destination ACL containing the current VM.

So a destination list containing only `CP_CDSP` means:

- HLOS is absent from the active owner set;
- the wrapper updates current-VM permissions to zero;
- the dma-buf is marked lent/shared rather than local-exclusive.

No CP_CAMERA entry is required by the generic mem-buf API.

## 4. HLOS CPU mapping is blocked after lend

The Qualcomm dma-buf exporter checks mem-buf ownership state on CPU map operations.

After HLOS has zero permissions:

- `mmap()` fails with `-EPERM`;
- `vmap()` fails with `-EPERM`;
- CPU cache-maintenance helpers do not perform normal HLOS CPU synchronization.

Existing CPU mappings cannot silently survive the ownership transition: mem-buf refuses an HLOS-excluding lend while the wrapper is pinned/mapped.

This gives the external sample the same critical property as Windows VTL1 secure backing: ordinary HLOS cannot use it as a CPU image buffer while protected ownership is active.

## 5. Device / CPZ visibility is independent from HLOS CPU visibility

The same Qualcomm dma-buf exporter explicitly allows IOMMU mapping independent of current-VM CPU permissions.

FastRPC imports the dma-buf by reference, sees that it is no longer an untouched local-exclusive buffer, marks it secure, and maps it through the secure SMMU context.

E004co proved the downstream extension that maps this secure-memory session to the `CPZ_USERPD` context-bank class.

Thus the external object has the required visibility shape:

`CP_CDSP / CPZ worker: writable`

`HLOS CPU: inaccessible`

`CAMSS hardware target: not required`.

## 6. Lifetime and teardown are parity-safe

The dma-buf itself supplies backing lifetime:

- FastRPC takes a dma-buf reference on import;
- user fd closure therefore cannot free backing while the worker still owns a mapping;
- FastRPC drops its reference only after unmap/detach;
- final dma-buf release calls mem-buf reclaim before the heap free callback;
- reclaim restores HLOS ownership first.

If reclaim fails, mem-buf deliberately retains an extra dma-buf reference so backing is not freed under unknown ownership.

That is the fail-closed lifetime discipline we need.

## 7. Logical identity remains separate from the dma-buf fd

Windows uses a GUID as the external sample identity. Linux does not need to copy that API literally.

E004bw already reserves a stable 16-byte provider identity in the external-sample representation. E004cq supplies the protected backing lifetime behind that identity.

The provider must retain:

`opaque 16-byte sample id -> dma-buf reference`

for the sample lifetime. An fd is only a transport handle and must not become the logical identity.

## 8. Two-buffer CPZ parity model after E004cq

The architecture is now mechanically complete at the design/authority level:

**Internal target**

`generic protected backing`
→ lend to `{CP_CAMERA, CP_CDSP}`
→ IFE/CAMSS writes
→ CPZ reads.

**External sample**

`generic mem-buf-aware backing`
→ lend to `{CP_CDSP}`
→ CPZ writes
→ HLOS CPU remains excluded.

**Teardown**

worker unmap/detach
→ protected ownership reclaim
→ backing release.

This reproduces the Windows security/execution shape without collapsing the two protected objects.

## What remains missing from Golden

The active Golden kernel still lacks the downstream implementation pieces proved in E004co/E004cq:

- mem-buf-aware Qualcomm heap integration;
- CPZ remote process-type/session ABI;
- PD-typed secure FastRPC context-bank selection;
- provider glue connecting CAMSS and the external sample contract to those mechanisms.

So **runtime remains unauthorized** even though the architecture is now mechanically resolved.

## Safety boundary

No dma-buf was lent, reclaimed or mapped through CPZ. No SCM ownership call, FastRPC invoke, CPZ process creation, camera stream, Windows boot or SecureISP runtime occurred. Golden FullIO v19c remained active.

## Next gate

**E004cr — compile-only external CPZ sample provider contract.**

Encode the now-proven external sample lifecycle without implementing it:

1. per-sample opaque identity distinct from fd;
2. generic mem-buf-aware backing;
3. HLOS -> CP_CDSP lend phase;
4. secure/CPZ import phase;
5. active worker visibility with HLOS CPU excluded;
6. worker detach before ownership reclaim;
7. reclaim before backing release;
8. no CP_CAMERA requirement for the external object;
9. no HLOS transfer fallback.

Require byte-identical executable `.text` versus baseline and perform no runtime binding.
