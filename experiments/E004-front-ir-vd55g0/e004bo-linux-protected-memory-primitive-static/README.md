# E004bo — Linux protected-memory primitive inventory

## Result

**PASS: the current SP11 Linux kernel contains the low-level Qualcomm memory-ownership primitive needed for protected-memory transitions, but it does not contain a ready-made protected/restricted DMA heap or camera protected-buffer backend.**

This is a static source inventory only. No SCM call or protected-memory operation was executed.

## What exists

### 1. Qualcomm ownership reassignment

The current kernel exports:

`qcom_scm_assign_mem(phys_addr_t mem_addr, size_t mem_sz, ...)`

Its own documentation says that it makes a secure call to **reassign memory ownership** between VMIDs.

The API takes a physical memory region, a bitmap of current owners, and destination VMID/permission pairs. On success it updates the current-owner bitmap.

The kernel also defines camera-related VMID names, including:

- `QCOM_SCM_VMID_CP_CAMERA = 0xD`;
- `QCOM_SCM_VMID_CP_CAMERA_PREVIEW = 0x1D`.

Their presence proves that the firmware ABI knows camera protection domains. It does **not** prove which VMID is correct for the external protected capture sample.

E004bh already established that Windows SecureISP's internal buffer uses a CP_CAMERA ownership concept, while the external VTL1 sample has a separate lifetime. E004bo therefore deliberately does not assign either VMID to the Linux external-sample contract.

### 2. Reversible assignment patterns

Existing Qualcomm drivers show that `qcom_scm_assign_mem` is normally treated as a transaction, not a one-way label.

Examples in the current tree:

- FASTRPC assigns memory to a remote VMID and explicitly reclaims it to HLOS on free/failure.
- remoteproc PAS assigns known physical reserved-memory ranges and unassigns them later.
- RMTFS uses a known reserved physical range and reclaims it on driver removal.
- ath10k similarly has paired map/unmap permission paths.

This gives us a strong lifetime rule for any future camera backend:

**an ownership change must have an explicit, failure-safe reclaim path before the underlying allocation is freed.**

These drivers are precedents for transaction structure only. They are not evidence that their VMIDs, permissions, allocators, or sharing model are correct for the camera.

## What does not exist

### No restricted/secure DMA heap

The current `drivers/dma-buf/heaps` tree contains only:

- system heap;
- CMA heap.

There is no restricted heap or secure heap implementation in this source tree.

The Golden build configuration enables ordinary DMA-BUF system/CMA heaps, CMA, Qualcomm SCM/TZMEM, and ARM SMMU support, but no generic protected DMA heap.

### Ordinary CMA heap is not a protected sample backend

CMA is useful because it provides physically contiguous memory.

However the existing CMA DMA-BUF exporter also supports:

- CPU access synchronization;
- `mmap`;
- `vmap`;
- normal DMA attachment/mapping.

It is therefore an ordinary CPU-visible allocator/exporter and cannot simply be relabeled as a protected camera heap.

A future protected backend might use a contiguous allocator internally, but it would need a different exported object/policy that forbids inappropriate CPU exposure and owns the protection transaction.

### System heap is even less suitable for a physical-range ownership call

The system heap builds a scatter/gather table from multiple page allocations and is explicitly CPU-mappable.

`qcom_scm_assign_mem` takes one physical range, so a generic SG system-heap allocation is not a direct fit for a single contiguous ownership transaction.

## qcom_tzmem is not the sample allocator

`qcom_tzmem` provides memory used by Qualcomm secure-call plumbing.

In fact, `qcom_scm_assign_mem` uses `qcom_tzmem_alloc` to construct the SCM **descriptor metadata** containing source VMIDs, target region information, and destination permissions.

That is not evidence that TZMEM is intended to hold multi-megabyte camera capture samples.

Therefore E004bo treats qcom_tzmem as secure-call implementation plumbing, not the protected-camera backing allocator.

## Critical SP11 address-model finding

The current ordinary CAMSS path does:

`vb2_dma_sg_plane_desc → sg_dma_address → camss_buffer.addr[] → VFE`.

Linux's scatterlist API explicitly defines `sg_dma_address()` as the **bus address after DMA mapping**.

On this SP11, the CAMSS node `isp@acb7000` is attached to the application SMMU with multiple camera stream IDs. Historical camera runs also show `acb7000.isp` joining an IOMMU group under the translated IOMMU domain.

Therefore the address programmed into VFE is a DMA/SMMU address and must not be assumed to be the physical address of the underlying memory.

By contrast, `qcom_scm_assign_mem` explicitly takes a `phys_addr_t` physical memory region.

This closes an important design ambiguity:

**a future protected sample object must retain the physical protected range used for ownership transitions separately from the camera-visible DMA/IOVA used to program VFE.**

Passing the ordinary `camss_buffer.addr[]` value directly to `qcom_scm_assign_mem` would be architecturally unjustified.

## Candidate backend shape implied by this inventory

E004bo does not implement a backend, but the source tree now constrains what a correct one would have to own:

- a physically known backing allocation suitable for the firmware ownership API;
- a separate CAMSS device mapping/IOVA;
- a stable per-buffer identity;
- explicit assignment state and current-owner state;
- fail-closed attach/map rules;
- no ordinary mmap/read exposure for protected samples;
- paired reclaim before backing memory is released;
- cleanup on every partial-failure path.

The low-level SCM API is only one potential primitive inside that owner object. It is not itself the protected-buffer abstraction.

## Important unresolved questions

Before any secure runtime can be considered, static work still needs to resolve:

1. which ownership domain is correct for the **external** protected sample;
2. what physical allocation/alignment contract the SP11 camera protection firmware requires;
3. how a protected physical backing should be mapped into the exact CAMSS SMMU context used by the secure camera path;
4. whether the secure camera path expects a different stream ID/domain or secure SMMU configuration from the ordinary CAMSS mappings;
5. whether HLOS is allowed to remain an owner while the camera consumes the sample, or must be excluded entirely.

Those answers must come from the Windows/firmware oracle or existing Qualcomm contracts—not from guessing based on VMID names.

## Safety boundary

No module was loaded, no SCM method was invoked, no ownership was changed, and no QCOMTEE or protected MMIO operation occurred.

This checkpoint changes no kernel source or runtime state.

## Evidence

- `evidence/QCOM-SCM-ASSIGN-MEM.txt`
- `evidence/ASSIGN-ROLLBACK-PRECEDENTS.txt`
- `evidence/DMA-HEAP-INVENTORY.txt`
- `evidence/TZMEM-BOUNDARY.txt`
- `evidence/CAMSS-DMA-VS-PHYS-GAP.txt`
- `evidence/KERNEL-CONFIG.txt`

## Next gate

Statically resolve the SP11 protected-camera **memory + SMMU ownership contract** far enough to determine whether the external sample requires a dedicated secure SMMU context/stream ID and which physical-memory ownership set is expected. No SCM calls or Linux secure runtime.
