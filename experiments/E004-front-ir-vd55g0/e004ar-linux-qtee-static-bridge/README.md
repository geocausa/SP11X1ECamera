# E004ar — Linux QTEE static bridge

## Result

PASS as a **static / passive Linux bridge**. No SecureISP task was sent and no QTEE driver was loaded.

E004aq proved the Windows Hello IR path reaches the Qualcomm SecureISP kernel/trustlet stack. E004ar asks the next Linux question: does the current SP11 Golden kernel already contain the generic Qualcomm mechanisms needed to talk to the same trusted-execution environment?

The answer is **partly yes**, but there is still an important camera-specific gap.

## What Golden already has

The running Golden kernel has:

- `CONFIG_QCOM_SCM=y`
- `CONFIG_QCOM_TZMEM=y`
- `CONFIG_QCOM_TZMEM_MODE_SHMBRIDGE=y`
- `CONFIG_QCOM_QSEECOM=y`
- `CONFIG_TEE=m`
- `CONFIG_QCOMTEE` is **not enabled**

The live device tree contains the X1E reserved regions:

- camera: `0x8e100000 + 0x00800000`, `no-map`
- QTEE: `0xd80e0000 + 0x00520000`, `no-map`
- TA: `0xd8600000 + 0x08a00000`, `no-map`

The running SCM driver has also created a passive platform device named `qcomtee`. In the upstream/current kernel source this platform device is created only after the SCM QTEE SMC-invoke capability probe is accepted. This is strong evidence that the firmware interface exists on this machine.

There is currently no `/dev/tee*`, no loaded qcomtee module, and no installed qcomtee module in the Golden module tree.

## Build feasibility

The in-tree Qualcomm QTEE driver was copied to a temporary build directory and built as a module against the exact Golden kernel build headers, without installing or loading it.

Build result:

- module: `qcomtee.ko`
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- alias: `platform:qcomtee`
- depends: `tee`
- SHA-256: `3234dc1ffc24e1320356190ec4ba622b6e3a8df7659d26b61f9667d1fac9258d`

The Golden Module.symvers already exports the QTEE SCM entry points consumed by this driver.

## Windows -> Linux primitive map

Windows SecureISP evidence from E004z/E004aq maps to existing generic Linux primitives as follows:

| Windows role | Linux-side candidate | Status |
| --- | --- | --- |
| trusted-environment transport | `qcom_scm_qtee_invoke_smc()` / qcomtee object transport | present in source + firmware capability exposed |
| secure shared buffers | QCOM TZMem SHM Bridge | enabled in Golden |
| memory ownership reassignment | `qcom_scm_assign_mem()` | present |
| camera protection VMIDs | `QCOM_SCM_VMID_CP_CAMERA` and `QCOM_SCM_VMID_CP_CAMERA_PREVIEW` | defined by kernel ABI, no in-tree camera user found |
| Windows trustlet secure mappings | qcomtee memory objects / primordial map-region callback + SCM memory APIs | generic primitives present |
| Windows CameraSecureISP camera command broker | Linux camera-specific SecureISP host driver | **missing** |
| Windows secure CSI lane protect/unprotect service | Linux equivalent | **not identified yet** |

## Important unresolved point

Windows installs `QcISPTrustlet8380.dll` as a SecureCompanion with `TrustletIdentity = 4096`.

The Linux qcomtee API opens QTEE services by a 32-bit UID through the client-environment object. That is structurally compatible with an identity-based service model, but E004ar does **not** claim that Windows TrustletIdentity 4096 is the same namespace as a qcomtee service UID. That mapping still needs proof.

The trustlet itself imports secure-memory primitives such as `AssignMemoryToSocDomain`, `MapSecureIo`, and secure-section operations, which lines up with the Linux SCM/TZMem/QTEE building blocks but does not by itself establish the exact calling convention.

## What is still missing for 1:1 Linux parity

The generic trusted-execution transport is not the hard blocker anymore. The missing piece is the camera-specific host bridge that reproduces the Windows CameraSecureISP lifecycle and command protocol:

1. identify how the ISP trustlet/service is addressed from Linux;
2. identify the Linux equivalent of the secure CSI lane protection service used before START and after STOP;
3. model the Windows SecureISP outer operation sequence and class-1 tasks without executing them;
4. only after a separate runtime authorization, test the smallest reversible QTEE/secure-camera probe.

No normal CAMSS CSID/VFE route should be promoted as Windows parity for IR; E004y already disproved that route.

## Safety boundary

E004ar performs no Linux SecureISP runtime. It does not load qcomtee, open a QTEE object, touch the camera reserved region, reassign camera memory, protect CSI lanes, start the trustlet, or send any camera task.

SP11 remains on protected Golden Linux.
