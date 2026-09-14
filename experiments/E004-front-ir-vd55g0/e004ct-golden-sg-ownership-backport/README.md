# E004ct — Golden scatter-gather ownership backport

## Result

**PASS: Golden's existing Qualcomm SCM transport can be extended, compile-only, to assign scatter-gather protected buffers without requiring one physically contiguous frame allocation. The multi-region path reuses the exact MP/HYP_ASSIGN SMC already used by `qcom_scm_assign_mem()`, stages descriptors through Golden's existing `qcom_tzmem` pool, and a compile-only SG consumer batches system-heap-style physical extents correctly. No runtime code was installed or executed.**

This closes the E004cs contiguity question: system-heap SG backing is mechanically viable for the future CPZ provider. It does **not** yet make Golden's ordinary dma-heap safe for protected use, because Golden still lacks mem-buf ownership tracking and the CPZ FastRPC runtime binding.

## 1. Golden already has the secure-world multi-region primitive

The low-level `__qcom_scm_assign_mem()` in Golden already accepts three descriptor buffers:

- an array of physical memory regions;
- an array of current-owner VMIDs;
- an array of destination VMID/permission records.

The public `qcom_scm_assign_mem()` simply wraps that interface for one physical region.

Therefore SG support does not require a new secure call or guessed firmware ABI. The backport exposes a bounded multi-region wrapper around an interface already present in the exact Golden source.

## 2. Final backport preserves Golden's qcom_tzmem transport

Golden's current one-region function deliberately allocates its secure-call descriptor block from `qcom_tzmem` and passes those physical addresses to secure world.

The initial E004ct draft passed caller kmalloc descriptors through `virt_to_phys()`. That compiled, but audit rejected it as unnecessarily diverging from Golden's established secure-call memory lifetime.

The final `qcom_scm_assign_mem_regions()` instead:

1. validates descriptor array sizes;
2. allocates one aligned block from `__scm->mempool` with `qcom_tzmem_alloc()`;
3. copies region descriptors into it;
4. converts source VMIDs to little-endian records inside that block;
5. copies destination permission records;
6. calls the unchanged `__qcom_scm_assign_mem()` with qcom_tzmem physical addresses.

This is the same descriptor transport class as Golden's existing `qcom_scm_assign_mem()`.

## 3. SG batching is offset-correct and bounded

The compile-only consumer accepts a `sg_table` and batches at most 32 entries while keeping each batch below 2 MiB.

Before the first ownership transition it validates the entire table. Each physical extent is encoded with `sg_phys(sg)`, not `page_to_phys(sg_page(sg))`, so an SG entry with a non-zero offset is represented correctly.

A region at or above the batch-size limit is rejected before the first SCM call.

## 4. Partial success must fail closed

A multi-batch ownership transition is not atomic across the whole dma-buf. Batch N can fail after batches 0..N-1 have succeeded.

E004ct therefore does not pretend it can safely free or restore such a buffer. Any post-start failure becomes `-EADDRNOTAVAIL`; the future provider must mark the sample ownership-unknown/poisoned and retain the backing until explicit reclaim succeeds.

That is consistent with the protected-sample lifetime proven in E004cq/E004cr.

## 5. What this resolves

E004cs left two possible backing strategies:

- force a dedicated contiguous heap;
- add the missing multi-region SCM path and permit ordinary SG-backed allocation underneath a protected ownership wrapper.

E004ct proves the second architecture compiles against Golden. **Physical contiguity is no longer a fundamental requirement.**

That is useful because the final external sample can remain a normal per-sample dma-buf shape while its physical SG extents are lent away from HLOS.

## 6. What this does not resolve

Golden's live dma-heaps remain ordinary HLOS-accessible allocators. E004ct does not change that.

Still missing are:

- mem-buf-style ownership state attached to the dma-buf;
- mmap/vmap denial after HLOS-excluding lend;
- protected import classification in FastRPC;
- authorized CPZ PD selection and context-bank policy;
- provider orchestration and poison/reclaim state.

So the SG result removes the contiguous-memory blocker but does not authorize protected runtime.

## Compile evidence

Both the untouched Golden SCM translation unit and the staged translation unit compile against the Golden runtime-v4 headers. The staged object exports `qcom_scm_assign_mem_regions()` and the SG consumer retains it as an unresolved dependency, proving the call path was compiled.

The staged SCM `.text` grows from 21,852 to 22,300 bytes (+448 bytes).

No module was linked into the running kernel or loaded.

## Safety boundary

Golden FullIO v19c stayed active. No SCM ownership call, dma-buf lend, CPZ process, FastRPC invoke, DT change, camera stream, Windows boot or SecureISP runtime occurred.

## Next gate

**E004cu — Golden protected dma-buf ownership state/backing wrapper, compile-only first.**

Now that SG ownership is mechanically possible, port only the minimum host-side dma-buf ownership state needed by the already-proven architecture:

1. distinguish untouched HLOS-exclusive backing from a lent protected sample;
2. deny mmap/vmap/CPU-access hooks after HLOS-excluding lend;
3. retain the dma-buf while CPZ imports it;
4. encode `ACTIVE -> DETACHED -> RECLAIMED` versus `POISONED` lifetime;
5. use the E004ct multi-region SCM interface behind a disabled provider boundary;
6. leave CPZ FastRPC/DT activation unreachable.

Do not modify the live system heap or perform an ownership transition.
