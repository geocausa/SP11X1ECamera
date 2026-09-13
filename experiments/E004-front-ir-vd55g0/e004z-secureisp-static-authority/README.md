# E004z — SecureISP static authority

E004z reconstructs the exact same-machine Windows SecureISP host/trustlet ABI from the installed SP11 driver packages. It performs **no Linux SecureISP runtime action**.

## Exact installed sources

- `qccamsecureisp8380.sys` SHA-256 `47c944fa497477751073ec79a27a589a55e884178c1859d6f27388ec7af2ad53`
- `QcISPTrustlet8380.dll` SHA-256 `55ebf254447b9ff8c0a5b20ae81e84f04355f84ce6fa6a09f6205562a5b0b606`
- SecureISP INF SHA-256 `22bffc4795803de62825ee8eab6bd13cdd2d18e505a39b410eecad52b092e05f`
- `QcTrEE.sys` SHA-256 `9cd8252c1b501c1d58e4c49d020d526a5b9bc41a3f5de2ec08e866c3a26c16a2`
- QcTrEE INF SHA-256 `9e6d38df0b0ff8f766a4b67084f1d55e3bf44ddac766c5466b179e99adda8d6b`

The SecureISP INF explicitly installs `QcISPTrustlet8380.dll` as a **SecureCompanion** with `TrustletIdentity = 4096`, together with `libbitml_nsp_v2_skel.so` and `bm3a68v08s11n52.bin`.

## Two-layer command model

The kernel driver uses `WdfCompanionTargetSendTaskSynchronously`. For the normal camera-control path it selects Companion task class **1** and passes the following task IDs to the trustlet:

| Task | Meaning | Important shape |
|---|---|---|
| 0 | INIT | trustlet runs ISPDriverInit + ISPDriverConfig |
| 1 | DEINIT | secure IFE manager teardown/cleanup |
| 2 | START | secure stream start |
| 3 | STOP | secure stream stop |
| 4 | PROCESS_DMFT_SURFACE | exactly 0x60 bytes |
| 5 | PROCESS_CMD_BUFFER | variable |
| 6 | PROCESS_DMI_BUFFER | variable |
| 7 | PROCESS_CSL_PACKET | packet-sized input, 8-byte output |
| 8 | diagnostic-buffer retrieval | 1000-byte output; descriptive name, not a recovered vendor enum |
| 9 | GET_SWABF_DATA | 0x22-byte input |
| 10 | GET_SWASF_DATA | 0x804-byte input |
| 11 | unimplemented/default | — |
| 12 | unimplemented/default | — |
| 13 | NOTIFY_EVENT | 8-byte input |

The trustlet receive dispatcher independently confirms those numerical cases. Tasks 11 and 12 hit its default invalid path.

The send helper also supports task classes 2 and 3. Class 3 is used by a separate frame-dump/debug path and reuses numeric task ID 1 for image retrieval, so task IDs **must be interpreted with their class**. E004z's table above is explicitly the class-1 camera-control namespace.

## Outer KMD operation map

The exact SecureISP KMD switch is:

- `0x801` GetInitParams
- `0x802` DeviceConfig; creates process/interrupt workers, powers the device, then sends class-1 task 0 INIT
- `0x803` SendCSLPacket
- `0x804` DeviceStart
- `0x805` DeviceStop
- `0x806..0x80b` unsupported/default
- `0x80c` GetDeviceInfo
- `0x80d` Init
- `0x80e` DeInit/PowerOff
- `0x80f` SupplementalDeviceConfig carrying CSIPHY/lane information
- `0x810` NotifyEvent

`SendCSLPacket` decomposes the host packet into secure tasks for DMFT surfaces, command buffers, DMI, optional SWABF/SWASF data, and finally the CSL packet itself.

## Secure CSI-lane protection ordering

Before sending class-1 START, the KMD calls an exported function-table command **0x2e**. After class-1 STOP, it calls **0x2f**.

The helper computes a lane-protection bitmask from the SupplementalDeviceConfig CSIPHY/lane fields. It then routes the request to `ConfigSecureCamera()`.

`ConfigSecureCamera()` does **not** talk to the normal MIPI driver directly. It opens device-interface GUID:

`{AE865C08-4A07-404D-BE51-D9A0465E23E5}`

The exact QcTrEE INF identifies that GUID as:

`Parameters\SecureServices\{AE865C08-4A07-404D-BE51-D9A0465E23E5}`
→ **PassThroughService**

The SecureISP KMD sends synchronous IOCTL `0x00568004` to that QcTrEE PassThrough service. Its request begins with dword `0x02001807`, then carries the protect boolean and computed lane bitmask. The exact secure-world semantic name of `0x02001807` is not claimed yet.

Thus the lifecycle is:

**START:** secure-lane protect via QcTrEE → class-1 task 2 START  
**STOP:** class-1 task 3 STOP → secure-lane unprotect via QcTrEE

## Why this matches E004y

The trustlet imports isolated-user-mode secure-memory primitives including:

- `CreateSecureSection`
- `OpenSecureSection`
- `AssignMemoryToSocDomain`
- `MapSecureIo`
- `MapViewOfFile`
- `UnmapViewOfFile`
- `FlushSecureSectionBuffers`

Its internal code contains both `DAL_csid_process_iq_packet` and `DAL_secure_ife_process_iq_packet`.

That is consistent with E004y's live result: Windows delivers real IR frames while the ordinary observable CSID/VFE MMIO blocks stay at their inactive/default state.

## Boundary

This is static authority, not a Linux implementation authorization.

A normal Linux CAMSS route remains diagnostic-only, not Windows parity. The next proof is a same-machine Windows dynamic trace at the KMD Secure Companion send helper so we can record the exact class-1 task sequence actually exercised by a real IR start/frame/stop cycle.
