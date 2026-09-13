# E004bi — Windows secure capture-surface owner

## Result

**PASS: Media Foundation / MFCore owns the protected camera capture-surface transition and requests the Windows secure-buffer allocator.**

This closes the owner ambiguity left by E004bh without booting Windows.

No Linux SecureISP runtime was performed.

## Why KSProxy is not the protected allocator path

The matching Microsoft symbols for SP11's installed `ksproxy.ax` identify the private `IKsD3DPin` methods used by ordinary DirectShow/KSProxy allocator negotiation.

Its `DecideTransportSurfaceType` path accepts only:

- `1` — system memory;
- `2` — VRAM.

Any other preferred capture-surface value, including `0x10` (`KS_CAPTURE_ALLOC_SECURE_BUFFER`), falls into the invalid-argument path.

`ConnectPipeToUserModePin` uses that private interface to reset/apply the ordinary SYSTEM/VRAM result. Therefore the protected camera path does not come through the normal KSProxy allocator negotiation.

## MFCore owns the secure transition

The matching Microsoft PDB for SP11's installed `mfcore.dll` exposes these exact `CKsBasePin` methods:

- `IsSecureBufferEnabled`;
- `SetCaptureStreamMode`;
- `GetPreferredCaptureSurface`;
- `SetCurrentCaptureSurfaceType`;
- `InitAndCreateAllocator`;
- `CreateAllocator`.

The binary closes the chain mechanically.

### 1. SecureMode selects the secure capture surface

`CKsBasePin::SetCaptureStreamMode` calls `IsSecureBufferEnabled`.

When secure buffers are enabled, it immediately invokes `SetCurrentCaptureSurfaceType` with **`0x10`** and stores **`0x10`** as the pin's current capture surface.

This is the exact transition that E004bh was missing.

### 2. The property operation is the standard Windows capture-surface SET

The same binary contains the exact little-endian bytes for `KSPROPSETID_VramCapture`.

`CKsBasePin::GetPreferredCaptureSurface` constructs:

- property Id `2` — `KSPROPERTY_PREFERRED_CAPTURE_SURFACE`;
- flags `1` — GET.

`CKsBasePin::SetCurrentCaptureSurfaceType` constructs:

- property Id `3` — `KSPROPERTY_CURRENT_CAPTURE_SURFACE`;
- flags `2` — SET.

So the `0x10` selected by `SetCaptureStreamMode` is sent to the camera pin using the standard capture-surface property that SurfaceCam consumes.

### 3. The selected surface flows into allocator creation

`CKsBasePin::InitAndCreateAllocator` calls `SetCaptureStreamMode`, then reads the same stored current-surface field.

When that field is `0x10`, it also accounts for the secure UVC/KS attribute allowance already defined by the Windows KS contract.

The routine later loads that exact current-surface value as the argument to the pin's virtual `CreateAllocator` method.

There is therefore no inferred gap between “secure mode chose 0x10” and “allocator receives 0x10”.

### 4. `CreateAllocator(0x10)` invokes the Windows secure allocator

`CKsBasePin::CreateAllocator` has an explicit branch for capture-surface value `0x10`.

That branch:

1. calculates allocator limits for the secure surface;
2. calls the import slot that the matching PDB names **`MFCreateSecureBufferAllocator`**;
3. creates the pooled camera allocator while preserving capture-surface type `0x10`.

The import identity is independently anchored by the PE/PDB layout: the symbol is section 9 offset 512, and section 9 is `.didat` at RVA `0x7f5000`, giving the exact import slot used by the secure branch.

## FrameServer boundary

FrameServer contains `KSPROPSETID_VramCapture`, but its direct reference decoded in this experiment constructs property Id `1` with GET flags — `KSPROPERTY_DISPLAY_ADAPTER_GUID`.

That direct reference is therefore not evidence that FrameServer itself performs the secure current-surface SET.

FrameServer may still be an upstream policy client, but the actual camera-pin secure-surface transition and allocator request are inside MFCore.

## Ownership model after E004bi

The Windows protected IR path can now be separated cleanly:

1. trusted camera policy enables SecureMode;
2. **MFCore detects secure buffers are enabled**;
3. **MFCore sets the camera pin's current capture surface to `0x10`**;
4. **MFCore requests `MFCreateSecureBufferAllocator`**;
5. the secure sample is represented by the VTL1 GUID-addressed `SECURE_BUFFER_INFO` established in E004bh;
6. SurfaceCam consumes that descriptor and forwards it into the SecureISP request;
7. SecureISP separately manages its own CP_CAMERA internal protected allocation.

This is the Windows parity contract Linux eventually needs to model.

## What remains unresolved

E004bi identifies the **MFCore ownership boundary** and the Windows secure allocator API it calls.

It does not yet identify the lower-level implementation behind `MFCreateSecureBufferAllocator` that ultimately creates/manages the VTL1 secure sections. That can be mapped separately from the installed Windows implementation without changing the proven MFCore ownership result.

## Evidence

- `evidence/MFCORE-SYMBOL-IDENTITY.txt`
- `evidence/MFCORE-VRAM-PROPERTY-CONTRACT.txt`
- `evidence/MFCORE-SECURE-ALLOCATOR-CHAIN.txt`
- `evidence/KSPROXY-ORDINARY-ALLOCATOR-NEGATIVE.txt`
- `evidence/FRAMESERVER-VRAMCAPTURE-BOUNDARY.txt`

Exploratory Ghidra output remains in `ghidra/`; the checkpoint only needs the focused evidence above plus the verifier.

## Safety boundary

All Windows inspection was static against the Windows volume mounted read-only. No Windows configuration or binary was modified. No Linux secure SCM call, camera-domain reassignment, protected MMIO access, or QCOMTEE load occurred.

## Next gate

Resolve the implementation behind `MFCreateSecureBufferAllocator` far enough to determine the low-level VTL1 secure-section creation/lifetime contract. Do not perform Linux secure runtime work.
