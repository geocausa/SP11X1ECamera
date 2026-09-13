# E004bp — Windows two-buffer protected camera pipeline

## Result

**PASS: the Windows protected IR path uses two distinct protected buffers. The IFE hardware writes into a worker-created CP_CAMERA internal target, then the protected worker transfers/processes that image into the externally supplied VTL1 secure sample.**

This corrects the earlier working assumption that the external VTL1 sample itself was the direct IFE/VFE DMA target.

No Windows runtime and no Linux secure runtime were required.

## Pipeline

The protected path is:

`camera / IFE hardware`
→ **internal SecureISP buffer assigned to CP_CAMERA**
→ **protected-worker copy / image-processing stage**
→ **external GUID-addressed VTL1 secure sample**

The secure lane remains a third, separate ownership lifetime.

## Internal buffer is the hardware capture target

The SecureISP worker creates its own secure section, maps it, aligns the allocation to 4 KiB pages, builds a domain-VA array, then calls:

`AssignMemoryToSocDomain(..., DomainId=0x0d, Protection=0x04, ...)`

The numerical domain `0x0d` is the Windows-side value previously cross-checked against Linux `QCOM_SCM_VMID_CP_CAMERA`.

The object retains:

- internal assignment handle at `+0x10`;
- internal CP_CAMERA domain/SMMU address at `+0x28`;
- second internal address at `+0x48 = +0x28 + image offset`;
- internal trustlet mapping at `+0x30`.

The request builder then writes:

- `hMems[0]` from object offset `+0x28`;
- `hMems[1]` from object offset `+0x48`.

It rejects the request if either is zero with the diagnostic **“Invalid SMMU address for HW programming.”**

Because the code indexes the object as an `undefined8 *`, the observed `local_f0 + 5` and `local_f0 + 9` reads are byte offsets `0x28` and `0x48`.

Therefore the addresses handed to the protected IFE request are both derived from the **internal CP_CAMERA allocation**.

## External VTL1 sample is a separate object

The external sample arrives through the Surface camera stack with a GUID identity.

The worker's external-buffer path:

1. reconstructs the secure-section identifier;
2. calls `OpenSecureSection`;
3. maps the section into the protected worker;
4. stores the section handle at `+0x88`;
5. stores the mapped view at `+0x90`.

This path does not perform the internal `AssignMemoryToSocDomain` sequence.

The external GUID/sample therefore has a separate lifetime and representation from the internal hardware target.

## Internal → external transfer is explicit

After the worker has set the FrameBuffer attribute for a request, it calls:

`FUN_1800037c8(external_mapping + frame_offset, internal_mapping, width, height, request_id, ...)`

The first argument is derived from object `+0x90` — the external VTL1 mapping.

The second argument is object `+0x30` — the internal secure mapping.

The helper dispatches based on mode/request number:

- for early requests, `FUN_180003718` copies from argument 2 to argument 1 and neutral-fills the chroma plane;
- for later requests, `FUN_180003478` performs the worker's software image-processing sequence with the same internal-source/external-destination direction;
- a diagnostic/test path can pattern-fill the destination instead.

The low-level `FUN_180028600` used by the early-frame path decompiles as a memcpy/memmove-style routine: it reads from parameter 2 and stores into parameter 1.

This makes the direction mechanically explicit:

**internal CP_CAMERA mapping → external VTL1 mapping**.

## SurfaceCam's external descriptor versus worker hMems

SurfaceCam's secure path keeps the external GUID distinct from the request's memory handles.

The protected worker is what fills the request memory addresses from its internal secure buffer when the relevant output resource has no ordinary buffer.

This resolves the ambiguity around the earlier SurfaceCam diagnostic that printed both `hMems[]` and a GUID: they are related request metadata, but the GUID-backed external sample is not the origin of the hardware-programmed SMMU addresses.

## Lifetime separation

The secure-buffer object owns two independently releasable objects:

### Internal CP_CAMERA target

- secure section;
- CP_CAMERA assignment handle;
- domain/SMMU addresses;
- protected-worker mapping.

Cleanup closes/revokes the assignment and tears down the internal section state.

### External VTL1 sample

- external GUID;
- `OpenSecureSection` handle;
- protected-worker mapped view.

Cleanup unmaps the external view and closes the external section handle.

The worker's request cleanup releases both sides.

## Linux parity correction

This changes the Linux design target in an important way.

The compile-only E004bm/E004bn abstractions were useful for proving lifecycle boundaries, but a single `camss_protected_sample` directly consumed by VFE is **not** sufficient for strict Windows parity.

The parity model should instead distinguish:

1. **internal protected capture target**
   - physically owned/assigned to the camera protection domain;
   - owns the secure camera-domain/SMMU address programmed into VFE/IFE;
   - analogous to Windows' internal CP_CAMERA buffer;

2. **external protected sample**
   - consumer-facing protected object with its own stable identity/lifetime;
   - analogous to the GUID-addressed VTL1 secure section;
   - not assumed to carry the CAMSS hardware IOVA;

3. **protected transfer/processing stage**
   - moves/processes data from the internal target into the external sample inside an appropriate protected execution boundary;

4. **secure lane ownership**
   - still a separate stream/hardware lifetime.

Queue policy remains a fifth concern orthogonal to those ownership objects.

## Consequence for E004bo

E004bo remains valid about the Linux low-level primitives and the physical-address-versus-SMMU-IOVA distinction.

Its physical backing + CAMSS IOVA requirement applies specifically to the future **internal capture target**.

E004bp does **not** establish any CP_CAMERA VMID requirement for the external consumer sample. Do not infer one from the internal buffer's domain assignment.

## Safety boundary

All work here is static analysis of already-captured Windows binaries/evidence.

No Windows boot or process was started. No Linux SCM call, camera-domain assignment, QCOMTEE load, protected MMIO access, or secure camera runtime occurred.

## Evidence

- `evidence/INTERNAL-CP-CAMERA-HW-TARGET.txt`
- `evidence/EXTERNAL-VTL1-OPEN-LIFETIME.txt`
- `evidence/INTERNAL-TO-EXTERNAL-TRANSFER.txt`
- `evidence/MEMCOPY-DIRECTION.txt`
- `evidence/SURFACECAM-EXTERNAL-DESCRIPTOR.txt`
- `evidence/TWO-BUFFER-FIELD-MAP.txt`

## Next gate

Replace the compile-only single-buffer Linux scaffold with a **disabled-by-default two-buffer contract**:

- internal protected capture target;
- external protected sample;
- transfer/processing interface;
- secure lane interface;
- queue policy.

It must still compile to byte-identical executable code versus baseline and contain no backend instance or runtime activation path.
