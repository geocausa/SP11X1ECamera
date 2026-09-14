# E004ck — VTL trusted-CPU visibility versus Qualcomm device-domain ownership

## Result

**PASS: Windows' trusted CPU visibility is orthogonal to the Qualcomm CP_CAMERA device-domain ACL. The SecureISP trustlet keeps a Hyper-V/Secure-Kernel VTL1 mapping while the same backing is assigned only to CP_CAMERA for hardware writes. On this X1E platform, non-secure EL2/HYP access is separately mediated by Qualcomm's HYP_ASSIGN / AC_VM_HYP policy, and that HYP destination is exclusive. Current Linux pKVM therefore has no parity-safe ownership combination for the Windows internal protected target.**

This is a static/read-only gate. No pKVM boot, HYP assignment, CP_CAMERA assignment, Windows boot, QTEE/QSEE call or camera runtime occurred.

## 1. Windows uses two independent protection planes

The exact Windows internal target lifetime is already mechanically proven:

1. `CreateSecureSection(NULL, 4, 4, size, 2)` creates Secure-Kernel backing;
2. the VTL1 SecureISP trustlet maps that section and retains the VA at object `+0x30`;
3. `AssignMemoryToSocDomain(..., DomainId=0x0d, Protection=4, ...)` creates the camera-device assignment;
4. the IFE writes while the assignment handle remains live;
5. the VTL1 CPU worker later reads through the still-live `+0x30` mapping;
6. teardown closes the assignment handle before unmapping the trustlet VA.

E004ca/QcSkExt proves the assignment reaches Qualcomm as:

- VMID `0x0d` = `CP_CAMERA`;
- permission `0x2` = write.

There is no extra Qualcomm destination entry representing the VTL1 CPU worker.

Separately, E004cc proves the section pages are protected by Hyper-V's `HvCallModifyVtlProtectionMask`: the durable lower-VTL/VTL0 permission mask is zero, while Secure Kernel can map the same pages into an authorized VTL1 process.

Therefore Windows does **not** implement trusted CPU access as:

`Qualcomm { CP_CAMERA, CPU-worker-VMID }`

It implements:

`Hyper-V/Secure-Kernel trusted CPU mapping`

plus, independently,

`Qualcomm CP_CAMERA device write assignment`.

## 2. Qualcomm HYP is a separate explicit domain

QcSkExt treats destination VMID 4 as the platform HYP domain.

Its strings and branches explicitly name:

- `AC_VM_HYP`;
- `HYP_ASSIGN`;
- memory mapped to the `HYP VM`.

The assignment engine enforces that when HYP is a destination:

- the destination count must be exactly one;
- the region must have the required mapped backing;
- sharing HYP with another destination is rejected.

The exact diagnostic is:

`Invalid assignment, assignment to HYP domain cannot be shared with other domains or memory region not mapped into view.`

Thus `{ CP_CAMERA, HYP }` is not an authorized Qualcomm destination set on this policy path.

## 3. Same-machine QHEE firmware confirms EL2/HYP memory is access-controlled

Recovered same-machine Qualcomm hypervisor image:

SHA-256:

`cc33b7c0d902f0aafd64d3d866899401af7d4e0ad1c9ffc1cc97555d9a6bd78a`

It is an AArch64 static PIE hypervisor image and contains source-bearing diagnostics for:

- `hyp/platform/qhee/src/qhee_hyp_assign.c`;
- `platform/qcom/src/hyp_assign/hyp_assign.c`;
- `HYP_ASSIGN` source/destination validation;
- `Failed to create AC_VM_HYP VM`;
- `hyp_manager_map_memory_hlos_to_el2`;
- `hyp_manager_map_memory_el2_to_hlos`;
- `Failure mapping memory from HLOS to HYP VM`;
- `VTTBR_EL2_get_VMID(&vttbr) == QHEE_VMID_HLOS`;
- `pil_camera_mem_assign`;
- Camera Preview S2/SMMU handling;
- camera protected-zone validation.

This is decisive for the architectural boundary: EL2/HYP mappings on the platform are themselves a Qualcomm-hypervisor-managed access class. EL2 is not an unconditional physical-memory bypass around QHEE ownership policy.

## 4. Why pKVM stage-2 isolation is not the Windows VTL1 privilege

Linux pKVM has real host/hyp page-state machinery:

- host-owned;
- host/hyp shared;
- hyp-owned/donated;
- return/reclaim transitions.

That machinery controls the Linux host versus nVHE EL2 stage-2 relationship.

What it does **not** currently provide is an integration that tells the underlying Qualcomm access-control plane:

> keep this CPU mapping privileged while the physical backing is owned by CP_CAMERA and ordinary HLOS is excluded.

No current SP11 Linux callsite binds pKVM's hyp-owned page state to a Qualcomm camera-capable VMID or to the Windows-style VTL1 privilege.

So a pre-existing pKVM mapping cannot be assumed to survive a later CP_CAMERA ownership transition.

## 5. Candidate ownership combinations

### A. `CP_CAMERA` only + pKVM mapping

This most closely matches the Qualcomm destination list on Windows.

But Linux has no proven mechanism by which nVHE/pKVM CPU accesses remain allowed after HLOS is removed from the Qualcomm owner set. Same-machine QHEE instead has explicit HYP mapping/assignment machinery.

**Status: not authorized.**

### B. `CP_CAMERA + AC_VM_HYP`

This would make the Linux worker a Qualcomm destination owner.

QcSk explicitly rejects HYP sharing with another destination.

**Status: policy-rejected.**

### C. `HLOS + CP_CAMERA`, with pKVM denying EL1 CPU mappings

This is mechanically expressible through `qcom_scm_assign_mem()` and would let the non-secure CPU access class remain admitted at the Qualcomm layer.

It is **not** security-equivalent to Windows today:

- Windows gives VTL0 no page access at all;
- HLOS ownership is a broader platform access class than one pKVM CPU mapping;
- current pKVM on this tree does not implement the device/DMA isolation needed to treat a hostile HLOS kernel as unable to reach the backing through another non-secure master.

Keeping HLOS as a Qualcomm owner would therefore weaken the Windows protection contract.

**Status: reject for parity.**

### D. Protected guest / FF-A partition + CP_CAMERA

E004ci already proved that the current tree has no Qualcomm owner binding or camera-DMA binding for such a guest/partition.

**Status: no binding.**

## 6. Consequence for the pKVM candidate

E004cg ranked pKVM as the best **source-controlled CPU habitat** because we can compile our own worker into nVHE.

E004ch proved that code can be built at the correct EL2 boundary.

E004ck now closes the missing ownership question:

**pKVM is not a selectable protected-camera backend on the current SP11 stack.**

The blocker is not CPU code execution. The blocker is physical-memory authority across two independent security planes:

- Linux/pKVM stage-2 ownership;
- Qualcomm/QHEE device-domain ownership.

Windows has a special VTL1/Secure-Kernel mapping privilege that coexists with CP_CAMERA without becoming a Qualcomm destination owner. No equivalent Linux authority has been identified.

## 7. What is still useful from pKVM

The compile-only work is not wasted. It established:

- the trusted worker is portable CPU code;
- a host↔trusted-worker ABI can be compiled cleanly;
- the CAMSS provider gate now correctly requires simultaneous hardware/worker visibility;
- any future provider can reuse that worker contract if a real trusted mapping authority is found.

But runtime pKVM activation would not answer the ownership problem and remains unauthorized.

## What remains forbidden

Do not:

- boot pKVM for camera testing;
- attempt `CP_CAMERA + HYP`;
- retain HLOS as an owner and call it Windows-equivalent protection;
- assume a donated pKVM page bypasses QHEE;
- invoke raw HYP_ASSIGN/SCM ownership transitions;
- enable QCOMTEE/QSEE as a substitute;
- activate protected camera runtime.

## Next gate

**E004cl — Qualcomm HypX / protected-hypervisor extension authority**, static first.

The recovered same-machine QHEE image exposes a richer platform mechanism than Linux pKVM:

- `HypX` image launch/relocation;
- authenticated hypervisor-extension management;
- explicit HLOS↔EL2 memory mapping;
- `AC_VM_HYP` creation;
- camera and protected-zone policy in the same platform hypervisor.

Determine whether HypX is merely Qualcomm/Windows platform infrastructure or whether it exposes a reusable signed extension/service model capable of a camera trusted CPU worker **without** violating HYP exclusivity. Specifically:

1. identify the Windows-side HypX launch client and signed payloads;
2. determine what authentication/root-of-trust controls extension loading;
3. determine whether HypX code executes as `AC_VM_HYP` or another privileged context;
4. check whether any installed HypX workload has a secure-section/VTL-like protected mapping primitive;
5. reject it immediately if all HypX memory is necessarily the exclusive HYP owner class;
6. use the Windows one-shot only if static launch/identity evidence becomes ambiguous.
