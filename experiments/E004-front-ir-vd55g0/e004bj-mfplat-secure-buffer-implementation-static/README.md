# E004bj — MFPlat secure-buffer implementation and FsIso owner

## Result

**PASS: Windows MFPlat implements the secure camera allocator as a GUID-addressed object whose create/destroy operations are brokered over local RPC to `FsIso.exe`.**

This is a Windows-static ownership checkpoint. It extends E004bi, which already established that MFCore selects secure capture surface `0x10` and calls `MFCreateSecureBufferAllocator`.

No Linux secure-camera runtime occurred.

## Exact SP11 binary and symbols

The analyzed binary is the exact installed SP11 `mfplat.dll`.

Its matching Microsoft PDB was retrieved using the CodeView identity embedded in that binary. The PDB names the relevant implementation classes and functions, including:

- `MFCreateSecureBufferAllocator`;
- `CMFDX11Allocator::AllocateSecureBuffer`;
- `CameraTrustletConnectionImpl::CreateInstance`;
- `CameraTrustletConnectionImpl::CreateSecureBuffer`;
- `CameraTrustletConnectionImpl::DestroySecureBuffer`;
- `CameraTrustlet::{Connect,GenerateEndpointName,LaunchProcess,EstablishRpcConnection,CreateSecureSection,CloseSecureSection}`;
- `SecureMediaBuffer::{CreateInstance,GetIdentifier,~SecureMediaBuffer}`.

This removes the ambiguity caused by the earlier whole-image Ghidra failure: the PDB gives exact function identities for the same installed image.

## Allocator factory

The exported `MFCreateSecureBufferAllocator` is a thin branch into `CameraTrustletConnectionImpl::CreateInstance`.

So the secure allocator object handed to MFCore is specifically backed by the camera-trustlet connection implementation.

## Create/destroy delegation

`CameraTrustletConnectionImpl::CreateSecureBuffer` delegates to:

`CameraTrustlet::CreateSecureSection(GUID, size)`

`CameraTrustletConnectionImpl::DestroySecureBuffer` delegates to:

`CameraTrustlet::CloseSecureSection(GUID)`

Therefore MFPlat does not implement the secure section as an ordinary local mapping. It forwards lifetime operations to the lower isolated-process broker.

## FsIso ownership boundary

The same exact MFPlat image contains the endpoint/process identities:

- RPC transport: `ncalrpc`;
- endpoint format: `FsIso_%u_%I64u`;
- executable launch format: `%s\FsIso.exe %s`;
- executable suffix: `\FsIso.exe`.

`CameraTrustlet::Connect` performs this order:

1. `GenerateEndpointName`;
2. `LaunchProcess`;
3. `EstablishRpcConnection`.

`GenerateEndpointName` uses 8 bytes of `BCryptGenRandom` plus `GetCurrentProcessId` to construct the unique endpoint identity.

`LaunchProcess` obtains the system directory, builds the FsIso command line and calls `CreateProcessW`.

`EstablishRpcConnection` constructs an `ncalrpc` binding, converts it to an RPC binding handle and uses the generated endpoint for the client connection. Secure-section operations then enter the RPC client path through `NdrClientCall3`.

Thus the Windows protected external-sample owner below Media Foundation is **FsIso**, not the Qualcomm CameraSecureISP trustlet.

## SecureMediaBuffer GUID lifetime

`SecureMediaBuffer::CreateInstance` generates a GUID with `CoCreateGuid`, then constructs the secure media-buffer object around that identifier and the secure allocator.

The constructor stores:

- the 16-byte GUID in the object;
- the allocator object used to own the remote secure section.

`GetIdentifier` copies that stored GUID back to its caller.

On destruction, `SecureMediaBuffer::~SecureMediaBuffer` loads the retained allocator, passes the stored 16-byte GUID through the allocator's destroy slot, and then releases the allocator reference.

This establishes a direct Windows lifetime rule:

**secure media-buffer object lifetime owns the corresponding FsIso secure-section lifetime by GUID.**

## Relationship to the camera stack

The Windows chain established by E004bi + E004bj is now:

`SecureMode`
→ MFCore selects capture surface `0x10`
→ `MFCreateSecureBufferAllocator`
→ MFPlat `CameraTrustletConnectionImpl`
→ FsIso local-RPC secure section
→ GUID-backed `SecureMediaBuffer`
→ KS `SECURE_BUFFER_INFO`
→ SurfaceCam
→ SecureISP protected processing.

This is separate from the SecureISP trustlet's own CP_CAMERA internal allocation documented by E004bh.

## Linux parity consequence

Linux parity must reproduce the semantics, not the Windows API names:

- a protected sample must have a stable identity and independent lifetime;
- allocation/release must be owned outside ordinary user-visible memory;
- camera processing consumes that protected object without collapsing it into the SecureISP internal CP_CAMERA allocation;
- sample destruction must release the protected backing object.

Nothing in E004bj implies Linux needs an FsIso clone. It establishes the behavior that a Linux protected-buffer owner must preserve.

## Evidence

- `evidence/MFPLAT-PDB-AUTHORITY.txt`
- `evidence/ALLOCATOR-DELEGATION.txt`
- `evidence/CAMERATRUSTLET-FSISO-RPC.txt`
- `evidence/SECUREMEDIABUFFER-GUID-LIFETIME.txt`

## Safety boundary

The Windows volume was inspected read-only. No Windows binary was modified. No Linux secure allocation, CP_CAMERA reassignment, protected MMIO access or QCOMTEE runtime occurred.

## Next gate

Use a bounded Windows boot to observe `FsIso.exe` dynamically during the already-proven protected IR route: capture process creation, command line/endpoint argument, lifetime relative to secure streaming, and whether the process exits after secure-buffer teardown.
