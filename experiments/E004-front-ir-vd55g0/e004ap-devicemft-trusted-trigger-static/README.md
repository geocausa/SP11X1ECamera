# E004ap — Windows Hello trusted secure-trigger ownership

## Result

PASS as a static ownership result.

The protected Windows camera trigger is not the FaceAuth media profile by itself. Windows Hello's own `FaceProcessor.dll` explicitly owns the missing control sequence and sends the FaceAuth and SecureMode extended-camera properties through the infrared MediaFrameSource controller.

Linux SecureISP runtime remains NOT AUTHORIZED.

## Stack ownership recovered

The installed Windows driver packages line up into one concrete chain:

- `surfacecamavspro_ext8380.inf` defines `KSCAMERAPROFILE_FaceAuth_Mode` for both front RGB and AUX/IR. The AUX profile is NV12 644x604 at 60 fps and the AUX interface is bound directly to Qualcomm DeviceMFT.
- `helloface.inf` installs the Windows Hello Face biometric stack, including `FaceProcessor.dll`, normal/VSM sensor adapters, and the VSM secure sensor adapter.
- `qccamsecureisp8380.inf` installs `CameraSecureISP`, `QcISPTrustlet8380.dll`, and the `SecureBioCompanion` trustlet service.

This closes the ownership gap left by E004ao.

## Exact Windows Hello property path

`FaceProcessor.dll` SHA256:

`fa201c3ec21d5e7caf4ab16c685d7a237f8883e95965a30791198bd1a061e0e7`

Its `SensorInputManagerFS::InitializeComponents` builds two property strings from the extended-camera-control GUID and property IDs:

- GUID: `{1CB79112-C0D2-4213-9CA6-CD4FDB927972}`
- property 35 / `0x23`: `KSPROPERTY_CAMERACONTROL_EXTENDED_FACEAUTH_MODE`
- property 36 / `0x24`: `KSPROPERTY_CAMERACONTROL_EXTENDED_SECURE_MODE`

The string constructor uses a literal comma delimiter, so the controller property identifiers are:

- `{1CB79112-C0D2-4213-9CA6-CD4FDB927972},35`
- `{1CB79112-C0D2-4213-9CA6-CD4FDB927972},36`

The relevant FaceProcessor RVAs are:

- InitializeComponents: `0x3ba40`
- SetPropertyString: `0x4c5b8`
- GetPropertyBuffer: `0x375c8`
- generic SetProperty: `0x4bd98`
- ToggleFaceMode: `0x4ed50`
- ToggleSecureSensor: `0x92540`
- CreateInfraredReader path: `0x31328`

## Payload behavior

Windows Hello does not manufacture a fresh guessed payload. It first performs `GetPropertyAsync` through the IR source controller, obtains the existing driver-provided byte array, requires at least 0x28 / 40 bytes, modifies the 64-bit Flags field at offset `+0x10`, then writes the byte array back through `SetPropertyAsync`.

This is exactly the 40-byte KSCAMERA_EXTENDEDPROP layout already recovered independently from Qualcomm DeviceMFT.

### FaceAuthMode

`ToggleFaceMode(enable)` reads current Flags and Capability.

- disable requests Flags = 1
- enable prefers Flags = 2 when Capability bit 1 is present
- an alternate capability can request Flags = 4

The proven Surface/Qualcomm path is therefore not just profile selection: Windows Hello explicitly toggles FaceAuthMode after constructing the infrared reader.

### SecureMode

ARM64 disassembly removes the ambiguity left by the decompiler signature:

- `ToggleSecureSensor` takes a boolean enable argument in `w1`
- CreateInfraredReader calls it with `w1 = 1`
- cleanup calls it with `w1 = 0`
- the function computes requested Flags as `enable + 1`
- therefore enable => Flags 2 and disable => Flags 1
- it requires SecureMode Capability bit 1 before writing
- it writes only the Flags field at payload offset `+0x10`, preserving the GET-returned header/capability data

That exactly matches the DeviceMFT SecureMode semantics from E004ai.

## Why E004ao was negative

E004ao selected the FaceAuth media profile and streamed valid IR frames, but did not reproduce Windows Hello's controller operations.

The real Windows Hello sequence is:

1. select the FaceAuth profile
2. create the infrared reader
3. GET FaceAuthMode property buffer from the IR source controller
4. set FaceAuthMode to an enabled flag
5. when the secure-feature condition is active, GET SecureMode property buffer
6. set SecureMode to Flags 2
7. stream through the biometric path
8. on teardown, set SecureMode back to Flags 1

A generic MediaCapture profile selection therefore cannot be used as evidence that SecureMode or SecureISP was exercised.

## Dynamic next gate

The next bounded Windows oracle should reproduce the Windows Hello controller path, not use VideoDeviceController:

- use the IR `MediaFrameSource.Controller`
- property IDs must be the two exact comma-form strings above
- GET the driver's byte array first
- preserve the returned 40-byte structure
- modify only Flags at offset 16
- enable FaceAuthMode, then SecureMode
- trace `surfacecamavs8380.sys` SecureMode setter / secure CSI path and current relocated `qccamsecureisp8380.sys`
- always disable SecureMode and return immediately to Golden

No Linux SecureISP runtime is authorized until that Windows dynamic gate is proven.

## Evidence

- `evidence/WINDOWS-STACK-EVIDENCE.txt`
- `evidence/FACEPROCESSOR-SECURE-ASM.txt`
- `ghidra/FACEPROCESSOR-SECURE-CONTROLS.txt`
- `ghidra/FACEPROCESSOR-CONSTANTS.txt`
- `ghidra/DEVICEMFT-CAPABILITY-FACEAUTH-CALLERS.txt`
