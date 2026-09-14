# E004cj — platform secure-worker authority closure

## Result

**PASS: the same-machine Windows image contains multiple signed VTL1/VSM workloads that directly obtain protected CPU access to secure buffer objects, but no reusable QcTrEE/QSEE secure-copy service carrying the camera contract was found. The trusted CPU worker is therefore a property of the isolated execution / Secure Kernel framework, not a generic QTEE transport endpoint we can simply invoke from Linux.**

This gate is static/read-only. No Windows boot, trustlet launch, QTEE/QSEE call, SCM assignment, camera runtime or protected-memory operation occurred.

## 1. The exact IUM secure-section client population is small

A scan of the mounted SP11 Windows System32 and DriverStore PE images found only eight files exposing the IUM secure-section Create/Open surface. The meaningful workloads are:

- `QcISPTrustlet8380.dll`;
- `SecureUSBVideo.dll`;
- `UsbXhciCompanion.dll`;
- `BioIso.exe`;
- `FsIso.exe`;
- `QcSkExt8380.exe`.

The remaining hits are the IUM forwarding DLL itself and a duplicate installed xHCI companion path.

This is useful because it bounds the Windows protected-buffer ecosystem on the exact machine rather than inferring from generic VBS terminology.

## 2. IUM workers do not bridge through QcTrEE service GUIDs

E004cj rebuilt the cross-match from the exact QcTrEE service catalogue recovered in E004bs rather than from guessed GUIDs.

The catalogue contains the PassThrough, TPM, EFIVar, WinSecApp, InlineCrypto, MemSharing, MfgMode, Mssec, Invoke, SSGListener and OpsListener interfaces.

Every IUM secure-section client above has:

`NO_QCTREE_SERVICE_GUID_MATCH`

in its own binary.

This is consistent with the earlier camera-specific control:

- `qccamsecureisp8380.sys` references QcTrEE PassThrough for the secure lane path;
- the VTL1 `QcISPTrustlet8380.dll` itself references no QcTrEE service GUID;
- its frame worker operates on its retained IUM secure mappings directly.

Therefore QcTrEE is not what grants the SecureISP CPU worker its protected mappings.

## 3. SecureCompanion is a repeated Windows execution pattern

Three independent driver packages install signed isolated workloads as:

`ServiceType = SecureCompanion`

with:

`TrustletIdentity = 4096`

on this image:

- Qualcomm SecureISP;
- Microsoft SecureUSBVideo;
- Microsoft USB xHCI companion.

These are separate signed workloads rather than clients of one generic copy service.

The common architecture is:

1. Windows creates or obtains an isolated secure object;
2. the signed workload maps/accesses that object inside VTL1;
3. the workload performs its own CPU/device-specific operation.

## 4. xHCI is secure device plumbing, not a generic secure-copy provider

`UsbXhciCompanion.dll` identifies itself as a USB xHCI SDF trustlet and imports:

- `CreateSecureSection`;
- `OpenSecureSection`;
- `GetExposedSecureSection`;
- `MapViewOfFile`;
- `MapSecureIo`;
- `DmaMapMemory`.

The recovered call chain shows:

- Create/Open/GetExposed produce a secure-section handle;
- a shared helper passes that handle to `DmaMapMemory()` for the USB controller;
- `MapSecureIo()` is used for protected controller/device I/O.

This is secure xHCI resource plumbing, not a buffer-processing service other workloads can invoke.

### `GetExposedSecureSection` is not a VTL0 escape hatch

Secure Kernel's `SkmmCreateExposedSecureSection()`:

- maps an incoming transfer descriptor;
- creates a secure-section object;
- allocates secure PTE backing;
- calls `SkmiClaimPhysicalPage()` for each supplied page;
- writes the Secure Kernel PTEs;
- returns a secure-section handle.

So “exposed” means externally described pages are admitted into a Secure Kernel protected object. It does **not** mean secure pages become normally CPU-visible to VTL0/HLOS.

## 5. Windows Hello supplies a second trusted CPU-worker oracle

`FaceRecognitionSensorAdapterVsmSecure.dll`

SHA-256:

`56be2315b22b9cb82f3582a744b086bf27326fe78b16f907c8659805c607d0ff`

contains an explicit secure IR processing workflow:

- `AsyncImportSecureBuffer`;
- `WbioFrameworkLockAndValidateSecureBuffer`;
- `CopyingFrameBuffer`;
- `WbioFrameworkReleaseSecureBuffer`;
- `WorkerProcessFrame`;
- `RunInfraredFaceProcessor`.

Its HelloFace package enables `VirtualSecureMode` and names the secure VSM sensor adapter separately.

This is important corroboration of E004cf: Windows runs ordinary CPU algorithms over protected camera/biometric data inside a VTL1/VSM workload.

The `WbioFramework*SecureBuffer` names are not exported by some normal System32 DLL on this image; the exact strings occur only inside this secure adapter. They therefore represent an internal VSM/biometric host contract rather than a portable QTEE API Linux can call.

## 6. Qualcomm DX has a real secure-copy mechanism — but it is GPU/content-protection specific

The GPU driver `qcdxkm8380.sys` contains:

- `CryptoCopyData`;
- `CryptoSendCopyCmdSecureApp`;
- `UseSecAppNonSecToSec`;
- `UseSecAppSecToNonSec`;
- TrEE PassThrough / WinSecApp / MemShare registration;
- PlayReady service discovery;
- SCM secure-app start/send-command plumbing.

The secure-copy command is a structured secure-app protocol containing:

- copy direction;
- nonsecure buffer length/address;
- segmented secure-side physical addresses.

This proves that the Qualcomm platform can host a signed secure-copy app for another subsystem.

However it does **not** provide camera authority:

- it does not use the IUM secure-section camera identity/lifetime model;
- its source paths are `cryptoEngineCP.cpp` / `cryptoSecureApp.cpp`;
- it is tied to GPU content protection / PlayReady behavior;
- the startup path contains a `sampleap.mbn` development/test identity;
- the installed package supplies GPU cryptographic/video payloads such as `qcdxkmsuc8380.mbn`, whose embedded identity is “Qualcomm Cryptographic Operations”;
- no camera binary references this copy service or its protocol.

So the existence of secure-copy code is useful platform precedent, not permission to repurpose a DRM secure app as a camera worker.

## 7. What this says about the Linux design

E004cj closes the hypothesis that we merely missed a generic signed QcTrEE/QSEE camera-copy service.

The same-machine Windows evidence instead says protected CPU execution is supplied by **VTL1/VSM workload context**:

- SecureISP trustlet maps the internal and external IUM secure sections and runs its CPU worker;
- SecureUSBVideo maps its own secure sections;
- BioIso maps imported secure sections;
- Windows Hello's VSM adapter locks/validates a secure buffer and runs IR processing;
- xHCI maps/protects its own secure resources.

The common authority is the isolated execution / Secure Kernel memory framework, not a single reusable QTEE service.

## 8. Important correction to the pKVM model

E004ch correctly proved that Qualcomm's `AC_VM_HYP` destination is exclusive at the QcSk assignment layer.

But E004cj makes clear that Windows' trusted CPU mapping and Qualcomm's SoC-domain assignment are **not necessarily members of one Qualcomm VMID owner list**.

For the SecureISP internal target:

- the VTL1 trustlet already owns/maps the IUM secure section through Secure Kernel / Hyper-V mechanisms;
- `AssignMemoryToSocDomain(... CP_CAMERA ...)` is then applied separately for the camera device;
- the VTL1 mapping remains live while CP_CAMERA is active.

Therefore it would be premature to conclude that a Linux VTL analogue must request a Qualcomm `{CP_CAMERA, HYP}` destination set.

The next question is more precise:

> can Linux establish a protected CPU mapping through an architectural isolation layer such as pKVM while Qualcomm CP_CAMERA device-domain assignment remains active, **without** making that CPU context a second Qualcomm destination owner?

That distinction becomes the next gate.

## What remains forbidden

Do not yet:

- invoke or load a QcDX GPU secure app for camera work;
- reuse PlayReady/DRM secure-copy commands for camera frames;
- enable QCOMTEE/QSEE merely because transport exists;
- assume VTL1 == Qualcomm HYP VMID 4;
- attempt `CP_CAMERA + HYP` assignment;
- attempt pKVM + CP_CAMERA runtime coexistence;
- activate Linux protected camera runtime.

## Next gate

**E004ck — VTL trusted-CPU visibility versus Qualcomm device-domain ownership**, static first.

Goals:

1. prove the exact Qualcomm destination/source ownership produced by the Windows internal target's CP_CAMERA assignment;
2. establish whether VTL1 CPU access is maintained entirely by Hyper-V/Secure Kernel rather than by inclusion in the Qualcomm destination list;
3. determine how Qualcomm access-control hardware classifies non-secure EL2/pKVM CPU accesses;
4. decide whether a pKVM-protected CPU mapping could coexist with CP_CAMERA without using `AC_VM_HYP`;
5. keep the E004ch HYP-exclusivity rule intact for any design that actually uses Qualcomm VMID 4;
6. use a Windows one-shot only if static evidence cannot distinguish the Windows ownership layers cleanly.
