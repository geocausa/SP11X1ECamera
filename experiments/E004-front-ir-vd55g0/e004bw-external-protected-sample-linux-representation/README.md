# E004bw — external protected-sample Linux representation contract

## Result

**PASS: the compile-only CAMSS/VB2 protected-pipeline contract now preserves the Windows-proven external-sample identity, request association, allocation/captured extents and trusted payload layout as separate state, with zero executable `.text` change and no provider/backend choice.**

E004bw is disabled by construction. It does not allocate, map, import, assign, invoke, transfer, install or load anything.

## Windows oracle carried forward from E004bv

The external Windows protected sample is not the IFE hardware target and is not the 0x60 `PROCESS_DMFT_SURFACE` record.

Its authoritative chain is:

`SECURE_BUFFER_INFO -> SurfaceCam -> CSL IOConfig -> VTL1 trustlet -> OpenSecureSection`

The distinct concepts proven by E004bv are:

- **identity** — 16-byte secure-section GUID;
- **allocation extent** — SDK `cbBufferSize`;
- **captured extent** — SDK `cbCaptured`, used by the trustlet as the final external map length;
- **request association** — CSL request identity copied into the protected-image object;
- **serialized extent** — trustlet object `+0x98` running metadata/payload layout extent;
- **pixel payload offset** — trustlet object `+0x9c`, used as `external_mapping + payload_offset` for the protected worker destination.

These must not be collapsed into one `vb2_plane_size`, one DMA address, or one `protected` Boolean.

## External representation correction

`camss_external_protected_sample` now contains independently:

- `id[16]`;
- `request_id`;
- `allocation_extent`;
- `captured_extent`;
- `serialized_extent`;
- `payload_offset`;
- plane sizes/count for image geometry;
- a lifecycle phase;
- opaque backend handle;
- whether identity has been proven;
- trusted-worker visibility;
- normal-HLOS CPU visibility.

### Deliberately absent fields

The external sample has **no**:

- CAMSS IOVA;
- ownership physical address/range;
- CP_CAMERA assignment state.

Those belong to the distinct internal capture target. This preserves the Windows two-buffer architecture instead of accidentally making the protected consumer sample the IFE target.

## External lifetime phases

The declaration now makes the external lifetime explicit:

1. `DETACHED`;
2. `IDENTITY_BOUND`;
3. `TRUSTED_VISIBLE`;
4. `PAYLOAD_READY`;
5. `RELEASING`.

This is a representation contract, not an implementation state machine. No code transitions these states in E004bw.

The declared provider boundary is correspondingly split into:

- `bind_identity()`;
- `activate_trusted_visibility()`;
- `deactivate_trusted_visibility()`;
- `release_identity()`.

The internal target retains its separate backing/visibility operations, and internal→external transfer plus secure-lane ownership remain independent roles.

## Why allocation and captured extents stay separate

Windows explicitly forwards both `cbBufferSize` and `cbCaptured`.

The SecureISP trustlet initially copies `cbBufferSize`, then overwrites its final external map-length field with `cbCaptured` before `MapViewOfFile()`.

That is direct authority that Linux must not assume:

`allocated capacity == valid captured payload extent`.

The contract therefore preserves both values even though no Linux provider has yet been selected.

## Why serialized extent and payload offset stay separate

The trustlet's external mapping is not raw pixels beginning at byte zero.

It serializes an attribute header and other metadata into the mapped sample. For the frame-buffer attribute:

- `serialized_extent` advances as attributes are appended;
- `payload_offset` is set to the pixel-data start after the attribute header;
- the protected worker writes to `external_mapping + payload_offset`.

A future provider/backend must therefore return a protected object suitable for trusted serialization, not merely a protected plane with an assumed zero offset.

## Mechanical zero-runtime proof

E004bw uses the exact same production CAMSS preimage as E004bq/E004bu:

- `camss-video.c` SHA-256 `2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4`;
- `camss-video.h` SHA-256 `69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982`.

Both baseline and scaffold build with Golden vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

Their executable `.text` sections are byte-for-byte identical:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`

The generated tree contains:

- zero SCM/VMID implementation references;
- zero QCOMTEE/QSEECOM references;
- zero DMA-heap/TEE-shm provider references;
- zero Windows IUM secure-section calls;
- zero invocations of any new protected-pipeline callback.

No generated module was installed or loaded. SP11 stayed on Golden FullIO v19c with no camera/media nodes.

## Provider authority remains closed

The new fields describe **what must be represented**, not **how Linux obtains it**.

E004bw deliberately does not decide whether the eventual external provider is:

- a protected DMA-BUF heap;
- a QTEE-backed object;
- an as-yet-unidentified Qualcomm/Microsoft camera service;
- another signed secure-world mechanism.

Nor does it invent a GUID registry to mimic Windows mechanically.

## What remains forbidden

Do not yet:

- allocate or map a protected external sample;
- enable/load QCOMTEE;
- query guessed QTEE/QSEE services;
- call `qcom_scm_assign_mem()`;
- expose protected sample backing to normal HLOS CPU access;
- implement HLOS internal→external memcpy;
- activate Linux protected CAMSS/SecureISP runtime.

## Next gate

The next useful gate is **E004bx — external protected-sample provider authority**, static first.

Search the available Linux/X1E mechanisms for a provider that can satisfy the E004bw representation contract, specifically one that can provide:

1. opaque protected identity/lifetime;
2. a trusted-worker mapping without normal-HLOS CPU visibility;
3. distinct allocation and captured extents;
4. trusted serialization at a non-zero payload offset;
5. compatibility with the still-unresolved trusted transfer worker.

The search should start from actual provider implementations and firmware/service metadata, not from generic names such as `secure-video-record`. No secure runtime call is authorized by E004bw.
