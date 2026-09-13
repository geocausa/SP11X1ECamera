# E004bs — Linux protected execution counterpart authority

## Result

**PASS (negative authority gate): Linux contains a generic QTEE object transport and memory-object mechanism, but no camera/SecureISP service identity or already-proven trusted execution counterpart for the Windows VTL1 protected worker is present in Golden source or installed X1E metadata. Windows SecureISP uses only QcTrEE PassThrough for secure-lane control; it does not use QcTrEE MemShare or Invoke for the protected frame transfer.**

This experiment is static-only. It did not enable QCOMTEE, issue an SMC/QSEE/QTEE call, change memory ownership, load CAMSS, or activate camera runtime.

## 1. What Linux QCOMTEE can do

The source tree contains a generic Qualcomm QTEE object transport. Its object model is capability-like:

1. invoke the QTEE root object with `QCOMTEE_ROOT_OP_REG_WITH_CREDENTIALS` (operation 5) to obtain a client-environment object;
2. invoke `QCOMTEE_CLIENT_ENV_OPEN` (operation 0) on that client environment with a 32-bit service UID;
3. receive a QTEE-hosted object and invoke service-specific operations on it.

The kernel helper deliberately uses a **NULL credential object** to obtain a privileged client environment. The userspace object-invoke path explicitly rejects that NULL-credential form, so privileged service acquisition is kernel-only.

This is a transport and discovery-by-known-UID mechanism. It is not an enumerator of camera services.

### Only known service UID in this tree

A whole-tree search finds one hard-coded QTEE service UID:

- `QCOMTEE_FEATURE_VER_UID = 2033` — FeatureVersions service.

No camera, SecureISP, protected-video-record, MemShare, or similar QTEE service UID is present in the kernel source.

## 2. QCOMTEE memory objects are real capability, but not camera authority

QCOMTEE can export a Linux `tee_shm` as a memory object. When QTEE invokes the primordial callback with `QCOMTEE_OBJECT_OP_MAP_REGION`, Linux returns:

- physical address;
- length;
- read/write permission;
- a mapping object whose release tears down the mapping reference.

The QCOMTEE shared-memory pool registers memory with the secure world through the TZMEM SHM-bridge path.

This proves a useful primitive: **a QTEE service can be given an explicitly shared Linux TEE memory object.**

It does **not** prove any of the following:

- that a QTEE camera service exists;
- that QTEE can access a buffer after Linux reassigns it solely to `CP_CAMERA`;
- that a CAMSS SMMU IOVA is meaningful to QTEE;
- that generic `tee_shm`/SHM-bridge memory has the Windows external VTL1 secure-camera contract;
- that a QTEE service can replace the VTL1 `QcISPTrustlet8380.dll` worker.

The current memory-object implementation wraps `tee_shm` and publishes its physical range to QTEE. That is structurally different from merely handing QTEE a CAMSS IOVA or an arbitrary already-reassigned CP_CAMERA allocation.

## 3. Enabling QCOMTEE is not a passive compile experiment

Golden has:

`# CONFIG_QCOMTEE is not set`

The SCM code's QTEE setup path probes SMC-invoke support by actually calling:

`qcom_scm_qtee_invoke_smc(0, 0, 0, 0, ...)`.

If supported, it registers the `qcomtee` platform device. During QCOMTEE probe, the driver opens a TEE context, obtains a privileged client environment, opens the FeatureVersions service, and invokes it to fetch the QTEE version.

Therefore enabling/loading QCOMTEE would immediately cross the current **Linux secure-runtime authorization boundary**. E004bs does not do that.

## 4. Windows QcTrEE catalogue does not hide the frame-transfer backend

The exact SP11 QcTrEE INF registers these secure-service GUID classes:

- PassThrough
- TPM
- EFIVar
- WinSecApp
- InlineCrypto
- MemSharing
- MfgMode
- Mssec
- Invoke
- SSGListener

The binary includes implementations such as `PassThroughService*`, `MemShareService*`, and `SmcInvokeService`.

The existence of those generic services is not enough to associate them with camera. To test that association mechanically, E004bs scans the exact SecureISP KMD and trustlet for the little-endian bytes of every QcTrEE secure-service GUID from the INF.

### Exact result

`qccamsecureisp8380.sys`:

- PassThrough GUID `{AE865C08-4A07-404D-BE51-D9A0465E23E5}` — **1 reference**;
- MemSharing — **0**;
- Invoke — **0**;
- InlineCrypto — **0**;
- all other catalogue GUIDs — **0**.

`QcISPTrustlet8380.dll`:

- all QcTrEE service GUIDs — **0 references**.

That matches E004z: SecureISP opens the PassThrough interface for secure CSI/lane ownership and sends IOCTL `0x00568004` with request family `0x02001807`.

It also matches E004br: the protected internal-to-external frame transfer occurs inside the VTL1 Secure Companion trustlet while that trustlet owns both mappings.

Therefore Windows gives us no authority to reinterpret QcTrEE MemShare or Invoke as the camera transfer backend.

## 5. Installed X1E metadata does not provide the missing UID

A static sweep of the installed X1E firmware metadata and kernel source found no named camera/SecureISP/QTEE object-service identity. The only relevant generic constants are:

- `QCOM_SCM_VMID_CP_CAMERA = 0x0d`;
- `QCOM_SCM_VMID_CP_CAMERA_PREVIEW = 0x1d`;
- generic TEE secure-video-record heap identifiers.

This is a scoped negative result. It does not prove that Qualcomm secure firmware contains no undocumented object, nor does it authorize probing unknown UIDs at runtime.

## Architectural consequence

For Windows parity, the missing Linux piece is now sharply defined:

**a trusted execution context that is demonstrably authorized to see both the CP_CAMERA hardware target and the external protected consumer sample, and to execute the worker's internal -> external copy/processing semantics.**

Linux currently has mechanisms that could participate in such a design—SCM ownership APIs, TZMEM SHM bridge, QTEE object transport, TEE memory objects, protected DMA-BUF framework—but no proven camera capability binding those primitives together.

Mechanism is not authority.

## What remains forbidden

Do not yet:

- enable/load `CONFIG_QCOMTEE`;
- call QTEE root/client-env/service operations;
- brute-force or guess QTEE service UIDs;
- issue QSEECOM app lookups/sends for guessed camera names;
- call `qcom_scm_assign_mem()`;
- allocate a generic protected heap and call it Windows parity;
- use QcTrEE MemShare/Invoke as camera evidence;
- run HLOS `memcpy()` as the protected transfer;
- activate Linux SecureISP/CAMSS protected runtime.

## Next gate

The next technically justified gate is **E004bt — CP_CAMERA + trusted-worker visibility contract**, static first.

The question is independent of service discovery: *could an available Linux trusted context even be granted the same simultaneous visibility that the Windows VTL1 trustlet has?*

E004bt should compare:

1. Windows `AssignMemoryToSocDomain(..., 0x0d, ...)` semantics and the fact that the trustlet retains its mapped view;
2. Linux `qcom_scm_assign_mem()` source/destination VMID ACL semantics;
3. whether Linux SCM supports a destination ACL containing both `CP_CAMERA` and a trusted-OS/QTEE VMID while preserving the camera SMMU target;
4. whether QCOMTEE memory objects can represent that ownership state without exposing it back to normal HLOS;
5. the external protected-sample side of the same visibility equation.

No runtime ownership change is needed to answer that gate initially.
