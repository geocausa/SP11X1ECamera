# E004au — trustlet secure-resource / camera-domain static map

## Result

**PASS: the Windows SecureCompanion's secure hardware and buffer-domain requirements are now concretely mapped.**

No Linux SecureISP runtime was performed.

## Secure hardware resource

The trustlet's `EvtCompanionPrePrepareHardware` walks the companion hardware resource list and, for the first memory resource, calls `MapSecureIo()` with:

- the resource physical start;
- a literal mapping-mode value `0x12`;
- the resource length.

It stores the resulting virtual address as the trustlet's `SECUREIFE_BASE_ADDRESS`.

E004y dynamically proved that the installed `CameraSecureISP` device has exactly one memory resource:

- `0x0acca000..0x0accdfff`
- size `0x4000`

That aperture rejected ordinary Windows KD physical reads even while real protected IR frames were flowing.

Because the SecureCompanion is paired to that CameraSecureISP device and the device exposes one memory resource, this is the unique hardware window corresponding to the trustlet's first-memory-resource mapping. The semantic meaning of mapping-mode literal `0x12` is not claimed.

## Secure internal buffers

The trustlet's internal-buffer allocator:

1. rounds requested size to 4 KiB;
2. creates a secure section;
3. maps the section into the trustlet;
4. constructs a per-page domain virtual-address array;
5. calls `AssignMemoryToSocDomain(..., DomainId=0x0d, Protection=0x04, ...)`;
6. flushes the secure section;
7. stores the returned assignment handle and domain address.

The domain-VA allocator starts at `0x18000000`, advances by pages and resets to that base after crossing `0x19000000`.

## Linux cross-check

The current Linux Qualcomm SCM ABI defines:

`QCOM_SCM_VMID_CP_CAMERA = 0x0d`

That is an exact numerical match to the Windows trustlet's `AssignMemoryToSocDomain` target.

This is stronger than a name-based analogy: the Windows secure camera worker explicitly assigns its internal buffers to the same camera VMID value that Linux already publishes as `CP_CAMERA`.

The Windows protection argument `0x04` is recorded as an exact value but is **not** assumed to be numerically interchangeable with Linux `qcom_scm_assign_mem()` destination permission flags.

## Architectural consequence

The protected IR path now has three distinct pieces:

1. **Windows IUM SecureCompanion worker** — implements secure CSID/IFE processing and maps the protected SecureISP hardware aperture.
2. **CP_CAMERA memory ownership** — internal secure buffers are assigned to domain/VMID `0x0d`.
3. **Secure CSI lane control** — separate QcTrEE PassThrough SIP operation decoded in E004as.

Linux already knows the CP_CAMERA VMID and has SCM memory-assignment infrastructure, but that does not authorize using it yet.

## Evidence

- `evidence/TRUSTLET-RESOURCE-DECOMP.txt`
- `evidence/WINDOWS-SECUREISP-RESOURCE.txt`
- `evidence/LINUX-CAMERA-DOMAIN.txt`
- `evidence/TRUSTLET-DOMAIN-VA.txt`

## Safety boundary

No `MapSecureIo` equivalent was attempted on Linux. No camera memory was reassigned. No qcomtee module or camera module was loaded. No secure-lane call was made.

## Next static gate

Map the trustlet's secure IFE/CSID register model and task-0 initialization against the protected `0x4000` aperture. The goal is to identify the smallest hardware register/state model required by the Windows worker before considering any Linux implementation.
