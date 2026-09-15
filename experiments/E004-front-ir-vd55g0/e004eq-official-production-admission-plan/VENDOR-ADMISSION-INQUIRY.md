# Draft vendor inquiry — not sent

## Routing

Primary: Qualcomm Customer Engineering, through https://www.qualcomm.com/support/contact (Customer engineering).
Platform-owner follow-up: Microsoft Surface camera/platform engineering, via an appropriate official support channel. A specific engineering recipient has not yet been resolved.

This is a proposed private technical inquiry. It is not a support submission, purchase authorization, licensing application or acceptance of terms.

## Subject

Supported production admission for a protected camera worker on Surface Pro 11 / X1E80100

## Body

I am developing a native Linux camera stack for my Microsoft Surface Pro 11 (Denali, X1E80100). My objective includes Windows-equivalent protection of front IR camera samples and eventual face authentication. I want a supported production integration, with all firmware verification and protected-memory boundaries preserved.

The front IR sensor is ST VD55G0. The observed Windows protected image-processing profile is 644x604 NV12 at 60 fps. On this device, the Windows SecureISP package registers an ARM64 QcISPTrustlet8380.dll SecureCompanion using the Windows isolated execution environment.

An independently implemented image-processing worker passes an offline byte comparison against a stable same-device Windows reference. There is also an offline Hexagon-v73 implementation core and an interface adapter based on the shipped SecurePD environment. It has not been loaded into SecurePD and is not signed. The current build is a relocatable object with ten runtime imports, not a finished production-loadable module.

Please route this request to the team responsible for X1E80100 CDSP/SecurePD production admission and Surface protected-camera integration, and clarify:

1. Is CPZ/SecurePD a supported backend for a Linux protected-camera worker on retail Surface Pro 11 firmware? If not, what official architecture or partner interface preserves the corresponding Windows protected CPU and camera-device memory guarantees?
2. If it is supported, which SDK/runtime package and version, API headers/libraries, final module format, linker requirements and image metadata apply? We need confirmed protected mapping, mailbox, thread and buffer-validation interfaces.
3. What production signing/admission process is accepted by this exact retail firmware? Who owns that process, and is it available to an independent developer or only through the OEM? Does it require a platform-owner approval, contract or firmware release?
4. Does admission cover processing camera-protected buffers, including CP_CAMERA/CP_CDSP ownership and exclusion of the normal host OS, or is that a separate permission/service?
5. Is an already-admitted camera processing service available that can be used unchanged, with a documented Linux host interface and the required protected buffer operations?
6. Is there any supported way to reuse the existing Surface SecureISP protected service on Linux without transplanting the Windows OS or weakening its protection? If not, please explicitly distinguish that limitation from the availability of generic FastRPC or VBS enclave development.
7. What validation and redistribution requirements would apply to an approved implementation and any vendor dependencies?

For reference, the inspected archived SecureISP driver version is 1.0.4258.7900; the inspected CDSP extension version is 30.0.0219.1000. The SecureISP/CDSP contents in a cached copy of the currently advertised SurfacePro11_ARM_Win11_26100_26.041.12746.0.msi are byte-identical to those packages. This identifies the material investigated; it is not an assertion that no newer Windows Update or private OEM package exists.

I am requesting the supported process and interface documentation, not signing keys or a verification bypass. No production trust configuration has been changed.

A source/evidence summary and exact component hashes can be provided through your appropriate private support channel.

## Microsoft-specific routing note

If forwarded to Microsoft, please route to Surface protected-camera/Windows Hello platform engineering. The Windows Hello HLK signature process is understood to be distinct from Qualcomm DSP ELF admission. The question is whether Microsoft can authorize or identify an official Linux-compatible protected camera interface, or coordinate a supported Qualcomm implementation for this Surface platform. No assumption is made that ordinary Partner Center attestation or a VBS enclave certificate grants that capability.
