# E004ci — protected guest/partition worker visibility feasibility

## Result

**PASS (negative feasibility gate): neither the current pKVM protected-guest path nor the current FF-A partition path provides an authoritative way to keep a CPU worker visible to the same backing while CP_CAMERA remains active. pKVM guest ownership is architectural stage-2 state with no Qualcomm/QHEE owner binding, and FF-A is transport to an already-existing partition whose camera identity/policy is unknown.**

No protected VM, FF-A call, partition probe, QTEE/QSEE call, SCM assignment, camera runtime or Windows reboot occurred.

## 1. pKVM protected guest solves host isolation, not Qualcomm camera ownership

`__pkvm_host_donate_guest()` can remove a page from the host stage-2 and map it into a protected guest:

- host page must be `PKVM_PAGE_OWNED`;
- guest IPA must be `PKVM_NOPAGE`;
- host metadata is changed to `PKVM_ID_GUEST`;
- the guest stage-2 receives an RWX `PKVM_PAGE_OWNED` mapping.

That is a real architectural CPU isolation boundary.

But the entire arm64 KVM/pKVM tree contains **no**:

- `qcom_scm_assign_mem()` integration;
- `QCOM_SCM_VMID_CP_CAMERA` integration;
- QHEE/AC_VM mapping for guest ownership;
- `HYP_MEM_PROTECT_ASSIGN` platform glue.

Therefore `PKVM_ID_GUEST` is not evidence of a Qualcomm memory-owner identity that can coexist with CP_CAMERA.

## 2. Guest stage-2 visibility cannot substitute for QHEE authority

The Windows oracle's internal target is not protected by stage-2 alone. It has:

- a trusted VTL1 CPU mapping;
- a live Qualcomm CP_CAMERA assignment on the same backing.

A Linux protected guest could map a physical page in its own stage-2, but E004ci finds no source path proving that guest CPU access remains valid once the physical range is assigned into a Qualcomm camera owner set.

The converse is also true: assigning the physical range to CP_CAMERA does not automatically tell pKVM which guest should retain CPU access.

So the two ownership systems are currently unbound.

## 3. pKVM DMA/device isolation is not ready to close the gap

The pKVM documentation in this exact kernel marks DMA isolation using an IOMMU as:

**Unimplemented.**

That matters for a camera design because protected CPU ownership alone is insufficient when a device must DMA into the same backing.

A future architecture could potentially integrate device assignment with protected guests, but that infrastructure is not present here today.

## 4. FF-A is a memory transport to an existing secure partition

pKVM's FF-A proxy supports memory sharing/lending flows and protects pKVM/hypervisor pages from being exposed by a confused host.

The host-side page state transition for FF-A is explicit:

`PKVM_PAGE_OWNED -> PKVM_PAGE_SHARED_OWNED`

and reversed on unshare.

This proves useful transport semantics, but FF-A still needs a real secure partition endpoint.

The generic Linux FF-A driver discovers partitions at runtime by UUID/partition information. E004ci finds no X1E camera secure-partition UUID, driver binding or static service identity that can serve as the protected frame worker.

No runtime partition enumeration/probe was performed.

## 5. Why neither candidate satisfies E004bt

E004bt requires the same internal backing to be simultaneously:

- writable by CP_CAMERA hardware;
- readable by a trusted CPU worker;
- inaccessible to ordinary HLOS CPU code.

### Protected guest

Known:

- can isolate CPU pages from host;
- can execute our own worker code.

Missing:

- Qualcomm owner identity for guest CPU access;
- camera DMA/device integration;
- authority for simultaneous CP_CAMERA + guest visibility.

### FF-A secure partition

Known:

- can share/lend memory to a pre-existing secure partition;
- pKVM mediates host/secure-world sharing.

Missing:

- a camera worker partition identity;
- proof that its memory-access identity may coexist with CP_CAMERA;
- signed worker/provider implementation.

Neither candidate meets the overlap gate.

## 6. Current architecture status

The search has now eliminated the obvious source-controlled habitats:

- direct pKVM HYP worker: executable, but HYP co-ownership conflicts with QcSk policy;
- pKVM protected guest: no Qualcomm owner/device binding;
- FF-A partition: no identified camera partition/provider;
- QCOMTEE/QSEE: only existing signed services/apps can execute and no camera service identity is known;
- Gunyah: no local host control stack.

This strongly suggests the missing parity component is a **platform secure-world/VTL-style provider**, not ordinary Linux camera-driver code.

## 7. Windows one-shot decision

A Windows one-shot is **not yet needed** for E004ci.

The Windows side of the relevant contract is already unambiguous:

- CP_CAMERA assignment remains live;
- trusted worker mapping remains live;
- worker executes while both exist.

What is missing is Linux/platform authority, which a Windows trace cannot manufacture.

A one-shot becomes worthwhile only if we need a dynamic answer about a Windows identity or transition that static evidence cannot resolve.

## What remains forbidden

Do not yet:

- boot a protected VM/pKVM mode for camera work;
- attach CAMSS to a protected guest;
- perform VFIO/IOMMU camera assignment;
- call FF-A memory lend/share for camera pages;
- probe arbitrary secure-partition UUIDs;
- enable QCOMTEE/QSEE;
- time-multiplex CP_CAMERA ownership;
- activate Linux protected camera runtime.

## Next gate

**E004cj — platform secure-worker authority closure**, static-first.

Rather than search more generic execution habitats, pivot back to same-machine platform authority and determine whether any signed Secure Kernel/QcSk/QTEE component already exposes a reusable protected-memory CPU service distinct from exclusive HYP:

1. enumerate QcSk secure-memory services and their client identities beyond PIL/HYP;
2. search exact SP11 Windows binaries for components that combine `OpenSecureSection`/secure mapping with CPU processing but no exclusive HYP assignment;
3. correlate those consumers with QcTrEE/QTEE service GUIDs/UIDs where possible;
4. look for a generic secure-copy/secure-buffer service rather than a camera-specific name;
5. only if static authority still closes, use a Windows one-shot trace targeted at the specific unresolved service boundary.
