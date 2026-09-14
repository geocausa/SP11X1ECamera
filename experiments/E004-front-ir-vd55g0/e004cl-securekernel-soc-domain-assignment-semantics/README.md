# E004cl — Secure Kernel SoC-domain assignment semantics

## Result

**PASS / architecture correction: the Windows camera internal target does not become a CP_CAMERA physical-page owner through `IumAssignMemoryToSocDomain`. The exact Secure Kernel implementation keeps the backing as a protected Secure-Kernel section and creates a separate Hyper-V device-GPA mapping into IO domain `0x0d`. The returned assignment handle owns that device mapping and unmaps it on close.**

This supersedes the earlier E004ca/E004ck interpretation that the frame target's IUM assignment was a raw Qualcomm VMID ownership replacement.

No runtime action occurred. SP11 remained on Golden Linux; no pKVM boot, Windows boot, IUM call, Hyper-V call, SMMU operation, SCM assignment, QTEE/QSEE call or camera runtime was performed.

## Exact authority

The exact mounted `securekernel.exe` and matching Microsoft public PDB used in E004cc expose:

- `IumAssignMemoryToSocDomain`;
- `SkhalValidateProcessIoDomain`;
- `SkmmReferenceSecureSection`;
- `SkmmProbeSecureSectionPages`;
- `ShvlMapSparseDeviceGpaPages`;
- `ShvlUnmapSparseDeviceGpaPages`;
- `SkhalpDeleteDomainAssignment`.

That gives us the complete frame-target assignment lifetime below the IUM API.

## 1. Camera API parameter map

The SecureISP trustlet calls the user-facing IUM API with the already-proven shape:

`AssignMemoryToSocDomain(section, page_array, page_offset, page_count, io_domain, protection, flags)`

For the internal camera target:

- IO domain = `0x0d`;
- protection = `4`;
- flags = `0`.

`iumbase.dll` prepends an output assignment-handle pointer before entering `IumAssignMemoryToSocDomain`, so Secure Kernel sees:

- `param_1` — output assignment handle;
- `param_2` — secure-section handle;
- `param_3` — optional caller page/IPA array;
- `param_4` — page offset;
- `param_5` — page count;
- `param_6` — IO domain;
- `param_7` — protection;
- `param_8` — flags.

## 2. The Secure Kernel validates the device domain against process policy

`IumAssignMemoryToSocDomain` first calls:

`SkhalValidateProcessIoDomain(process_policy, io_domain)`

The recovered implementation walks the secure process policy's IO-domain table and returns success only when an entry exactly matches the requested domain.

Thus `0x0d` is not merely a guessed Qualcomm constant here. It is an IO-domain identity that the SecureISP isolated process must be explicitly authorized to use.

This is an important difference from ordinary HLOS DMA mapping: the trusted process policy itself gates which device domain may receive the mapping.

## 3. The secure-section backing remains the source of truth

After domain validation, Secure Kernel:

1. creates a domain-assignment object;
2. references the existing secure-section object with `SkmmReferenceSecureSection`;
3. checks the requested page range against the section;
4. builds/probes the secure section's PFN/GPA list through `SkmmProbeSecureSectionPages`.

It does **not** release the secure section, expose it to VTL0, or replace its protected-page lifetime.

The trusted CPU mapping proven in E004cc therefore remains backed by the same Secure-Kernel-owned pages.

## 4. The actual operation is `ShvlMapSparseDeviceGpaPages`

The decisive call is:

`ShvlMapSparseDeviceGpaPages(...)`

The function constructs a sparse device mapping request from the secure section's page list and issues Hyper-V fast hypercall:

`199 / 0xC7`.

The inverse path uses:

`ShvlUnmapSparseDeviceGpaPages(...)`

with Hyper-V hypercall:

`200 / 0xC8`.

The PDB function names are authoritative about the semantic layer: these calls map/unmap **device GPA pages**. They are not page-ownership donation calls.

## 5. Protection value 4 means device R/W, not write-only page ownership

`IumAssignMemoryToSocDomain` translates the IUM protection argument as:

| IUM protection | Device-GPA flags |
|---:|---:|
| `2` | `0x1` |
| `4` | `0x3` |
| `0x20` | `0x0d` |
| `0x40` | `0x0f` |

That pattern matches the ordinary Windows protection classes, with the camera's value `4` becoming device-GPA **read + write** flags `0x3`.

Therefore the earlier statement that camera `Protection=4` became Qualcomm write-only permission `0x2` was from a different QcSkExt assignment path and is **not** the frame-buffer oracle.

## 6. Assignment handle lifetime is exactly the device mapping lifetime

`IumAssignMemoryToSocDomain` creates and returns a Secure Kernel object handle for the mapping.

When that handle is closed, its delete callback is:

`SkhalpDeleteDomainAssignment`

which calls:

`ShvlUnmapSparseDeviceGpaPages`.

Only after the device pages are unmapped does it free the assignment metadata and dereference the secure section.

This matches the trustlet release order already observed:

1. close assignment handle;
2. free page-address metadata;
3. unmap trusted CPU view;
4. close secure-section handle.

So the Windows contract is now completely coherent:

**trusted CPU mapping lifetime** and **device-GPA mapping lifetime** overlap, but are independent objects over the same protected backing.

## 7. What QcSkExt still proves — and what it no longer proves for this path

`QcSkExt8380.exe` remains authoritative for its own Qualcomm Secure-Kernel extension workflows, including:

- PIL camera firmware handoff;
- HYP assignment policy;
- AC_VM_HYP exclusivity;
- platform memory-assignment rules.

But the exact Secure Kernel implementation of the camera trustlet's IUM SVC does not call the QcSkExt `QcSkAssignMemoryToSocDomain` path.

Therefore E004cl supersedes these frame-target interpretations from earlier checkpoints:

- **superseded:** the internal capture pages become Qualcomm `CP_CAMERA` physical owners;
- **superseded:** camera `Protection=4` means Qualcomm write-only permission `0x2` for this frame target;
- **superseded:** a Linux implementation must reproduce a `{CP_CAMERA, trusted CPU owner}` physical-owner set.

The corrected frame-target model is:

**Secure-Kernel/VTL1 protected pages**

plus

**policy-authorized Hyper-V device-GPA mapping into IO domain `0x0d`, R/W**.

## 8. This reopens pKVM conceptually

E004ck closed pKVM under the assumption that Linux needed a Qualcomm physical ownership set containing both camera hardware and a trusted CPU domain.

That assumption is no longer the Windows oracle.

A closer Linux analogue can instead be:

1. pages owned/mapped only by a trusted pKVM/nVHE context;
2. ordinary HLOS CPU access revoked;
3. a separate trusted IOMMU/SMMU mapping grants CAMSS device DMA access to those pages;
4. mapping lifetime is explicitly bracketed and revoked before page release;
5. HLOS cannot reprogram the mapping or map the same protected pages to another device.

This is much closer to Windows' two-plane architecture.

## 9. Current blocker: trusted DMA/SMMU control

The current Linux source has the first half:

- pKVM host/hyp page ownership and donation primitives;
- source-controlled trusted CPU execution;
- compile-proven worker ABI.

CAMSS already consumes DMA addresses through standard VB2 SG mappings.

But the current pKVM/nVHE tree has **no trusted IOMMU/DMA ownership implementation** connecting hyp-owned pages to a device while preventing a hostile HLOS from altering the mapping.

E004cd had already marked pKVM DMA isolation as unimplemented. E004cl now shows that this is not a secondary hardening detail — it is the precise missing parity primitive.

Using normal HLOS `iommu_map()`/DMA mapping for hyp-owned protected pages would not be enough, because a compromised HLOS would still control the DMA translation/security boundary.

## Architectural consequence

The protected internal-target problem has narrowed significantly.

We no longer need to discover a mysterious trusted CPU VMID or make QCOMTEE own the frame buffer.

We need a Linux implementation equivalent to:

`protected trusted pages + trusted device-GPA mapping + independent lifetimes`.

That is an implementable architecture in principle, but it requires a trustworthy SMMU/IOMMU control point.

## What remains forbidden

Do not yet:

- call `qcom_scm_assign_mem()` for the frame target based on the old model;
- attempt `CP_CAMERA + HYP` owner combinations;
- boot pKVM for camera runtime;
- map hyp-owned pages through ordinary host-controlled DMA and call it protected;
- change SMMU programming at runtime;
- activate Linux protected camera runtime.

## Next gate

**E004cm — trusted CAMSS device-GPA/SMMU mapping feasibility**, static/compile-only first.

Goals:

1. trace the current CAMSS/VB2/IOMMU mapping path on X1E from buffer SG table to IFE DMA address;
2. identify the exact Arm SMMU instance/context used by CAMSS and which layer controls its page tables;
3. determine whether the platform/QHEE exposes an existing secure device-mapping API Linux can use without giving HLOS page access;
4. inspect pKVM for any extensible IOMMU ownership hooks or protected-device groundwork, including downstream/local branches;
5. define a compile-only provider boundary that mirrors Windows `MapSparseDeviceGpaPages` / assignment-handle lifetime;
6. use the Windows one-shot only if device-domain identity or mapping lifetime cannot be resolved statically.
