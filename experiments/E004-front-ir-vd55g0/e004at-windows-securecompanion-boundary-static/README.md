# E004at — Windows SecureCompanion boundary static authority

## Result

**PASS: the main SecureISP task target is a Windows WDF SecureCompanion trustlet, and `TrustletIdentity = 4096` is not evidence for a Qualcomm QTEE service UID.**

This resolves an ambiguity left by E004ar. Linux has usable generic QTEE plumbing, but the Windows CameraSecureISP class-1 task path is not targeting that QTEE object namespace.

Linux SecureISP runtime remains **NOT AUTHORIZED**.

## Installed package authority

The exact SP11 SecureISP INF binds two cooperating components:

- KMDF service: `CameraSecureISP` → `qccamsecureisp8380.sys`
- UMDF service: `SecureBioCompanion` → `QcISPTrustlet8380.dll`
- `ServiceType = SecureCompanion`
- `TrustletIdentity = 4096`
- the KMDF device declares that companion in its `CompanionConfiguration`.

The trustlet binary independently carries Windows secure-process characteristics:

- imports `IumSdk.dll`;
- imports secure-section, secure-I/O mapping and SoC-domain assignment APIs;
- contains UMDF/WDF user-mode entry strings;
- contains companion prepare-hardware callbacks;
- carries the "Microsoft Third Party Secure Bio Signer" certificate string.

Microsoft's public secure-camera/UVC guidance uses the same SecureCompanion model and also shows `TrustletIdentity = 4096`. Microsoft documents trustlets as Isolated User Mode secure processes in VTL1.

Therefore 4096 belongs to the Windows SecureCompanion/trustlet registration mechanism. It must **not** be reused as a Linux qcomtee service UID unless some separate Qualcomm evidence proves that equivalence.

## Task transport

The SecureISP KMD's recovered send helper resolves to `WdfCompanionTargetSendTaskSynchronously`.

For the normal camera task class, the KMD sends the INIT/START/STOP/buffer/CSL work recovered in E004z to the companion target. That path is distinct from the QcTrEE PassThrough path decoded in E004as.

The protected Windows IR architecture now separates cleanly into two security mechanisms:

1. **Secure camera worker:** Windows WDF companion target → `QcISPTrustlet8380.dll` SecureCompanion trustlet.
2. **Secure CSI lane control:** CameraSecureISP KMD → QcTrEE PassThrough → Qualcomm SIP call decoded in E004as.

## Linux consequence

E004ar's qcomtee transport remains a real firmware capability, but it is not a drop-in replacement for `WdfCompanionTargetSendTaskSynchronously`.

The Linux parity problem is now more precise: the camera-specific secure ISP worker logic present inside the Windows trustlet must be mapped/reimplemented independently from the secure-lane SIP operation.

E004at does **not** claim what Linux execution domain can safely host that logic. The Windows trustlet depends on IUM-only services such as secure I/O mapping and secure memory/domain APIs, so ordinary Linux execution cannot be assumed equivalent.

## Evidence

- `evidence/SECURECOMPANION-INF.txt` — exact installed INF companion registration.
- `evidence/TRUSTLET-PE.txt` — exact trustlet hash, IUM/secure imports and companion/WDF strings.
- `evidence/WDF-COMPANION-TASKS.txt` — KMD class/task path into WDF companion transport.
- `PUBLIC-AUTHORITY.md` — Microsoft public architecture corroboration.

## Safety boundary

No Windows runtime was needed for E004at. No Linux QTEE or SecureISP component was loaded or called. SP11 stays on Golden Linux.

## Next static gate

Map the trustlet's hardware/resource acquisition and secure-memory-domain assumptions into a Linux requirements matrix. In particular, determine which pieces are ordinary host logic and which require a protected execution domain before designing any Linux implementation.
