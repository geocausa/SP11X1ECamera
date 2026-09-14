# E004cm — trusted CAMSS device GPA / SMMU feasibility through Gunyah/QHEE

## Result

**PASS: the same-machine Gunyah Resource Manager can create protected trusted VMs and can passthrough devices to a firmware-approved static trusted-VM set, but it cannot express the Windows internal protected target as `{trusted worker VM, CP_CAMERA}`. CP_CAMERA is rejected by the RM memparcel ACL namespace, and the QHEE access-control rule table contains zero rules combining CP_CAMERA with the trusted-VM class.**

This is a static/read-only gate. No Gunyah VM, memory parcel, HYP assignment, SMMU reassignment, SCM call, Windows boot or camera runtime occurred.

## 1. The actual same-machine Gunyah RM was recovered from QHEE

The SP11 QHEE image from E004ck/E004cl contains multiple ELF images. At file offset `0x14a5c0` is a complete AArch64 PIE Resource Manager ELF:

- size: `370112` bytes;
- SHA-256: `533c1d629f498b7185275507c516336ef94ed04fff661fd7e9db63c222c98a6d`;
- entry point: `0x12000`.

Its own strings identify:

- `gunyah-resource-manager`;
- `src/memparcel/memparcel.c`;
- `platform/qcom/src/hyp_assign/hyp_assign.c`;
- `src/vm_passthrough_config/vm_passthrough_config.c`;
- `qcom,rm-acl`;
- `vm_device_assignments`.

This is much stronger authority than inferring Gunyah behavior from host documentation.

## 2. Gunyah RM does support real protected guest ownership

The RM has first-class:

- VM allocation/deallocation;
- VMIDs;
- SHARE/LEND/DONATE memory transactions;
- per-VM memparcel ACL entries and access rights;
- protected VM image memparcels;
- virtual SMMU/device passthrough configuration.

So Gunyah is a genuine platform security mechanism rather than a conceptual fallback.

## 3. But RM memparcel ACLs do not accept CP_CAMERA

The memparcel ACL validator only accepts:

- HLOS (`VMID 3`);
- a small fixed trusted/static VMID set;
- RM-allocated dynamic VMIDs in the `0x80+` range;
- a few special platform identities.

For this firmware, the fixed ACL whitelist mask resolves to:

`0x2d, 0x31, 0x32, 0x34, 0x35, 0x36, 0x37`

and additional special cases are handled separately.

`CP_CAMERA = 0x0d` is **not** accepted by that ACL whitelist.

Therefore the simple design:

`memparcel ACL = { trusted guest, CP_CAMERA }`

is not legal in the RM memory-sharing API.

## 4. Static trusted VMs are a distinct QHEE class

QHEE's access-control rule selection normalizes the RM-approved trusted/static VMIDs:

`0x2d, 0x31, 0x32, 0x34, 0x35, 0x36, 0x37, 0x3a`

into one abstract trusted-VM access-control class:

`0x3f`.

This normalization is deliberate: QHEE is explicitly able to write policy rules for "a trusted VM" without hard-coding one individual TVM identity.

That made it possible to test the exact desired policy directly against the firmware rule table.

## 5. QHEE has no CP_CAMERA + trusted-VM assignment rule

The complete 81-bucket QHEE access-control rule table was decoded: 116 rules total.

The exact target mask was:

- source: `HLOS` = `1 << 3`;
- destination: `CP_CAMERA | trusted-VM-class` = `(1 << 0x0d) | (1 << 0x3f)`.

Result:

`TARGET_FOUND=false`

A second exhaustive query searched every rule in every direction for the simultaneous presence of:

- CP_CAMERA bit `0x0d`;
- trusted-VM class bit `0x3f`.

Result:

`RULES_CONTAINING_BOTH_CP_CAMERA_AND_TRUSTED_CLASS=0`

Thus there is no supported two-step or reverse-direction rule either.

## 6. CP_CAMERA does have specific approved co-owner rules

This negative result is not because QHEE forbids all multi-owner camera memory.

The same firmware explicitly contains HLOS-origin rules for:

- `CP_CAMERA` alone;
- `{ CP_CAMERA, CP_CAMERA_PREVIEW (0x1d) }`;
- `{ CP_CAMERA, CP_CDSP (0x2a) }`;
- `{ CP_CAMERA, VMID 0x2e }`.

and matching return-to-HLOS rules.

This is important: QHEE has an explicit camera sharing policy, but **trusted Gunyah VM class 0x3f is not one of its permitted CP_CAMERA peers**.

### VMID 0x2e caution

VMID `0x2e` is present in QHEE metadata as a normal platform access-control domain (`type 0`), not as the RM trusted-VM class (`type 2`). It is not on the RM trusted/static memparcel whitelist and is not normalized to `0x3f`.

Its precise product name remains unresolved, but it is not evidence of a reusable trusted Gunyah CPU worker.

## 7. Direct device passthrough does not rescue parity

The RM also has a trusted-device passthrough mechanism. It is not open-ended:

- the configured VMID must be in the same firmware fixed trusted-VM mask;
- interrupts/devices are supplied by platform `vm_device_assignments` configuration;
- unsupported VMIDs are fatal configuration errors.

This proves QHEE can attach devices/SMMU resources to certain trusted VMs.

However, no same-machine policy binding was found that hands the CAMSS/IFE protected capture context to a trusted VM. More importantly, doing so would replace the Windows architecture:

`HLOS controls camera + CP_CAMERA DMA writes + separate trusted CPU worker`

with a much larger split-driver architecture in which camera DMA ownership is transferred to a guest.

That is not a parity-safe substitution without explicit same-machine authority.

## 8. Linux host-side availability

Golden Linux currently has no Gunyah host/RM driver enabled or exposed.

Qualcomm still publishes a `tech/virt/gunyah` kernel topic branch, but the currently referenced topic tree does not provide a drop-in `drivers/virt/gunyah` subtree matching this Golden kernel. Android/vendor trees exist with Gunyah host modules, so porting is possible in principle, but this does not change the firmware-policy blocker above.

In other words, host-driver availability is **not** the primary blocker. QHEE policy is.

## Architectural consequence

Gunyah is no longer the leading candidate for the Windows protected-frame worker.

The required simultaneous ownership shape:

`camera hardware writer + protected CPU worker + no HLOS access`

cannot be represented as:

`{ CP_CAMERA, Gunyah trusted VM }`

on this firmware.

But E004cm revealed a much more interesting native co-owner rule:

`{ CP_CAMERA, CP_CDSP }`

`CP_CDSP` is a real Qualcomm protected compute domain and is explicitly authorized by the same-machine access-control table to share backing with CP_CAMERA.

That is the next justified target.

## What remains forbidden

Do not yet:

- create a Gunyah VM;
- allocate or share a memparcel;
- attempt a custom VMID allocation;
- call HYP_ASSIGN;
- attach CAMSS SIDs to a guest;
- perform CP_CAMERA assignment;
- enable protected camera runtime.

## Next gate

**E004cn — CP_CAMERA + CP_CDSP trusted-worker feasibility**, static first.

Goals:

1. map the same-machine Linux CDSP remoteproc/FastRPC stack and Golden runtime availability;
2. determine whether CP_CDSP-backed memory can be mapped to a DSP process without retaining HLOS CPU access;
3. identify whether a signed/static CDSP PD or secure compute service can execute the simple trusted frame worker from E004cf;
4. inspect the Windows SecureISP package's Hexagon payloads again in light of the newly proven `{CP_CAMERA, CP_CDSP}` QHEE rule;
5. distinguish `CP_CDSP` protected ownership from ordinary FastRPC shared buffers;
6. reject the path if user-loadable DSP code cannot access CP_CDSP-owned memory without an HLOS mapping.

Stay static/read-only until a concrete executable CDSP worker authority is proven.
