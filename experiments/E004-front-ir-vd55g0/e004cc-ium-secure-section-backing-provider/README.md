# E004cc — IUM secure-section backing/provider path below CreateSecureSection

## Result

**PASS: Windows external protected camera samples are backed by Secure Kernel physical pages whose final Hyper-V protection mask for VTL0 is `0` — no read, write, or execute access. `CreateSecureSection(..., flags=0)` therefore establishes a real hypervisor-enforced VTL boundary, not merely an object ACL or software convention.**

The internal SecureISP target starts with the same Secure Kernel protected-page mechanism, then `flags=2` additionally claims every page as a trusted page before the already-proven CP_CAMERA VMID `0x0d` / write-only Qualcomm assignment.

This gate is static/read-only. The exact Microsoft public PDB for the mounted `securekernel.exe` was used. No Windows boot, IUM syscall, Hyper-V call, SCM assignment, QTEE/QSEE invocation or camera runtime was performed.

## Exact Secure Kernel authority

Mounted SP11 binary:

`/mnt/windows/Windows/System32/securekernel.exe`

SHA-256:

`9a2eeb0e4a3d76aa9a6bfaf287540f5f1f7562d814e8ecb3c3f6df6b57a557b6`

Its CodeView identity is:

- PDB: `securekernel.pdb`
- GUID: `{0A49C8CF-92C9-F8EC-65C6-D61180FDAE51}`
- age: 1

The exact matching PDB was obtained from Microsoft's public symbol server and loaded successfully in Ghidra.

PDB SHA-256:

`8a7182241511195029a512aad0e0eb2b4799269f76d5f9ee71ccf697f649ca72`

This gives authoritative internal names including:

- `IumCreateSecureSection`;
- `IumOpenSecureSection`;
- `SkmmCreateSecureSection`;
- `SkmiAllocateZeroedPage`;
- `SkmiAllocateSinglePage`;
- `SkmiAllocatePhysicalPage`;
- `SkmiSecurePhysicalPages`;
- `SkmiProtectPlaceholderPages`;
- `ShvlpProtectPages`;
- `SkmiMapViewOfSection`;
- `SkmiClaimTrustedPage`;
- `ShvlModifySparseSpaPageHostAccess`.

## 1. External flag-0 CreateSecureSection allocates Secure Kernel pages

The Windows camera external sample uses:

`CreateSecureSection(descriptor, 4, 4, size, 0)`

At the Secure Kernel boundary, `IumCreateSecureSection` calls:

`SkmmCreateSecureSection(descriptor, 0, size, protection, ...)`

`SkmmCreateSecureSection` creates the section object, allocates its PTE/PFN array and, for ordinary newly-created backing, loops over the section pages calling:

`SkmiAllocateZeroedPage()`

which is:

`SkmiAllocateZeroedPage -> SkmiAllocateSinglePage -> SkmiAllocatePhysicalPage`.

This is not a Qualcomm SHM-bridge allocation and is not a QCOMTEE object. The pages are acquired into the Windows Secure Kernel memory manager.

## 2. Physical pages are explicitly converted to Secure Kernel pages

For the default section-page allocation class (`class 0`), `SkmiAllocatePhysicalPage` may obtain a PFN from normal mode, but before making it available to the section it calls:

`SkmiSecurePhysicalPages(PFN, 1, access_index, page_access_class)`.

For this exact default path:

- allocation class passed by `SkmiAllocateSinglePage` = `0`;
- `local_e8` / secure VTL access index therefore remains `0`;
- `SkmiPageAccessProtection[0]` is used for the page's internal PFN/access class.

`SkmiSecurePhysicalPages` changes the Secure Kernel PFN state and then calls:

`SkmiProtectPlaceholderPages(PFN, count, access_index, 0)`.

So VTL protection is part of allocation itself; it is not added only when a trusted process later maps the object.

## 3. `SkmiProtectPlaceholderPages` applies the VTL protection

For the normal PFN-list path, `SkmiProtectPlaceholderPages` does three important things:

1. applies a temporary protection mask using `ShvlpProtectPages`;
2. maps and scrubs the page through Secure Kernel hyperspace;
3. applies the final access mask from:

`SkmiVtlPageAccess[access_index]`.

The exact table begins:

| Access index | Protection mask |
|---:|---:|
| 0 | `0x0` |
| 1 | `0x1` |
| 2 | `0x0d` |
| 3 | `0x11` |
| 4 | `0x1` |

The ordinary secure-section allocation path reaches **index 0**.

Therefore its final protection mask is:

`SkmiVtlPageAccess[0] = 0x0`.

## 4. `ShvlpProtectPages` is exactly HvCallModifyVtlProtectionMask

`ShvlpProtectPages` constructs the hypercall input as:

- offset `+0x00`: partition ID `0xffffffffffffffff`;
- offset `+0x08`: requested protection mask;
- offset `+0x0c`: `0`, the target VTL;
- followed by the GPA/PFN page list.

It issues Hyper-V hypercall code:

`0x000C`.

Microsoft's Hyper-V TLFS names call `0x000C`:

`HvCallModifyVtlProtectionMask`

and documents the same input layout:

- `TargetPartitionId` at `+0x00`;
- `MapFlags` at `+0x08`;
- `TargetVtl` at `+0x0c`;
- page list after the header.

The target here is therefore **VTL0**.

Golden Linux's bundled Hyper-V headers independently give the GPA permission bits:

- `HV_MAP_GPA_PERMISSIONS_NONE = 0x0`;
- `HV_MAP_GPA_READABLE = 0x1`;
- `HV_MAP_GPA_WRITABLE = 0x2`;
- kernel execute `0x4`;
- user execute `0x8`.

The TLFS likewise defines VTL memory protection in terms of lower-VTL read/write/execute access.

Thus the final mask for the external section's pages:

`0x0`

means:

**VTL0 has no read, no write and no execute access.**

This is the physical protection mechanism we had previously left unresolved.

## 5. Temporary mask 1 does not weaken the final state

During page transition/scrubbing, `SkmiProtectPlaceholderPages` first uses the second table value:

`SkmiVtlPageAccess[1] = 0x1`

which is the Hyper-V readable bit.

After the Secure Kernel transition/scrub it applies the requested final access-index value.

For the normal flag-0 secure section, that final value is still:

`SkmiVtlPageAccess[0] = 0`.

Therefore the durable external sample state is VTL0 no-access.

## 6. Trusted consumers map the section in VTL1/Secure Kernel context

`SkmiMapViewOfSection` creates a secure-process virtual allocation and installs the section's PTEs into that secure address space while retaining a reference to the secure-section object.

That matches the camera flow already proven:

- FsIso creates the GUID/scenario secure section;
- SecureISP's VTL1 trustlet opens it by GUID/scenario;
- the trustlet maps it and writes the protected frame payload through its trusted worker.

The object is therefore simultaneously:

- inaccessible to ordinary VTL0;
- mappable in an authorized isolated/trusted VTL1 process.

That is the key external protected-sample security contract.

## 7. Flag 2 adds a second Secure Kernel page class for the internal target

The SecureISP internal target uses:

`CreateSecureSection(NULL, 4, 4, size, 2)`.

`IumCreateSecureSection` first creates the same Secure Kernel section backing described above.

When flags bit `0x2` is present it additionally:

- sets section flag `0x20000`;
- iterates every section PFN;
- calls `SkmiClaimTrustedPage(PFN, NULL, 6)`.

The external FsIso flag-0 sample skips this trusted-page claim loop.

Afterward, the internal target separately performs the already-proven:

`AssignMemoryToSocDomain(... DomainId=0x0d, Protection=4 ...)`

which QcSkExt translates to:

- Qualcomm VMID `0x0d` = `CP_CAMERA`;
- Qualcomm permission `0x2` = write.

So the internal target protection stack is now:

**Secure Kernel / VTL0-no-access section**

plus

**Secure Kernel trusted-page class**

plus

**CP_CAMERA hardware write assignment**.

The external sample uses only the first layer plus its scenario/GUID authorization and trusted-process mapping.

## 8. This resolves the Windows external provider question

The Windows external protected-sample provider is not:

- QcTrEE MemShare;
- QTEE SmcInvoke;
- CP_CAMERA assignment;
- a generic Qualcomm carveout;
- an ordinary Windows section with ACLs.

Its core memory-security mechanism is:

**Microsoft Secure Kernel + Hyper-V VTL protection.**

The camera-specific scenario/GUID determines which isolated components can identify/open the secure-section object; Hyper-V VTL protection prevents ordinary VTL0 software from accessing its pages.

That distinction is important:

- **scenario/GUID = trusted-object authorization / identity**;
- **VTL protection = physical lower-VTL access enforcement**;
- **CP_CAMERA assignment = internal hardware-writer access only**.

## 9. Consequence for Linux parity

Bare-metal Golden Linux does not have Windows VTL1/Secure Kernel providing this external sample service.

Therefore a Linux implementation cannot achieve 1:1 protected-sample semantics merely by:

- allocating CMA/reserved memory;
- adding a SHM bridge;
- assigning pages to CP_CAMERA;
- turning on generic QCOMTEE transport.

A Linux external-sample provider must reproduce the **observable security shape**:

1. normal HLOS CPU cannot map/read/write the backing;
2. an authorized trusted worker can map/process it;
3. the object has independent protected identity and lifetime;
4. the internal camera hardware target remains a separate object;
5. no HLOS memcpy is introduced into the protected path.

The generic protected TEE DMA-BUF framework has the right HLOS-facing abstraction, but E004bx already proved there is currently no X1E secure-video-record provider behind it.

## Windows oracle decision

No one-shot Windows boot was required for E004cc.

The exact mounted Secure Kernel binary, its exact Microsoft PDB and the public Hyper-V TLFS resolve the backing and lower-VTL protection path unambiguously. A dynamic boot would only reconfirm a protection mask whose implementation is now directly visible.

The Windows oracle remains the next choice whenever static evidence becomes ambiguous.

## What remains forbidden

Do not yet:

- weaken the external sample to ordinary HLOS memory;
- use CP_CAMERA assignment as a substitute for external-sample VTL protection;
- expose external backing through CMA `mmap`/`vmap`;
- assume SHM bridge revokes HLOS access;
- enable/probe QCOMTEE by guessed UID;
- invoke a guessed protected-memory service;
- activate Linux SecureISP protected runtime.

## Next gate

The next useful gate is **E004cd — Linux VTL-equivalent protected-sample provider feasibility**, static first.

Now that the Windows contract is exact, evaluate Linux candidates against it rather than against generic labels:

1. determine whether any X1E secure-world/firmware primitive can actually revoke normal HLOS CPU access while retaining a trusted mapping;
2. inspect whether Qualcomm ASSIGN can form an external owner set suitable for a trusted worker without CP_CAMERA;
3. distinguish ownership ACL from QTEE shared memory and SHM bridge;
4. inspect generic TEE protected DMA-BUF provider interfaces for the minimum backend implementation needed;
5. search same-machine firmware and current source for a signed service capable of being that trusted owner/worker;
6. if static identity remains missing, use Windows only for a behavior question it can answer — do not use it to invent a Linux secure-world service that is not present.

No runtime secure call is authorized by E004cd unless a later gate explicitly establishes the service identity and rollback plan.
