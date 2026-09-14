# E004cd — Linux VTL-equivalent protected-sample provider feasibility

## Result

**PASS (feasibility boundary): Golden/X1E Linux contains the surface and ownership primitives needed to model a VTL-like external protected sample, but it does not contain an active, identified trusted execution endpoint that can retain access after normal HLOS access is revoked. Therefore a parity-safe runtime provider cannot yet be implemented.**

This is a static/read-only gate. No secure runtime call, ownership transition, FF-A transaction, QTEE/QSEE probe, protected VM, Gunyah operation, protected heap registration, camera activation or Windows reboot occurred.

## Windows contract being matched

E004cc made the external Windows contract exact:

- the external sample is an IUM Secure Kernel object;
- its physical pages end in Hyper-V VTL0 protection mask `0`;
- ordinary VTL0 therefore has no read, write or execute access;
- trusted VTL1 components can still open/map the object by its secure identity;
- the external object is not CP_CAMERA assigned;
- the separate internal hardware target adds CP_CAMERA VMID `0x0d`, write permission `0x2`.

E004cd evaluates Linux candidates against that observable security shape instead of against names such as `secure`, `reserved`, or `protected`.

## 1. Qualcomm ASSIGN can replace the HLOS owner set

Linux `qcom_scm_assign_mem()` is explicitly documented as a **memory ownership reassignment** interface.

Its inputs are:

- the current owner VMID bitmask;
- an arbitrary array of next-owner VMIDs;
- a permission value for every next owner.

After a successful secure call Linux replaces `*srcvm` with the newly constructed owner mask.

So, as a mechanism, ASSIGN is capable of expressing:

`HLOS -> secure owner set without HLOS`

and it supports more than one destination owner.

That is materially stronger than SHM bridge, which E004bz proved is sharing metadata/lifetime registration rather than ownership revocation.

### What is missing

No current Linux driver callsite in this Golden tree constructs a camera assignment using:

- `QCOM_SCM_VMID_HLOS_FREE`;
- `QCOM_SCM_VMID_TZ`;
- `QCOM_SCM_VMID_CP_CAMERA`;
- `QCOM_SCM_VMID_CP_CAMERA_PREVIEW`.

The constants exist, but there is no camera policy helper defining a valid external-sample owner set.

E004ca additionally proves that assigning the **external** sample to CP_CAMERA would be wrong: Windows only applies CP_CAMERA to the distinct internal capture target.

## 2. Generic TEE protected DMA-BUF is the right HLOS-facing surface

`drivers/tee/tee_heap.c` already implements a protected DMA-BUF heap abstraction with:

- allocation/free through an abstract protected-memory pool;
- DMA attach/detach;
- DMA map/unmap with `DMA_ATTR_SKIP_CPU_SYNC`;
- **no** normal `mmap`;
- **no** `vmap`;
- **no** CPU begin/end access callbacks.

This is a good surface match for E004bw/E004cc: userspace and ordinary HLOS code should not receive a CPU mapping of the protected sample.

The backend interface is intentionally small:

- `alloc()`;
- `free()`;
- `update_shm()`;
- `destroy_pool()`.

So a Qualcomm-specific protected-memory backend would not require inventing a new DMA-BUF framework.

## 3. A heap wrapper is not the security provider

The generic static protected pool is only allocation bookkeeping over a supplied physical range. It does not itself revoke HLOS ownership or establish secure-world visibility.

OP-TEE's dynamic protected-memory provider demonstrates what a real backend must do. Its source states that after `lend_protmem()` the physical memory becomes **inaccessible** and, where a hypervisor exists, the intermediate physical mapping is removed.

That security transition is provided by the trusted runtime, not by the heap name.

On SP11:

- OP-TEE is not the platform trusted OS used by the camera path;
- no OP-TEE runtime is active;
- OP-TEE provider code registers secure-video playback, not camera record;
- QCOMTEE has no `tee_protmem_pool` or protected DMA-heap provider at all.

Therefore `protected,secure-video-record` cannot honestly be registered until a Qualcomm backend with real secure ownership/lifetime semantics exists.

## 4. pKVM has strong host isolation but is not a camera provider

The kernel contains pKVM support. Its documentation states that protected-VM pages are removed from the host stage-2 identity map, and host access to unshared pVM memory faults.

That is genuinely VTL-like CPU isolation.

But it is not usable for this camera path:

1. Golden is **not** booted with `kvm-arm.mode=protected`; that mode is an early boot selection.
2. pKVM's own documentation marks **DMA isolation using an IOMMU as unimplemented**.
3. Its page donation interfaces are part of protected-VM/hypervisor ownership flows, not a general protected DMA heap for CAMSS.
4. There is no proven way to give a pVM trusted access to the CP_CAMERA internal target without first exposing/re-owning that memory through HLOS.

Using pKVM would therefore replace one missing provider with an even larger unproven architecture and would not currently meet camera DMA isolation requirements.

## 5. FF-A has donation/lend primitives but no camera secure partition

The tree contains ARM FF-A memory share/lend/donate transport and Golden builds the FF-A transport as a module.

However no camera secure-partition identity or signed FF-A worker is known on this machine. Loading/probing FF-A just to discover endpoints would cross the secure-runtime boundary and is outside E004cd.

A generic transport cannot substitute for the missing trusted camera service.

## 6. Gunyah exists in the platform layout but is not host-controlled here

The SP11 device tree reserves:

`gunyah-hyp@80000000`

and the kernel tree contains an X1 EL2 overlay whose comments explicitly distinguish operation **under Gunyah** from Linux taking ownership in EL2.

That proves Gunyah is part of the X1 platform architecture.

But current Golden has:

- no `CONFIG_GUNYAH` / Gunyah host driver configuration;
- no `drivers/virt/gunyah` implementation in this source tree;
- no `/dev/gunyah` or equivalent host control device;
- no live DT Gunyah interface beyond the reserved firmware region.

So Gunyah cannot currently provide the missing protected worker from this Linux stack.

## 7. Same-machine trusted-worker authority remains absent

The cumulative exact-machine evidence is consistent:

- E004br: Windows final protected transfer executes in the VTL1 `QcISPTrustlet8380.dll` itself.
- E004bs: current Linux QCOMTEE source has no known camera service UID.
- E004by: camera components do not use QcTrEE MemSharing or Invoke; those are generic transports.
- E004cb: Qualcomm `pil_camera_mem_assign` / VMID `0x39` is camera **firmware/PIL handoff**, not per-frame protected-sample processing.
- the SecureISP package's `libbitml_nsp_v2_skel.so` is Hexagon/DSP code and has no proven role as the final protected-frame worker.

The exact same-machine camera secure payload inventory therefore contains no signed Qualcomm TEE application that can be named as the Linux counterpart of the Windows VTL1 transfer worker.

This is the central blocker.

## Candidate matrix

| Candidate | Revoke normal HLOS CPU access | Trusted worker retains access | Camera authority known | DMA/camera suitability | Result |
|---|---:|---:|---:|---:|---|
| ordinary system/CMA heap | No | HLOS only | No | ordinary DMA | reject |
| SHM bridge | No ownership revocation | secure sharing only | No | generic | reject alone |
| QCOM SCM ASSIGN | **Yes, owner set can exclude HLOS** | only if a valid secure owner is known | **No external camera owner known** | low-level primitive | useful half |
| generic TEE protected DMA-BUF | surface only | backend-dependent | no X1E record backend | good façade | useful half |
| OP-TEE protmem | Yes by trusted lend | OP-TEE | not X1E camera authority | playback provider only | reject |
| QCOMTEE | ordinary shared memory only today | QTEE objects | no camera UID/provider | no protmem backend | incomplete |
| pKVM protected VM | Yes | pVM | no camera worker | DMA isolation unimplemented | reject |
| FF-A secure partition | potentially via lend/donate | secure partition | no camera SP known | transport only | unresolved/absent |
| Gunyah guest | potentially | guest | no host API/worker here | not available in Golden | absent |

## Feasible Linux architecture — in principle

The smallest architecture that would match the Windows **observable** contract is:

1. allocate pages through a protected-memory backend;
2. remove ordinary HLOS from the hardware-enforced owner/access set;
3. grant access to a **proven trusted worker identity**;
4. expose the object through the generic protected DMA-BUF surface with no CPU map callbacks;
5. let that trusted worker serialize metadata and copy/process pixels into the external sample;
6. restore ownership only after the protected object lifetime ends.

Qualcomm ASSIGN plus the generic TEE protected-DMA-BUF framework can supply much of the host-side plumbing.

The unresolved item is step 3: **which trusted execution identity is allowed to own/map the pages and execute the worker?**

Until that identity exists, implementing steps 1/2/4 alone would create a buffer that either nobody can fill or that must be reopened to HLOS, defeating the protection contract.

## Windows oracle decision

A Windows one-shot is not justified at this gate.

Windows behavior is no longer ambiguous: E004cc proves VTL0 no-access and the exact trusted worker is already statically identified. A Windows trace cannot manufacture a Linux secure-world service or Gunyah/QTEE endpoint that is absent from Linux and same-machine firmware authority.

Use the Windows oracle again when there is a concrete behavior question whose answer can change a Linux implementation decision.

## What remains forbidden

Do not yet:

- call `qcom_scm_assign_mem()` for an external camera sample;
- guess TZ, HLOS_FREE, QTEE or another VMID as the trusted owner;
- register a fake `protected,secure-video-record` heap;
- enable/probe QCOMTEE, FF-A, OP-TEE or Gunyah for endpoint discovery;
- boot pKVM merely to experiment with protected pages;
- temporarily remap protected external samples into normal HLOS for the transfer worker;
- use CP_CAMERA assignment for the external sample;
- activate Linux SecureISP protected runtime.

## Next gate

Proceed to **E004ce — compile-only protected-provider capability gate**.

Encode, with zero runtime effect, the provider properties that must be true before CAMSS can ever bind a protected external-sample backend:

1. hardware-enforced HLOS CPU access revoked;
2. concrete trusted-owner identity resolved;
3. trusted worker mapping/lifetime resolved;
4. reverse ownership/release path resolved;
5. no HLOS transfer fallback;
6. external sample remains distinct from the CP_CAMERA internal target.

The compile contract should reject/mark incomplete any backend that only supplies CMA, SHM bridge, CP_CAMERA assignment, or an opaque heap name. It must not contain a VMID, service UID, SCM call or runtime selector until authority is found.
