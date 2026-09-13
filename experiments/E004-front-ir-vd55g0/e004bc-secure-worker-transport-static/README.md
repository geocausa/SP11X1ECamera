# E004bc — secure-worker transport and executable-domain static map

## Result

**PASS: the Windows SecureISP worker is a Windows SecureCompanion/IUM PE image, not a Qualcomm QSEE/QTEE TA image, and upstream Linux currently exposes transport to already-loaded trusted services rather than a loader for that Windows trustlet.**

No Linux secure-camera runtime occurred.

## Windows worker identity

The exact installed `QcISPTrustlet8380.dll` is:

- PE32+/COFF ARM64;
- a Windows DLL;
- installed by the CameraSecureISP INF as `ServiceType = SecureCompanion`;
- assigned `TrustletIdentity = 4096`;
- exported through the Windows UMDF/SecureCompanion model.

Its imports include Windows IUM facilities such as:

- `MapSecureIo`;
- `AssignMemoryToSocDomain`;
- secure-section creation/opening;
- normal Windows runtime imports.

Therefore it is an isolated Windows worker using Windows's IUM/SecureCompanion ABI. It is not an MBN/ELF Qualcomm TA that Linux could simply pass to QSEE/QTEE.

The value `TrustletIdentity = 4096` is retained as a Windows SecureCompanion identity. E004bc does **not** reinterpret it as a QTEE service UID.

## Linux QCOMTEE model

Linux 7.1.5 includes the new Qualcomm QTEE object driver. Its own Kconfig describes it as access to services offered by QTEE and its **loaded** trusted applications.

The kernel API obtains a privileged client-environment object and then opens a service by UID. The object transport ultimately uses the QTEE SCM invocation/callback interface.

This is an object/session transport. The inspected QCOMTEE implementation contains no path that loads `QcISPTrustlet8380.dll` or otherwise converts a Windows PE SecureCompanion into a QTEE TA.

On Golden:

- the SCM-created `qcomtee` platform device exists;
- `CONFIG_QCOMTEE` is not set;
- consequently the qcomtee platform device has no qcomtee driver bound.

## Linux QSEECOM model

Golden does have upstream QSEECOM enabled and bound.

However, the current upstream QSEECOM implementation is also explicitly centered on **already-loaded** applications:

- it asks QSEE for an app ID by application name;
- it sends request/response buffers to that app ID;
- its app-client table currently contains only `qcom.tz.uefisecapp`;
- the source comment states that supported apps are assumed to have already been loaded, usually by firmware bootloaders.

Golden confirms that exact model: the live auxiliary client is `qcom_qseecom.uefisecapp.0`.

Thus upstream QSEECOM is not an arbitrary TA loader either.

## SP11 Linux firmware inventory

The installed Microsoft X1E firmware subtree contains Microsoft/Denali ADSP, CDSP and display-related firmware, but no filename suggesting a camera/ISP/QTEE/QSEE trusted application.

This is a filename/package inventory claim, not proof that no camera service exists inside secure firmware or is resident in QTEE from earlier boot stages.

## Existing Linux primitive for one Windows IUM operation

One important Windows IUM primitive already has an obvious Linux-side architectural counterpart:

- Windows trustlet: `AssignMemoryToSocDomain`;
- Linux SCM: `qcom_scm_assign_mem()`.

Mainline Qualcomm SCM definitions already include the camera protection VMIDs:

- `QCOM_SCM_VMID_CP_CAMERA`;
- `QCOM_SCM_VMID_CP_CAMERA_PREVIEW`.

That does **not** authorize or prove the exact ownership transition yet; it only shows Linux has the generic primitive and named domains needed to model it.

## Architectural consequence

The likely Linux parity architecture is no longer “load the Windows trustlet in QTEE.”

Instead, the parity work splits into:

1. reproduce the Windows SecureCompanion's small trusted-worker responsibilities using Linux/Qualcomm primitives;
2. identify the exact protected-memory ownership transitions;
3. identify the missing protected CSI control equivalent;
4. keep the already-known VFE680/CSID680 register semantics behind the same ownership boundary;
5. only then design a bounded Linux runtime experiment.

Whether QCOMTEE is needed for any camera-specific resident service remains unresolved. Nothing in E004bc justifies enabling it yet.

## Evidence

- `evidence/WINDOWS-SECURECOMPANION-NATURE.txt`
- `evidence/LINUX-QCOMTEE-MODEL.txt`
- `evidence/LINUX-QSEECOM-MODEL.txt`
- `evidence/GOLDEN-TEE-STATE.txt`
- `evidence/MICROSOFT-X1E-FIRMWARE.txt`
- `evidence/LINUX-CAMERA-DOMAIN-PRIMITIVES.txt`

## Safety boundary

No QCOMTEE driver was loaded. No QSEE app lookup beyond the already-running upstream UEFI client was initiated by E004bc. No camera-domain memory assignment, secure CSI call, protected MMIO mapping or SecureISP execution occurred on Linux.

## Next static gate

Map the Windows IUM calls used by the trustlet to Linux SCM/IOMMU equivalents. In particular:

- recover the exact source/destination ownership sets around `AssignMemoryToSocDomain`;
- map the protected CSI operation to an existing SCM convention if one exists;
- classify each trustlet responsibility as already available in Linux, missing wrapper only, or missing secure-world API.
