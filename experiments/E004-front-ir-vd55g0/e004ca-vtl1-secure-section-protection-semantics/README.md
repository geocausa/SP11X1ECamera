# E004ca — external VTL1 secure-section protection semantics versus Linux primitives

## Result

**PASS: Windows external protected camera samples are scenario-authorized Isolated User Mode secure-section objects created/opened through the IUM syscall boundary; they are not protected by the CP_CAMERA SoC-domain assignment used for the separate internal hardware target. The secure-kernel/Qualcomm bridge independently confirms the internal target reaches Qualcomm VMID 0x0d with write-only permission.**

This checkpoint is entirely static/read-only. SP11 stayed on Golden Linux. No Windows reboot, IUM call, SCM assignment, QTEE/QSEE call, protected allocation or camera runtime occurred.

## 1. The Windows API stack is a thin path into the IUM syscall boundary

The exact mounted Windows binaries form a direct chain:

`IumSdk.dll -> iumbase.dll -> iumdll.dll -> SVC`

### IumSdk.dll

Exact SHA-256:

`2fd5b8df49ad83ad1181fe4ead77ba484f292210c28a07c4d08f49fbe93d7d2f`

The camera-relevant exports are forwarders into `iumbase`, including:

- `CreateSecureSection`;
- `OpenSecureSection`;
- `CreateSecureSectionSpecifyPages`;
- `AssignMemoryToSocDomain`;
- `FlushSecureSectionBuffers`;
- `MapSecureIo` / `ProtectSecureIo` / `UnmapSecureIo`;
- `GetExposedSecureSection`.

### iumbase.dll

Exact SHA-256:

`fa7e94e0e2260d7b72fa9edecd13f25c3fa40a32788efd342ce02dbfe15413ee`

`iumbase` imports the corresponding `Ium*` entry points from `IUMDLL.dll`. Its wrappers mainly marshal an output handle plus the original arguments and translate failure status into Win32-style return values.

For `CreateSecureSection`, the wrapper sends the secure syscall:

- output-handle pointer;
- descriptor pointer;
- size;
- the two protection/access arguments;
- flags.

`AssignMemoryToSocDomain` has a separate wrapper and separate returned assignment handle.

### iumdll.dll

Exact SHA-256:

`3fefa86c3b0bdc5aa863099ffcfe658366a8bbf202bdab9fb67be9da9c39b152`

The relevant exports are literal two-instruction ARM64 SVC stubs:

- `IumAssignMemoryToSocDomain` -> `svc #0x8000`;
- `IumCreateSecureSection` -> `svc #0x8003`;
- `IumCreateSecureSectionSpecifyPages` -> `svc #0x8004`;
- `IumFlushSecureSectionBuffers` -> `svc #0x8008`;
- `IumGetExposedSecureSection` -> `svc #0x800a`;
- `IumMapSecureIo` -> `svc #0x800c`;
- `IumOpenSecureSection` -> `svc #0x800e`;
- `IumProtectSecureIo` -> `svc #0x8010`;
- `IumUnmapSecureIo` -> `svc #0x8016`.

So secure-section creation/open and SoC-domain assignment are distinct IUM kernel operations by construction.

## 2. External camera sample: scenario/GUID secure section, no CP_CAMERA assignment

FsIso's camera RPC path creates the external sample with:

`CreateSecureSection(&descriptor, 4, 4, size, 0)`

The 0x24-byte descriptor contains:

- its structure length;
- the per-buffer secure GUID;
- fixed scenario GUID `AE53FC6E-8D89-4488-9D2E-4D008731C5FD`.

That exact scenario is also embedded in FsIso's trusted-process policy.

The FsIso external creation path contains **no `AssignMemoryToSocDomain` call**.

The same shape is independently present in `SecureUSBVideo.dll`: it creates a random buffer GUID, combines it with a fixed scenario descriptor, calls:

`CreateSecureSection(&descriptor, 4, 4, size, 0)`

then maps the returned secure section in its trusted context.

That is strong static authority that a GUID/scenario secure section is already a protected IUM object before any Qualcomm camera-domain assignment is involved.

## 3. Trusted consumers open the same protected object by identity

The SecureISP VTL1 trustlet receives the per-buffer GUID through the Windows camera metadata chain and reconstructs an `OpenSecureSection` descriptor using:

- that per-buffer GUID;
- the same fixed secure-camera scenario.

It then calls `OpenSecureSection()` and maps the section inside the trustlet.

BioIso independently imports `OpenSecureSection` for the same GUID-based secure-buffer consumer contract.

The scoped import surface is informative:

- FsIso: `CreateSecureSection`, `OpenSecureSection`;
- SecureISP trustlet: `CreateSecureSection`, `OpenSecureSection`, `FlushSecureSectionBuffers`, `MapSecureIo`, `AssignMemoryToSocDomain`;
- BioIso: `OpenSecureSection`.

None of those three camera components imports `GetExposedSecureSection`.

That last observation is intentionally narrow: it supports the protected-object model but is **not** proof that the secure kernel has no other exposure mechanism.

## 4. Internal hardware target is a different secure-section class plus a separate SoC assignment

The SecureISP internal target instead uses:

`CreateSecureSection(NULL, 4, 4, size, 2)`

followed by a trustlet mapping and then:

`AssignMemoryToSocDomain(section, ..., DomainId=0x0d, Protection=4, ...)`.

Thus the Windows internal target combines two layers:

1. an IUM secure-section object;
2. an additional Qualcomm SoC-domain assignment used for camera hardware access.

The external sample uses layer 1 but not layer 2.

## 5. Qualcomm Secure Kernel extension proves the internal CP_CAMERA mapping exactly

A major E004ca finding is the exact same-machine Secure Kernel extension:

`QcSkExt8380.exe`

SHA-256:

`618910808afafda01533f6f0decc21209521d23db950209cebe1668520dff5e3`

Its embedded PDB path is:

`Z:\b\WP\QcSkExt\rel\10.9\ARM64\Release\QcSkExt8380.pdb`

It imports both `CreateSecureSectionSpecifyPages` and `AssignMemoryToSocDomain` and contains `QcSkAssignMemoryToSocDomain` plus dedicated camera memory/state code.

### Domain translation

`QcSkAssignMemoryToSocDomain` has a five-entry IUM-domain to Qualcomm-VMID translation table:

| IUM domain | Qualcomm VMID |
|---:|---:|
| `0x25` | `0x06` |
| `0x21` | `0x06` |
| `0x22` | `0x1a` |
| `0x24` | `0x1b` |
| `0x23` | `0x03` |

For a domain absent from that table, the input value is passed through.

The camera trustlet's `0x0d` is absent from the translation table, so the Qualcomm VMID remains **`0x0d`**.

Linux independently defines:

`QCOM_SCM_VMID_CP_CAMERA = 0x0d`.

This upgrades the earlier numerical cross-check into an end-to-end Windows secure-kernel proof.

### Protection translation

The same function translates IUM protection value `4` into Qualcomm/QHEE permission `0x2`.

Golden Linux defines:

- `QCOM_SCM_PERM_READ = 0x4`;
- `QCOM_SCM_PERM_WRITE = 0x2`;
- `QCOM_SCM_PERM_EXEC = 0x1`.

Therefore the exact internal Windows call is ultimately:

**CP_CAMERA VMID `0x0d`, write permission `0x2`.**

That is consistent with the camera hardware being a capture writer while the VTL1 trustlet retains its own protected mapping for later processing/transfer.

## 6. What E004ca proves about external protection — and what it does not

### Proven

For the external protected camera sample:

- creation occurs through the IUM secure-section syscall (`svc #0x8003`);
- open occurs through the IUM secure-section syscall (`svc #0x800e`);
- identity is per-buffer GUID + secure-camera scenario;
- the creator and trusted consumers map the object in isolated/trusted contexts;
- the external FsIso path does not call SoC-domain assignment;
- CP_CAMERA assignment belongs to the distinct internal hardware target.

### Not statically exposed yet

E004ca does **not** claim a specific physical-page VMID or hidden Secure Kernel page-table implementation for the external sample.

The secure-section syscall implementation lives behind the IUM/Secure Kernel boundary. The mounted `securekernel.exe` confirms that implementation exists on the same Windows image, but no public symbols recovered in this gate make it responsible to invent its internal page-owner rule.

So the correct statement is:

> the Windows external sample is protected by a Secure Kernel / IUM object-and-policy boundary, not by the camera's CP_CAMERA assignment path.

## 7. Linux primitive comparison

Linux has several lower-level pieces but no current provider with this complete semantic shape.

### SCM ASSIGN

`qcom_scm_assign_mem()` can change the Qualcomm VMID ownership ACL of a physical range. E004bt proves it can express multi-owner sets.

It is the clear analogue of the **internal target's additional Qualcomm-domain assignment**, not automatically the external IUM object itself.

Assigning the external sample to CP_CAMERA would be architecturally wrong: Windows keeps external and internal objects separate and only the internal target is CP_CAMERA-assigned.

### SHM bridge

E004bz proves SHM bridge is a secure-world sharing registration/lifetime handle, not ownership revocation. It cannot by itself reproduce the external protection boundary.

### Generic protected TEE DMA-BUF

The generic `tee_heap` DMA-BUF ops intentionally omit normal CPU mapping/access callbacks. That is the closest existing Linux **surface abstraction** to the Windows external object's non-ordinary-buffer semantics.

But E004bx proves Golden/X1E has no `secure-video-record` provider behind it.

Therefore the missing Linux piece remains a provider/policy authority, not a new queue data structure or a new Qualcomm transport.

## Architectural consequence

The Windows parity model is now sharper:

**external sample**

`media stack -> FsIso -> IUM secure section (GUID + camera scenario) -> trusted consumers open/map`

**internal hardware target**

`SecureISP trustlet -> IUM secure section -> CP_CAMERA VMID 0x0d / write-only Qualcomm assignment -> IFE writes -> trustlet worker reads`

These are deliberately different protection contracts.

Linux should therefore never implement the external sample by simply reusing the internal CP_CAMERA ownership path.

## What remains forbidden

Do not yet:

- assign an external sample to CP_CAMERA;
- assume a particular QTEE/TZ VMID for external sample pages;
- create a SHM bridge and call it IUM parity;
- register a fake protected heap;
- enable QCOMTEE or probe service UIDs;
- execute Linux SecureISP protected runtime;
- alter `vd55g0.c` security policy.

## Next gate

The new high-value static target discovered by E004ca is **E004cb — Qualcomm Secure Kernel camera memory state machine**.

Reverse the exact `QcSkExt8380.exe` functions already found:

- `pil_camera_mem_assign`;
- `camera_set_state`;
- their assignment-rule helpers.

Goals:

1. identify the meaning of camera-specific VMID `0x39` used by the function;
2. recover transitions among HLOS, HLOS_FREE (`0x0e`), VMID `0x39`, and any hypervisor camera state;
3. determine whether this state machine concerns firmware/PIL camera memory, frame buffers, or both;
4. separate that path from `QcSkAssignMemoryToSocDomain`'s proven CP_CAMERA `0x0d` operation;
5. look for an existing signed secure-world memory policy that could help a Linux protected-sample provider;
6. stay completely static — no camera state switch, assignment, SMC, QTEE, or Windows reboot.
