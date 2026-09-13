# E004bv — external protected-sample metadata contract

## Result

**PASS: the Windows external protected sample is carried end-to-end by the standard `SECURE_BUFFER_INFO` contract through the SurfaceCam CSL IOConfig tail into the SecureISP VTL1 trustlet. The 0x60 `PROCESS_DMFT_SURFACE` record is not the external secure-sample identity.**

This gate is static-only. No Windows reboot/debug trace was needed because the installed SDK, SurfaceCam KMD and exact SecureISP trustlet form a complete mechanical chain.

No Linux SecureISP/CAMSS protected runtime, QTEE/QSEE call, SCM ownership change or protected-memory operation occurred.

## 1. Canonical Windows external sample

The installed Windows SDK defines `SECURE_BUFFER_INFO` as:

- `+0x00` — `GUID guidBufferIdentifier` (16 bytes);
- `+0x10` — `DWORD cbBufferSize`;
- `+0x14` — `DWORD cbCaptured`;
- reserved payload afterward.

It also defines the fixed camera secure-section scenario:

`KS_SECURE_CAMERA_SCENARIO_ID = AE53FC6E-8D89-4488-9D2E-4D008731C5FD`.

For a secure transfer, `KSSTREAM_HEADER.Data` points at this structure.

## 2. SurfaceCam preserves GUID + both sizes

`CPin::GetBuffer` follows the secure stream-header path, reads `KSSTREAM_HEADER.Data`, and copies exactly:

- GUID first 8 bytes -> output descriptor `+0x64`;
- GUID second 8 bytes -> `+0x6c`;
- `cbBufferSize` -> `+0x74`;
- `cbCaptured` -> `+0x78`.

`IfeNode::GetBufferforRequestId` uses a 0x60-byte local descriptor followed immediately by stack locals. Because that local starts at stack `-0xf0`, the four secure writes land at the named locals immediately after it. On the protected external path (`hMems[0] == 0`), SurfaceCam copies them into the CSL packet as:

- packet/io-base `+0x18c` — GUID first 8 bytes;
- `+0x194` — GUID second 8 bytes;
- `+0x19c` — `cbBufferSize`;
- `+0x1a0` — `cbCaptured`.

The actual 0x130-byte CSL IOConfig record begins at packet/io-base `+0x74`, so the trustlet-visible record-relative offsets are exactly:

- IOConfig `+0x118` — GUID first 8 bytes;
- IOConfig `+0x120` — GUID second 8 bytes;
- IOConfig `+0x128` — `cbBufferSize`;
- IOConfig `+0x12c` — `cbCaptured`.

This arithmetic is independently cross-checked by `portResourceId`: SurfaceCam sees it at packet/io-base `+0x13c`; the trustlet sees the same field at IOConfig `+0xc8`; `0x74 + 0xc8 = 0x13c`.

## 3. SecureISP turns the IOConfig tail into one protected-image object

For protected output port `0x3000` or `0x3020`, `BuildCSLPacket` allocates a 0xa8-byte protected-image object.

The important external fields are copied as:

- object `+0x6c` <- IOConfig `+0x118` (buffer GUID first half);
- object `+0x74` <- IOConfig `+0x120` (buffer GUID second half);
- object `+0x7c` <- IOConfig `+0x128` (`cbBufferSize`, transient);
- object `+0x80` <- IOConfig `+0x12c` (`cbCaptured`);
- object `+0x7c` <- object `+0x80` immediately afterward.

Therefore the trustlet's **final external mapping length is `cbCaptured`, not `cbBufferSize`**.

The same object also carries the request identity from CSL packet `+0x08`, image geometry/plane fields, the internal CP_CAMERA backing, and later the external mapping/serialization offsets.

## 4. External section open contract

`FUN_180005868` first creates/maps/assigns the internal CP_CAMERA buffer, then calls the external opener.

`FUN_180004828` constructs an IUM secure-section open descriptor from:

- the fixed secure-camera scenario GUID;
- the per-sample GUID at object `+0x6c/+0x74`.

The exact fixed scenario GUID byte sequence occurs once in `QcISPTrustlet8380.dll` and matches the Windows SDK:

`AE53FC6E-8D89-4488-9D2E-4D008731C5FD`.

The trustlet then performs:

`OpenSecureSection(...)`

followed by:

`MapViewOfFile(..., length = object +0x7c)`.

It stores:

- external section handle at `+0x88`;
- external trustlet mapping at `+0x90`.

Because final `+0x7c == cbCaptured`, the mapped external view is the captured-sample extent forwarded by SurfaceCam.

## 5. Frame payload offset is trustlet metadata, not the secure-section GUID

The trustlet separately serializes frame attributes into the external mapping.

`FUN_1800039f0` uses object `+0x98` as a running serialized offset. For attribute type 0 it:

1. writes an 8-byte attribute header at `external_mapping + old(+0x98)`;
2. computes the frame payload size from object geometry;
3. sets object `+0x9c = old(+0x98) + 8`;
4. advances object `+0x98` by the attribute span.

The protected frame worker later writes image data to:

`external_mapping(+0x90) + frame_payload_offset(+0x9c)`

from the internal trustlet mapping `+0x30`.

So four things stay distinct:

- secure-section **identity** — GUID;
- secure-section **captured extent** — `cbCaptured`;
- trustlet **serialized metadata extent** — `+0x98`;
- frame **pixel-data offset** inside the mapped sample — `+0x9c`.

## 6. `PROCESS_DMFT_SURFACE` 0x60 is not the external sample descriptor

This corrects the tentative E004bu next-gate wording.

The KMD sends class-1 task 4 / `PROCESS_DMFT_SURFACE` for:

- command-buffer surface descriptors;
- indirect-buffer patch source surfaces;
- indirect-buffer patch destination surfaces;
- certain IOConfig memory descriptors.

On the trustlet side, task 4 merely:

- requires exactly 0x60 bytes;
- allocates 0x60 bytes;
- copies all twelve qwords opaquely;
- queues the object in `DAT_18003dde0`.

`BuildCSLPacket` later consumes that queued task-4 object as patch/source metadata and pairs it with the task-5 command buffer.

The external secure GUID/size path is instead the **CSL IOConfig tail described above**.

## Linux parity consequence

A Linux external protected sample contract must preserve more than “protected buffer = true”. At minimum it needs independently represented:

- opaque protected-sample identity/lifetime;
- allocated/maximum extent versus captured extent;
- request association;
- trusted-worker mapping capability;
- trusted serialization/payload offset;
- no requirement that the external sample carry a CAMSS IOVA, because Windows programs the internal CP_CAMERA target into IFE instead.

Do not model the task-4 DMFT descriptor as the protected consumer sample.

## What remains forbidden

E004bv does not authorize:

- allocating a Linux protected sample;
- inventing a Linux GUID-to-buffer registry;
- mapping a protected sample into HLOS;
- enabling QCOMTEE/QSEECOM;
- using an HLOS memcpy transfer;
- activating protected CAMSS/SecureISP runtime.

## Next gate

The next justified gate is **E004bw — external protected-sample Linux representation contract**, compile-only/static.

Use E004bv to correct the CAMSS/VB2 abstraction so it distinguishes:

- external identity;
- allocation extent;
- captured extent;
- trusted payload offset;
- request identity;
- external sample lifetime separate from internal CAMSS target lifetime.

No allocator/backend or concrete secure transport should be selected yet. After that contract is mechanically zero-text, return to authority discovery for a Linux provider that can actually implement it.
