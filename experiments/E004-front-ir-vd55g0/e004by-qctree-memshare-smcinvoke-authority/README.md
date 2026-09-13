# E004by — QcTrEE MemShare / SmcInvoke service authority

## Result

**PASS: QcTrEE MemShare and SmcInvoke are Windows wrappers over Qualcomm secure-world transport primitives that Linux already implements — MP SHM-bridge and QTEE SMC-invoke respectively. They do not supply the missing protected-camera sample provider or camera service identity.**

This is a static-only Windows/Linux comparison. No QcTrEE service was called, QCOMTEE was not enabled, no SMC was issued, no ownership was changed, and camera runtime remained inactive.

## Exact Windows authority

The exact SP11 QcTrEE binary is:

- `QcTrEE.sys`
- SHA-256 `9cd8252c1b501c1d58e4c49d020d526a5b9bc41a3f5de2ec08e866c3a26c16a2`
- PDB path embedded in the PE: `Z:\b\WP\TrEE\rel\10.9\ARM64\Release\QcTrEE.pdb`

Its INF registers separate secure-service interfaces including PassThrough, MemSharing and Invoke. E004bs already proved the exact camera SecureISP KMD references only PassThrough; it contains zero MemSharing or Invoke GUID references.

E004by reverses MemShare and SmcInvoke as generic infrastructure, not as camera behavior.

## 1. MemShare is Qualcomm MP SHM-bridge

The Windows `MemShareService.c` implementation exposes four request operations:

- op 0 — allocation;
- op 1 — free;
- op 2 — SHM bridge create;
- op 3 — SHM bridge delete.

### Exact SMC IDs

`SendShmBridgeCreateReqToTZ` uses literal:

`0x02000c1e`

`SendShmBridgeDeleteReqToTZ` uses:

`0x02000c1d`

These decode mechanically as ARM SMCCC standard 32-bit SIP-owner calls with:

- Qualcomm SCM service `0x0c` (`QCOM_SCM_SVC_MP`);
- command `0x1e` (`QCOM_SCM_MP_SHM_BRIDGE_CREATE`);
- command `0x1d` (`QCOM_SCM_MP_SHM_BRIDGE_DELETE`).

Linux constructs exactly the same function numbers:

- service `0x0c`, command `0x1e` -> `0x02000c1e`;
- service `0x0c`, command `0x1d` -> `0x02000c1d`.

So the Windows MemShare secure call is not an undiscovered QTEE object service. It is the same MP SHM-bridge ABI already exposed by Linux as:

- `qcom_scm_shm_bridge_create()`;
- `qcom_scm_shm_bridge_delete()`;
- and the higher-level TZMEM wrapper `qcom_tzmem_shm_bridge_create/delete()`.

### Windows bridge input semantics

The Windows create helper:

- requires 4 KiB-aligned addresses;
- accepts one to four VMID/permission entries;
- packs VMID and permission data into the secure-call arguments;
- recognizes VMID 3 (HLOS) specially as the non-secure side;
- returns an opaque 64-bit bridge handle from secure world.

This is useful infrastructure. It proves the SHM-bridge ABI itself can carry an explicit owner/permission description rather than being tied to a single hard-coded client.

It still does not provide the E004bw protected-sample contract by itself: no camera identity, request association, captured extent, serialization state or trusted frame worker is created by the bridge call.

Linux's current QCOMTEE/TZMEM usage is even narrower: it creates ordinary HLOS pages and retains an HLOS kernel mapping before adding the secure-world bridge. That usage is not a protected camera sample.

## 2. SmcInvoke is the QTEE object transport

The Windows `SmcInvokeService.c` path has generic object-transport operations including:

- register SSG TZD;
- register client;
- update client credentials;
- process object request;
- release object.

It marshals request/response buffers, tracks opaque object IDs per session and explicitly releases remote objects.

### Exact SMC IDs

For object invocation QcTrEE chooses:

- `0x32000602` on the newer firmware path;
- `0x32000600` on the legacy path.

The high owner field `0x32` is ARM SMCCC owner 50, `ARM_SMCCC_OWNER_TRUSTED_OS`.

The function number is service `0x06` plus command:

- `0x02` — modern invoke;
- `0x00` — legacy invoke.

Linux names exactly these values:

- `QCOM_SCM_SVC_SMCINVOKE = 0x06`;
- `QCOM_SCM_SMCINVOKE_INVOKE_LEGACY = 0x00`;
- `QCOM_SCM_SMCINVOKE_CB_RSP = 0x01`;
- `QCOM_SCM_SMCINVOKE_INVOKE = 0x02`.

and implements the modern path in `qcom_scm_qtee_invoke_smc()` using `ARM_SMCCC_OWNER_TRUSTED_OS`.

Therefore QcTrEE SmcInvoke and Linux QCOMTEE are two host-side implementations of the same underlying QTEE object-invoke transport family.

## 3. Transport is not service identity

This distinction matters.

SmcInvoke knows how to marshal and invoke **an object** and how to retain/release returned object IDs. That does not tell us which signed QTEE service object should implement protected camera capture.

Linux QCOMTEE has the same split:

1. obtain a privileged client-environment object from the root;
2. open a service by a **known 32-bit service UID**;
3. invoke the returned object.

As established in E004bs, the only service UID hard-coded in the current Linux QCOMTEE tree is FeatureVersions UID 2033. No camera or protected-record service UID is known.

E004by found no hard-coded camera service identity in QcTrEE's generic SmcInvoke transport either.

So enabling QCOMTEE would give Linux a transport, not the missing camera authority.

## 4. Exact QcTrEE client scan

E004by scanned every `.sys`, `.dll` and `.exe` in the same-machine SP11 driver dump for the exact little-endian interface GUIDs.

### MemSharing

MemSharing GUID:

`EB3C7242-1B1A-4D51-AB55-F268F018F860`

is referenced by six binaries:

- QcTrEE itself;
- QCPIL;
- QcSOCPartition;
- QcSCM;
- Qualcomm DX kernel driver;
- QcSecApp.

There is **no camera driver** in that list.

### Invoke

Invoke GUID:

`03B82FC5-2052-44D6-9462-F22C72499337`

is referenced by only:

- QcTrEE itself;
- `qcSSGServicesUMD.dll`;
- `qcconnectionsecurity8380.dll`.

Again there is **no camera component**.

### PassThrough contrast

PassThrough is widely referenced and specifically appears in both:

- `qccamsecureisp8380.sys`;
- `qccamisp8380.sys`.

That matches the proven camera lane-protection role and provides a useful internal control for the GUID scan.

## Architectural consequence

The Linux parity blocker is now narrower:

- **SHM bridge transport exists**;
- **QTEE object-invoke transport exists in source**;
- **generic protected DMA-BUF abstraction exists**;
- **multi-owner SCM ACL mechanism exists**;
- **QTEE itself exists on X1E**.

What remains absent is the authoritative binding that says:

> this signed secure-world service/object owns or can map an external protected camera sample, exposes it to the trusted frame worker, and preserves the Windows consumer-visible lifetime/extent semantics.

In short: **the plumbing exists; the protected-camera provider does not.**

This also prevents an attractive but incorrect shortcut: turning on QCOMTEE and treating any returned object as camera authority.

## What remains forbidden

Do not yet:

- enable/load QCOMTEE;
- invoke SmcInvoke/QTEE at runtime;
- probe or brute-force service UIDs;
- create a SHM bridge for a camera buffer;
- infer that MemShare protects ordinary HLOS pages just because it returns a handle;
- register a fake secure-video-record heap;
- perform CP_CAMERA reassignment;
- activate Linux protected camera runtime.

## Next gate

The next justified static gate is **E004bz — SHM-bridge ACL capability versus protected-camera requirements**.

Now that MemShare is mapped to the existing Linux SCM ABI, determine exactly what the bridge can and cannot guarantee without running it:

1. recover the Windows MemShare create-request structure and VMID/permission packing precisely;
2. compare it with Linux `qcom_scm_shm_bridge_create()` and TZMEM's fixed HLOS+secure wrapper;
3. determine whether the low-level ABI can omit HLOS from the accessible-owner set or whether HLOS necessarily retains access;
4. distinguish secure-world visibility from CP_CAMERA SMMU ownership;
5. identify whether a bridge handle is only sharing metadata or can serve as the opaque lifetime object required by E004bw;
6. preserve the distinction that Windows external camera samples are IUM secure sections, not QcTrEE MemShare objects.

This remains static-only and should not create a bridge.
