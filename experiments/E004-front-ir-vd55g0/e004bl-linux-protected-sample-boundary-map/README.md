# E004bl — Linux protected-sample integration boundary map

## Result

**PASS: the current Linux camera stack has a clean, narrow place to add a future protected-sample backend, and that place is the CAMSS video/VB2 layer—not the VD55G0 sensor driver.**

This is an architecture/checkpoint only. It does not add secure allocation, memory reassignment, SecureISP activation, or any runtime behavior.

## Windows contract being mapped

The preceding Windows checkpoints established three separate lifetimes:

1. **external protected capture sample**
   - MFCore selects capture surface `0x10`;
   - MFPlat creates a per-buffer GUID;
   - FsIso creates/closes an IUM secure section under the secure-camera scenario;

2. **SecureISP internal CP_CAMERA allocation**
   - separate protected allocation internal to SecureISP;

3. **secure camera lane / worker ownership**
   - separate CSI/protected-worker ownership bracket.

Linux parity must preserve those separations.

## Current Linux buffer path

The current CAMSS path is conventional VB2 + scatter/gather DMA:

`vb2 queue`
→ `video_buf_init`
→ `vb2_dma_sg_plane_desc`
→ `sg_dma_address`
→ `camss_buffer.addr[]`
→ `vfe_queue_buffer_v2`
→ `vfe_wm_update(..., addr)`
→ hardware
→ `vb2_buffer_done`.

The queue currently uses:

- `vb2_dma_sg_memops`;
- `VB2_DMABUF | VB2_MMAP | VB2_READ`.

That is correct for ordinary capture and is **not** an acceptable protected-sample contract because MMAP/READ and ordinary SG-backed CPU-visible memory are part of its assumptions.

## Correct insertion boundary

### 1. Queue policy: `msm_video_register`

The queue registration point is where normal versus protected backing must diverge.

Current code binds every queue to `vb2_dma_sg_memops` and enables DMABUF/MMAP/READ.

A future protected route should select a protected backend/policy here, based on an explicit camera-stream security mode owned by CAMSS/video policy.

Important constraints:

- ordinary capture must remain byte-for-byte behaviorally unchanged;
- protected queues must not silently fall back to ordinary `vb2_dma_sg_memops`;
- protected capture must not expose `VB2_MMAP` or `VB2_READ`;
- importing an external DMABUF is only acceptable if the protected backend can prove that buffer belongs to the required protected domain.

### 2. Per-buffer identity/backing: `struct camss_buffer`

Today `struct camss_buffer` contains only the VB2 object, DMA addresses, and queue node.

The Windows contract requires a separate protected-sample identity/lifetime.

A future Linux structure therefore needs an optional protected-sample subobject with at least:

- protected/unprotected backing type;
- opaque backend handle;
- stable per-buffer identifier;
- protected DMA/IOMMU address presented to CAMSS/VFE;
- size/plane metadata;
- explicit lifetime state.

The identifier does not need to mimic a Windows GUID internally, but it must provide the same invariant: one stable identity owns one protected sample from allocation through release.

### 3. Address derivation: `video_buf_init`

This is the current transition from VB2 memory to CAMSS DMA address.

Normal path:
`vb2_dma_sg_plane_desc → sg_dma_address → buffer->addr[]`.

Protected path must **not** derive its address from the ordinary SG descriptor. Instead it must ask the protected-sample backend for the already-authorized device-visible address/handle and fail closed if that backing is not valid.

This is the key analogue of Windows' FsIso-created secure section.

### 4. Hardware queueing: `vfe_queue_buffer_v2`

VFE consumes only `camss_buffer.addr[0]`; it does not care how the backing was created.

That is useful: a protected backend can remain above VFE if it produces an address that is valid for the protected camera hardware/IOMMU domain.

Therefore VFE should not become the protected-memory allocator.

Its responsibility is only:

- consume the address after policy/backing validation;
- never remap or downgrade protected backing;
- preserve buffer identity through completion.

### 5. Stream start

`video_start_streaming` is the correct lifecycle gate before subdevices/hardware begin.

A future protected stream must require all protected sample objects to be valid before hardware start.

The secure lane/worker acquisition must remain a **separate** operation from protected sample creation. Windows proved these are different ownership domains.

Failure ordering should be:

1. protected sample preparation fails → no lane acquisition, no hardware start;
2. secure-lane acquisition fails → release prepared protected samples;
3. hardware start fails → stop/unwind hardware, release lane, then release protected samples.

No silent fallback to ordinary buffers is permitted.

### 6. Completion versus destruction

Current VFE completion returns buffers with `vb2_buffer_done`.

Completion is not the same thing as protected backing destruction.

A protected buffer may be dequeued/requeued repeatedly while its protected allocation remains alive.

Therefore release of the protected backing belongs in the VB2 buffer lifetime cleanup path, not ordinary frame completion.

The current `vb2_ops` has no `.buf_cleanup` callback. A future implementation should add one and make it the per-buffer release boundary.

That provides the Linux analogue of:

`SecureMediaBuffer::~SecureMediaBuffer → DestroySecureBuffer(GUID) → FsIso close`.

### 7. Stream stop / flush

Current stop order is:

1. stop hardware/subdevices;
2. stop media pipeline;
3. flush active/pending buffers back to VB2.

That is the right direction for a protected route.

Protected teardown must preserve:

1. stop DMA/hardware first;
2. return/flush VB2 ownership;
3. release the secure lane separately;
4. destroy protected sample backing only when the VB2 buffer lifetime actually ends.

This avoids destroying protected memory while VFE may still own its address.

## VD55G0 boundary

The current VD55G0 driver owns:

- sensor power;
- sensor register programming;
- stream enable/disable;
- V4L2 subdevice state.

It contains no VB2, DMA-buffer, protected-memory, SCM, VMID, QCOMTEE, or secure-buffer logic.

That is the correct separation and should remain so.

Do **not** add protected-memory allocation or SecureISP ownership into `vd55g0.c`.

At most, a future protected route may require ordinary stream sequencing coordination through the existing `.s_stream` callback; security state should remain in CAMSS/platform policy.

## Minimal implementation shape

The least invasive future implementation should look conceptually like:

- a small CAMSS protected-sample backend interface;
- optional protected state in `camss_video` / `camss_buffer`;
- queue-policy selection before `vb2_queue_init`;
- protected address acquisition in the buffer-init/lifetime path;
- no change to ordinary SG-backed queues;
- separate lane-owner hooks around stream start/stop;
- per-buffer release in `.buf_cleanup`;
- fail-closed behavior at every boundary.

No SecureISP code is needed in the VD55G0 sensor driver.

## Explicit non-goals for the next implementation

Do not:

- call SCM memory assignment merely because a queue is marked protected;
- load QCOMTEE;
- touch protected MMIO;
- reuse the existing ordinary DMA address and merely label it “secure”;
- disable IOMMU/security checks;
- expose protected samples through mmap/read;
- conflate external capture buffers with SecureISP's internal CP_CAMERA buffer;
- conflate buffer lifetime with secure-lane ownership.

## Evidence

- `evidence/LINUX-SOURCE-IDENTITY.txt`
- `evidence/CAMSS-VB2-LIFETIME.txt`
- `evidence/CAMSS-VFE-BUFFER-OWNERSHIP.txt`
- `evidence/VD55G0-SENSOR-BOUNDARY.txt`
- `evidence/WINDOWS-CONTRACT-INPUT.txt`

## Next gate

Implement a **compile-only, disabled-by-default protected-sample abstraction/scaffold** in a copied CAMSS source snapshot or patch artifact. It must contain no SCM call, no secure memory assignment, no QCOMTEE dependency, and no runtime activation path. Its job is only to make the lifetime/API boundaries compile cleanly before any protected-memory backend is designed.
