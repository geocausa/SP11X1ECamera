# E004eq — official production admission investigation

Date: 2026-09-15
Base: fe3d73ce218cd10846170bd4a35a1959e67d7a3a
Status: INVESTIGATION COMPLETE / PRODUCTION ADMISSION BLOCKED / NO PROTECTED RUNTIME

## User direction

Pursue a clean, vendor-supported protected camera solution with Windows-equivalent behaviour and security on SP11 Linux. Keep ordinary Linux face-login and other alternative architectures parked as escape routes. Do not silently reduce the parity target. Windows on this SP11 remains the behavioural oracle.

Scope remains SP11, SP7 and PiMaster. Golden FullIO v19c remains the boot baseline. This request authorizes admission research and offline preparation; it does not authorize the previously prohibited Linux SecureISP/CPZ runtime or changes to production trust policy.

## Findings that change the next action

### 1. Windows signing and DSP signing are distinct

The observed Windows worker, QcISPTrustlet8380.dll, is an ARM64 PE SecureCompanion with TrustletIdentity 4096 and IumSdk dependencies. It runs in the Windows protected CPU environment. Our proposed Linux worker is a Hexagon-v73 DSP implementation of the observed image operations. CPZ/SecurePD is a candidate Linux equivalent, not evidence that Windows runs this image operation in the same DSP environment.

Microsoft explicitly states that ordinary attestation does not provide the required signing attributes for Windows Hello PE binaries; these need testing and an HLK package submission. This establishes a Windows submission process, not an admission service for Qualcomm DSP ELF modules. Do not purchase an EV certificate or enrol in a paid program on the assumption that it will sign our DSP worker.
Source: [Microsoft driver signing options](https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/driver-signing-offerings).

The exact party controlling the relevant SP11 CDSP production roots, permitted worker classes and camera-use policy must be confirmed by Qualcomm Customer Engineering and, where necessary, the Microsoft Surface platform owner. The phrase "Qualcomm/Microsoft/OEM signing" in earlier records is a category of missing authority, not a verified service offering.

### 2. The currently advertised Surface package supplies no new candidate in the checked packages

Microsoft's Surface Pro 11 download page advertised SurfacePro11_ARM_Win11_26100_26.041.12746.0.msi when checked. SP11 already held a cached copy with that filename. It was extracted into a fresh temporary directory without running its installer.

All 29 files in its qccamsecureisp and qcnspmcdmextcdsp8380 package trees are byte-identical to the corresponding archived packages already studied. This includes the ARM64 trustlet, SecureISP driver, BitML skeleton, CDSP root, example workers and loadalgo proxy.

The deployed Golden CDSP root also matches the prior E004de authority hash:
4a67a03367f2eff2f8a0e867ca25d2bf2fcd5aee3e41e2c9f436c804e257c789.

Scope limitation: this is a fresh comparison of the cached advertised-version MSI, not a claim to have enumerated every Windows Update flight, private OEM package or firmware ever released. The MSI was not freshly downloaded or its Authenticode signature independently validated in this turn. Its SHA-256 and the per-file comparisons are recorded in evidence/PACKAGE-COMPARISON.json.
Source: [official Surface Pro 11 download page](https://www.microsoft.com/en-us/download/details.aspx?id=106119).

E004dd's capability limitations therefore remain relevant; repeating the same example-module experiments would not yield a newly supported camera function.

### 3. The worker is not yet a final loadable production module

The canonical worker was rebuilt offline from maintained source. Wire tests, shipped-proxy contract tests and the stable 644x604 Windows differential passed again, with zero luma and neutral-tail differences. The combined object is byte-identical:
4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48.

Fresh ELF inspection identifies ET_REL, no program headers and ten intended unresolved Qualcomm/QURT imports. This is a compiled and partial-linked implementation core. It is not a final loadable module ready for a signature.

The remaining supported-build questions include the firmware-matched SDK/runtime version, sanctioned SecurePD camera interface, approved module form and entrypoint, linker/relocation requirements, runtime import availability, and signed-image metadata. A final shared object with guessed flags would not resolve those questions. Some runtime imports may legitimately remain dynamic in a final vendor module; the requirement is verified loader resolution, not an arbitrary zero-import rule.

Qualcomm offers a Hexagon SDK for native multimedia development, including Windows/Linux tooling, but its public landing page does not establish SecurePD camera entitlement on retail Surface firmware. Downloads request a Qualcomm login; a compiler SDK is not itself production admission.
Source: [Qualcomm Hexagon SDK](https://www.qualcomm.com/developer/software/hexagon-npu-sdk).

### 4. Public Microsoft VBS tooling is not a discovered Linux camera backend

Microsoft documents a production signing path for VBS enclaves and publishes a Windows Hello user-bound encryption example. Those are useful official references. The example consumes an existing Windows Hello setup; it does not implement a replacement face camera, demonstrate this SP11's protected camera-buffer imports, or provide a Linux VBS runtime.

No claim is made that it is impossible for a vendor to offer such integration. It remains an unanswered vendor question, not a ready solution.
Sources: [VBS enclaves](https://learn.microsoft.com/en-us/windows/win32/trusted-execution/vbs-enclaves), [Microsoft sample](https://github.com/microsoft/VbsEnclaveTooling/blob/main/SampleApps/SampleApps/README.md).

## Primary route and concrete next dependency

The next decisive action is an official platform-support inquiry, prepared in VENDOR-ADMISSION-INQUIRY.md. It asks for one of:

1. A supported production SecurePD build/admission process for an independently implemented protected camera worker on retail SP11, including the matched SDK and camera buffer permissions.
2. An already-admitted, documented vendor camera service with equivalent protected operations that can be used unchanged from supported Linux integration.
3. If SecurePD is not an intended camera backend, the vendor-supported Linux architecture that preserves the Windows protected CPU/device-memory contract.

[Qualcomm Customer Engineering](https://www.qualcomm.com/support/contact) explicitly offers technical case submission. Its support page also points to CreatePoint and Software Center. These are verified contact/resource channels, not proof that a personal project is eligible or that signing will be granted. No support case, forum post, email or application was sent. No account was created and no agreement accepted.

The Microsoft question is a Surface secure-camera platform support request. The generic Hardware Developer Program is documented, but enrolment does not establish support for this Linux/DSP use case.
Source: [Microsoft hardware program](https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/hardware-program-register).

## What constitutes a useful vendor answer

A useful answer must identify the supported hardware/firmware and host OS, worker execution environment, available interface and camera-memory permissions, correct development package and loader format, admission authority and submission steps, and independent-developer eligibility. A generic suggestion to use FastRPC, an unsigned PD, a Windows driver signature or a sample Gaussian algorithm does not close this request.

Before any accepted module is called production-ready, evidence must establish:

- the final module and dependencies match the vendor's supported ABI;
- production signature/admission applies to this exact device and firmware;
- the protected camera permissions are explicitly covered;
- the known offline differential still passes;
- a separately authorized bounded runtime proves protected buffer lifetime and image results;
- subsequent work proves face authentication, template protection and credential integration.

Admission is necessary but is not proof of full-stack completion.

## Hard wall and fallback policy

We have reached a local-material boundary, not proof that no official solution exists. A vendor refusal, confirmed absence of a supported retail admission route, or confirmed absence of required camera permissions would establish a stronger wall. Inaccessible documentation or an unanswered inquiry alone does not prove impossibility.

Alternatives remain parked pending that evidence and a user decision. No firmware replacement, trust weakening, protected-pixel exposure, direct IR stream or generic community face-login installation was performed.

## Reproducibility and handoff

- New evidence lives only in this E004eq directory.
- Existing five dirty top-level files are preserved exactly; their before hashes are in evidence/KNOWN-DIRTY.json.
- Old untracked experiment evidence was not staged or cleaned.
- Canonical worker source and readiness policy are unchanged.
- Golden state and the fresh worker audit are recorded in evidence/WORKER-AUDIT.json and evidence/FINAL-SAFETY.txt.
- The next turn should read this file before treating E004eo's admission-only wording as a claim that the final loadable image or protected Hello integration is already proven.

## Checkpoint publication limitation

The existing repository-wide pre-push hygiene script fails because 260 already-tracked paths match its forbidden binary/raw extensions. None belongs to E004eq. Those historical files were not audited, deleted or reclassified here. The new investigation contains text/JSON/Python only. A local checkpoint is appropriate, but no push is attempted while this existing gate fails. See evidence/REPOSITORY-HYGIENE.json.
