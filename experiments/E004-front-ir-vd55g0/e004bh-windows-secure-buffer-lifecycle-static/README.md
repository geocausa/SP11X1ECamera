# E004bh — Windows secure-buffer ownership and lifetime

## Result

**PASS: the protected Surface IR buffer path is a Windows VTL1 secure-section contract identified by GUID, and its lifetime is distinct from SecureISP lane protection.**

Windows remains the parity oracle. Dynamic evidence establishes the task ordering; static Windows analysis and SP11's installed Windows SDK fill in the buffer-object semantics that the accepted KD trace cannot see inside the trustlet.

No Linux secure-camera runtime was performed.

## Windows platform contract

The Windows SDK installed on this SP11 defines an explicit secure capture surface:

- `KS_CAPTURE_ALLOC_SECURE_BUFFER = 0x0010`;
- its documented meaning is a secure buffer in VTL1.

For a secure sample, the normal `KSSTREAM_HEADER.Data` field points to the standard `SECURE_BUFFER_INFO` structure:

- `GUID guidBufferIdentifier`;
- `DWORD cbBufferSize`;
- `DWORD cbCaptured`;
- reserved fields.

The stream header carries `KSSTREAM_HEADER_OPTIONSF_SECUREBUFFERTRANSFER = 0x00040000`. The same SDK's biometric interface imports the secure sample by that GUID and provides lock/validate and release operations keyed by the same identifier.

This is therefore not an ordinary Linux-style DMA buffer with a secure boolean. Windows models the external capture sample as a protected-section object with an identity and lifetime.

## Surface camera KMD bridge

The installed Surface camera KMD matches that SDK contract exactly.

Its secure-buffer paths test the constant `0x00040400`, which is:

- buffered transfer `0x00000400`;
- secure-buffer transfer `0x00040000`.

When that secure transfer form is present, SurfaceCam reads the object pointed to by `KSSTREAM_HEADER.Data` and requires it to be non-null as `pSecureBufferInfo`.

It consumes the structure in precisely the SDK layout:

1. first 8 bytes of the buffer GUID;
2. second 8 bytes of the buffer GUID;
3. buffer size;
4. captured size.

The IFE request-building path then carries the resulting external-buffer identity/state into the camera IO configuration used to build the SecureISP CSL packet.

SurfaceCam also explicitly recognizes capture-surface value `0x10` as `SECURE_BUFFER`.

## SecureISP trustlet buffer pair

The SecureISP trustlet uses two different objects for a protected image path.

### Internal secure buffer

The trustlet:

1. creates its own secure section;
2. maps it in the trustlet;
3. constructs a page-domain address list;
4. assigns that allocation to domain `0x0d`;
5. flushes the secure section;
6. retains the returned assignment handle and protected address.

E004au already established that domain `0x0d` numerically matches Linux's `QCOM_SCM_VMID_CP_CAMERA`.

### External secure buffer

For the externally supplied camera sample, the trustlet does **not** create another ordinary allocation. It receives secure-section identity metadata through the camera IO configuration and calls `OpenSecureSection`.

The trustlet's pair helper obtains the internal CP_CAMERA allocation first, then opens the external protected section.

## Lifetime

The accepted Windows E004aq trace dynamically shows multiple PROCESS_CSL_PACKET task deliveries before protected DeviceStart.

Static fallback shows that the packet builder is where a missing secure image buffer can cause the internal/external secure pair to be acquired.

Release is not tied one-for-one to the lane-protection switch:

- individual request buffers can be released during request completion;
- final trustlet deinitialization sweeps any remaining secure image buffers;
- the accepted dynamic trace places final trustlet DEINIT **after** protected worker STOP and after the lane-protection release.

Therefore Windows has at least two separate secure lifetimes:

**lane ownership:** protect -> protected worker -> unprotect

**secure sample objects:** acquire/use/release per protected sample/request, with a final deinit sweep

They must not be collapsed into one Linux toggle.

## Biometric consumer

The actual installed `BioIso.exe` on SP11 exposes the Windows biometric secure-buffer import path and opens secure sections by identity inside its protected process.

The installed SDK's sensor adapter contract names the operation `AsyncImportSecureBuffer` and passes a `GUID SecureBufferIdentifier`. BioIso contains that same operation and an `OpenSecureSection` path.

This closes the identity chain at the consumer side: the secure camera sample is handed onward by GUID rather than by an ordinary user-visible frame pointer.

## Microsoft secure-capture corroboration

The installed Microsoft `SecureUSBVideo.dll` is useful as independent platform corroboration, not as proof that it owns the Surface MIPI IR path.

It demonstrates the standard Windows secure-capture mechanism directly:

- generate a UUID;
- create a secure section;
- return GUID identities for secure producer buffers;
- open an incoming secure frame section by identity;
- map/unmap and close it at release.

Because Surface IR is MIPI rather than UVC, E004bh intentionally does **not** claim SecureUSBVideo is the Surface IR allocator.

## Linux parity consequence

Linux parity now needs to preserve three separate concepts:

1. the secure CSI/worker ownership bracket proven in E004bd–E004bg;
2. protected external sample identity/lifetime equivalent to Windows' VTL1 GUID secure section;
3. the SecureISP worker's own CP_CAMERA internal allocation.

A future Linux implementation must not pretend those are one buffer or one ownership switch.

The exact Windows component that allocates each MIPI Surface IR external secure section is still unresolved. That is the next Windows-oracle gate.

## Evidence

- `evidence/WINDOWS-DYNAMIC-BUFFER-ORDER.txt`
- `evidence/WINDOWS-SDK-SECURE-BUFFER.txt`
- `evidence/SURFACECAM-SECURE-KS-BRIDGE.txt`
- `evidence/TRUSTLET-BUFFER-LIFECYCLE.txt`
- `evidence/BIOISO-SECURE-IMPORT.txt`
- `evidence/SECUREUSBVIDEO-PLATFORM-CORROBORATION.txt`
- focused Ghidra extraction scripts and outputs in `ghidra/`

## Safety boundary

The Windows volume was mounted read-only for static inspection. No Windows binary or configuration was modified. No Linux secure SCM call was issued, no camera-domain reassignment occurred, no protected MMIO aperture was accessed, and QCOMTEE remained unloaded.

## Next gate

Use the Windows oracle to identify who requests `KS_CAPTURE_ALLOC_SECURE_BUFFER` / sets the current capture surface to secure for the Surface MIPI IR pin, and where the corresponding external secure section is allocated. Prefer existing or new dynamic Windows evidence; use static analysis only where runtime visibility ends.
