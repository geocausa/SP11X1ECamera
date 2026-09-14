# E004db — external protected-sample FastRPC handoff authority

## Result

**PASS: the real Linux control-plane handoff for the protected external sample is now bounded without inventing a kernel-private FastRPC API. A privileged CPZ control process can retain the original system-heap dma-buf fd while HLOS CPU mapping is revoked, select the CPZ FastRPC session first, and use the existing `MEM_MAP` / `MEM_UNMAP` fd protocol. The exact SP11 CDSP firmware independently proves map flag 2 dispatches through its fd-backed FastRPC mapping implementation. E004da's begin/commit/abort/detach lifecycle is now mechanically bound to the ioctl result lifetime, and the external map length is explicitly the Windows-oracle `cbCaptured` extent rather than allocation capacity.**

This checkpoint is static + compile/link only. It issues no ioctl and performs no ownership transition.

## 1. No special kernel FastRPC import API is required

Golden FastRPC is intentionally fd/ioctl based. Rather than inventing a direct kernel import function, E004db preserves that architecture.

The trusted control process can obtain the external backing as a normal dma-buf fd from:

`/dev/dma_heap/system`

before the provider lends ownership away from HLOS. The same fd is kept open throughout protected processing.

The fd is an object/lifetime capability, **not a CPU mapping**.

Golden `dma_buf_get(fd)` performs `fget()` and returns the dma-buf object from the file. It does not mmap/vmap the backing or begin CPU access.

While the E004cz system-heap object is protected:

- `mmap()` is denied;
- `vmap()` is denied;
- `begin_cpu_access()` is denied;
- DMA/IOMMU attachment to the authorized device remains possible.

Therefore retaining the userspace fd does not restore the HLOS image view that the ownership transition removed.

## 2. The same fd must remain stable until unmap

E004db verifies the fd resolves to the **same dma-buf object** already bound to the E004da external sample.

The preferred lifetime is:

`DMA_HEAP fd allocation`
→ provider bind
→ CP_CDSP-only lend
→ FastRPC map using same fd
→ worker processing
→ FastRPC unmap using same fd/raddr
→ worker detached
→ ownership reclaim
→ final fd/backing release

The fd must not be closed and reused before `MEM_UNMAP`. FastRPC's host map lifetime retains the dma-buf reference itself, but stable fd identity avoids fd-number alias/reuse ambiguity in map/unmap lookup paths.

## 3. CPZ session selection comes before process creation

E004cv already proved the privileged host process-type contract. E004db carries it into the handoff order:

1. open the **secure CDSP FastRPC device**;
2. same opener TGID + `CAP_SYS_ADMIN` selects CDSP domain 3 / `CPZ_USERPD = 6` / non-shared context;
3. session selection binds to the CPZ-typed secure context bank;
4. only then perform the process attach/create operation;
5. then map protected dma-bufs in that same FastRPC file/process context.

This ordering matters because E004cv locks session configuration as soon as an INIT attach/create operation starts.

Delegated/untrusted callers are not allowed to select CPZ.

The E004db object only builds the session-info structure. It opens no device and issues no ioctl.

## 4. Same-machine CDSP firmware proves fd map flag 2

Fresh Hexagon analysis of the exact Golden/SP11 CDSP firmware recovers:

- `fastrpc_invoke_mmap_create`;
- `fastrpc_invoke_fd_mmap_get`;
- `fastrpc_invoke_fd_mmap_create`;
- `fastrpc_invoke_mmap_get_cpz_phys`;
- fd map/unmap diagnostics from `apps_mem_dma_handle_map`.

The DSP FastRPC kprocess dispatcher branches on mapping flag `2` and calls the function associated with `fastrpc_invoke_fd_mmap_create`.

The Linux FastRPC UAPI defines:

`FASTRPC_MAP_FD = 2`.

So the fd-backed mapping path is not inferred from a generic name: it is directly present in the same-machine DSP firmware.

## 5. MEM_MAP owns a real dma-buf mapping/reference

On the E004cv staged host path, `FASTRPC_IOCTL_MEM_MAP`:

1. takes the supplied dma-buf fd;
2. `dma_buf_get(fd)` retains a reference;
3. checks provider-authoritative protected state;
4. requires secure CDSP + CPZ client/session for a protected dma-buf;
5. attaches/maps the dma-buf to the CPZ context-bank device;
6. retains **no HLOS virtual address** for the protected map;
7. sends `FASTRPC_RMID_INIT_MEM_MAP` to the DSP;
8. retains the map and returned remote VA only after success.

A DSP map failure drops the map/reference. If the host cannot return the result to userspace after the DSP map succeeded, it immediately executes the unmap path.

## 6. MEM_UNMAP is the trusted-detach authority

`FASTRPC_IOCTL_MEM_UNMAP` first tells the DSP to remove the mapping.

Only a successful DSP unmap causes FastRPC to drop the map. Final FastRPC map free then:

- unmaps the DMA attachment;
- detaches it from the secure context-bank device;
- drops FastRPC's dma-buf reference.

An unmap failure leaves the mapping/reference pinned.

That gives E004da a clean authority boundary:

- **before MEM_MAP** → `begin_worker_import()`;
- **MEM_MAP failure** → `abort_worker_import()`;
- **MEM_MAP success** → `commit_worker_import()`;
- **MEM_UNMAP failure** → do nothing; remain protected/pinned;
- **MEM_UNMAP success** → `worker_detached()`;
- only after that may ownership reclaim occur.

A defensive `MAP_COMMIT_FAILED` state handles the unlikely case where FastRPC mapped successfully but the provider ACTIVE transition failed. The FastRPC mapping must still be unmapped before the provider worker reference is released.

## 7. Windows `cbCaptured` mapping length is preserved

E004bv proves Windows has both values before the external trustlet map:

- `cbBufferSize` — allocation capacity;
- `cbCaptured` — captured sample extent.

SecureISP transiently copies capacity, then overwrites its final external map length with `cbCaptured` **before** calling `MapViewOfFile`.

E004db therefore does not let `build_mem_map()` accept an arbitrary length.

A separate pre-map declaration records:

`declared_captured_extent`

with:

`0 < declared_captured_extent <= allocation_extent`.

`MEM_MAP.length` is populated only from that value.

Later payload completion must report the **same** captured extent. It additionally enforces:

`payload_offset <= serialized_extent <= captured_extent <= allocation_extent`.

This closes the parity gap where Linux might otherwise have mapped the whole allocation capacity merely because the backing dma-buf is larger.

### Lower mapping-layer note

The Linux DMA attachment can establish SMMU translations for the backing object at the secure context-bank layer, while the FastRPC process map supplied to the trusted CPZ process is bounded by the declared captured extent. That is acceptable at this gate because CPZ is itself the trusted owner; HLOS CPU visibility remains revoked. The worker ABI must still use only the returned process mapping/range rather than raw backing/IOMMU addresses.

## 8. Compile/link closure

The new coordinator object:

- compiles against the Golden headers;
- has `1884` bytes of executable `.text`;
- contains no init/module registration;
- directly references the E004da lifecycle functions and provider-authoritative dma-buf query.

Partial-linking it with the complete E004da protected stack gives:

- `.text = 33308` bytes;
- SHA-256 `67dedfc5ba8c838990a5562ba9dac17fbf05dd763f9d44737a440a8dd0352831`;
- zero unresolved `sp11_cpz_*` integration edges;
- no runtime registration symbols.

The coordinator itself contains **no `ioctl()` call**. It constructs/validates request and result contracts only.

## 9. What is still missing

The memory, lifetime, context-bank, and host map/unmap path is now mechanically bounded. The largest remaining gap is the **actual CPZ worker program/invoke ABI**.

We still need to prove:

- which signed/authorized image runs as the camera CPZ worker, or how a source-controlled worker can be admitted;
- the remote method/command that receives internal and external protected mappings;
- how image geometry, payload offset and transfer mode are passed;
- how worker completion is reported before MEM_UNMAP;
- whether the worker can reproduce the Windows copy/SWAB/synthetic-fill behavior without gaining any HLOS fallback.

Do not mistake the existence of the CPZ process class and mapping path for an identified camera worker implementation.

## Safety boundary

SP11 stayed on Golden FullIO v19c. CB9 remains absent/disabled. No dma-heap allocation was made for this experiment, no protected ownership transition occurred, no SCM call ran, no FastRPC ioctl ran, no CPZ process was created, and no camera or Linux SecureISP runtime was invoked.

## Next gate

**E004dc — CPZ protected-frame worker image and invoke ABI**, static first.

Start from same-machine CDSP firmware and Qualcomm FastRPC process-loader/invoke contracts. Resolve the smallest worker ABI that can:

1. receive/map the internal `{CP_CAMERA, CP_CDSP}` target;
2. receive/map the external `{CP_CDSP}` sample;
3. consume geometry + payload offset + captured extent;
4. perform the Windows-proven CPU transfer variants;
5. signal completion before external MEM_UNMAP;
6. remain outside HLOS with no CPU-visible fallback.

Do not create a CPZ process or invoke protected buffers until that worker identity/ABI is proven.
