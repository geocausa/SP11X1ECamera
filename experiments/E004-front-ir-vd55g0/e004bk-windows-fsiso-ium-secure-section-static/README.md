# E004bk — FsIso server-side secure camera section

## Result

**PASS: Windows FsIso is the server-side owner that turns a camera secure-buffer GUID into an IUM secure section under the secure-camera trustlet policy, and closes that section when the GUID is released.**

E004bj already proved the upstream chain:

`MFCreateSecureBufferAllocator → CameraTrustletConnectionImpl → local ncalrpc → FsIso.exe`.

E004bk closes the remaining server-side gap without booting Windows.

## Exact server identity

The installed SP11 `FsIso.exe` matches Microsoft PDB identity:

- binary SHA-256: `bb8908c6abc4655e96dc8b01eac86dd39839f6df1cd6730f913d182e492ce288`
- PDB GUID: `93B68425-0001-BB52-0629-3C9D979A1351`
- PDB SHA-256: `d937099b26149a071af629b1f9b055645c1a58d6cce68a600425a01de01a34c1`

The matching symbols name:

- `RpcCreateSecureSection`;
- `RpcCloseSecureSection`;
- `RpcEstablishFsIsoConnection`;
- `RpcDestroyFsIsoConnection`;
- `FSISO_CONNECTION_rundown`;
- `SECURE_CAMERA_SCENARIO_GUID`;
- `__imp_CreateSecureSection`;
- `__imp_OpenSecureSection`;
- `__imp_CloseHandle`.

## Creation path

`RpcCreateSecureSection` receives the per-buffer GUID and requested size from the MFPlat CameraTrustlet RPC client.

The routine builds the IUM secure-section request with:

- the incoming GUID;
- the requested size;
- the fixed secure-camera scenario GUID;
- the installed IUM `CreateSecureSection` import.

The scenario GUID embedded in the executable is:

`AE53FC6E-8D89-4488-9D2E-4D008731C5FD`

The same GUID is also present in the executable's `.tPolicy` section, independently anchoring it as the trusted-process policy for this helper.

That is the exact `KS_SECURE_CAMERA_SCENARIO_ID` previously identified from the Windows camera contract.

At the decisive call site, `RpcCreateSecureSection` loads import slot `+0x8`, which the matching PDB identifies as `__imp_CreateSecureSection`, and invokes it. The returned secure-section handle is retained in FsIso's GUID-indexed state.

## Destruction path

`RpcCloseSecureSection` looks up the incoming GUID in the same server-side state, removes the corresponding entry, loads the stored secure-section handle, and calls import slot `+0x88`.

The matching PDB identifies that slot as `__imp_CloseHandle`.

Therefore the GUID is the end-to-end lifetime key from MFPlat's `SecureMediaBuffer` to the protected section inside FsIso.

## Ownership model after E004bk

The Windows protected IR path now has three deliberately separate ownership domains:

1. **External protected sample**
   - MFCore selects capture surface `0x10`;
   - MFPlat creates a GUID-addressed `SecureMediaBuffer`;
   - FsIso creates/closes the IUM secure section under the secure-camera scenario.

2. **SecureISP internal protected buffer**
   - separate CP_CAMERA allocation inside the SecureISP path.

3. **Secure camera lane / protected-worker ownership**
   - separate CSI/worker ownership bracket.

Linux parity must keep these lifetimes separate rather than collapsing them into one secure-mode flag or one ordinary DMA buffer.

## Safety boundary

This experiment is static only. The Windows volume stayed read-only. No Windows helper process was started, no camera stream was activated, and no Linux secure SCM call, memory reassignment, protected MMIO access, or QCOMTEE load occurred.

## Evidence

- `evidence/FSISO-SECURE-SECTION-SERVER.txt`
- `evidence/IDENTITY-AND-SYMBOLS.txt`

## Next gate

Map this now-complete Windows protected-sample lifetime onto the existing Linux camera allocator, buffer-queue, and teardown boundaries. That next step is architecture/design work only: do not enable SecureISP or perform protected-memory runtime experiments.
