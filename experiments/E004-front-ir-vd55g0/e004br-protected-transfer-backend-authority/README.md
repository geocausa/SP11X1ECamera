# E004br — protected transfer backend authority map

## Result

**PASS: Windows authority for the protected internal -> external frame transfer is the VTL1 Secure Companion trustlet itself, not a KMD copy and not an identified Qualcomm QSEE/QCOMTEE camera app. Linux currently has transport primitives but no proven active trusted counterpart for this transfer.**

This is a static-only gate. No Linux SecureISP runtime, QSEECOM send, QCOMTEE enable/load, SCM ownership change, protected MMIO access, or camera runtime activation occurred.

## Windows authority

Exact same-machine package trustlet:

- `QcISPTrustlet8380.dll`
- SHA-256 `55ebf254447b9ff8c0a5b20ae81e84f04355f84ce6fa6a09f6205562a5b0b606`
- INF service type: `SecureCompanion`
- `TrustletIdentity = 4096`

The PE import table shows that the trustlet imports the protected-memory operations directly from `IumSdk.dll`:

- `CreateSecureSection`
- `OpenSecureSection`
- `AssignMemoryToSocDomain`
- `MapSecureIo`
- `MapViewOfFile`
- `FlushSecureSectionBuffers`

Its dependency list is `IumSdk.dll` plus ordinary Windows/CRT DLLs. There is no imported QSEE, QCOMTEE, QTEE, FastRPC, or ADSP/CDSP transport DLL.

### Exact two-buffer constructor ordering

`FUN_180005868` is the protected image-object constructor used by the secure CSL packet path.

ARM64 disassembly proves it first calls:

- `0x180004c58` — internal secure-section creation/mapping and `AssignMemoryToSocDomain(..., DomainId 0x0d, ...)`;

then, on success, calls:

- `0x180004828` — external GUID `OpenSecureSection()` + `MapViewOfFile()`.

Thus a single trustlet object owns both mappings at once:

- internal CP_CAMERA mapping at object `+0x30`;
- external VTL1 mapping at object `+0x90`.

### Transfer execution

E004bp already proved the frame direction:

`internal CP_CAMERA mapping -> external VTL1 mapping`.

The worker dispatches:

`FUN_1800037c8(external_mapping + frame_offset, internal_mapping, width, height, request_id, ...)`.

For early requests this reaches `FUN_180003718` -> `FUN_180028600`, whose recovered semantics are memcpy/memmove-like with parameter 2 read as source and parameter 1 written as destination. Later requests run the trustlet's SWABF/SWASF image-processing path with the same source/destination direction.

Therefore an ordinary Linux HLOS `memcpy()` is not parity. Windows performs the copy/processing while both mappings are visible inside the isolated trustlet.

## Class-1 task protocol correction

Class-1 task 4 (`PROCESS_DMFT_SURFACE`) is not itself the protected final-frame transfer primitive. The receive dispatcher validates/copies its fixed 0x60-byte input and queues it.

The secure CSL packet path later creates the protected image object, opens the external GUID sample, creates/assigns the internal CP_CAMERA target, and replaces the hardware request's `hMems[]` with internal secure SMMU addresses.

So the host KMD task protocol does not expose a generic HLOS-callable `internal -> external secure copy` operation. The final transfer is trustlet-side worker behavior.

## Bundled Qualcomm DSP payloads are not transfer authority

The SecureISP package also installs:

- `libbitml_nsp_v2_skel.so`
- `bm3a68v08s11n52.bin`

The `.so` is a Qualcomm DSP6/Hexagon shared object and contains `bitml_nsp_v2_domains_*`, QSN/DLFD neural/image-processing strings, and DSP memcpy helpers. The trustlet has no direct string/import reference to the package `.so`/`.bin` names or a QSEE/QTEE transport.

This does **not** prove the DSP assets are unused by the complete camera stack. It does prove they are not evidence for replacing the VTL1 trustlet's secure two-mapping transfer with a Linux QSEECOM/QCOMTEE send.

## Linux transport inventory

Golden config:

- `CONFIG_QCOM_SCM=y`
- `CONFIG_QCOM_TZMEM=y`
- TZMEM shmem-bridge mode
- `CONFIG_QCOM_QSEECOM=y`
- `CONFIG_QCOM_QSEECOM_UEFISECAPP=y`
- `CONFIG_TEE_DMABUF_HEAPS=y`
- `# CONFIG_QCOMTEE is not set`

The SCM layer has generic `qcom_scm_qseecom_app_get_id()` and `qcom_scm_qseecom_app_send()` entry points.

However the current in-tree QSEECOM client table auto-registers only:

`qcom.tz.uefisecapp` -> `uefisecapp`.

No camera/SecureISP QSEE app is registered by the Linux QSEECOM driver.

The newer `drivers/tee/qcomtee/` object transport exists in the source tree, but Golden does not enable it. Static presence is not runtime authority.

A deeper installed-firmware filename inventory found normal X1E ADSP/CDSP/ZAP/display payloads, but no obvious Microsoft Denali camera secure-app filename. This remains a filename-level negative result, not proof that no camera capability exists inside a monolithic secure firmware image.

## External protected sample candidate: generic TEE DMA-BUF heap

The generic TEE heap framework defines:

- `TEE_DMA_HEAP_SECURE_VIDEO_PLAY`
- `TEE_DMA_HEAP_TRUSTED_UI`
- `TEE_DMA_HEAP_SECURE_VIDEO_RECORD`

and exports corresponding protected heap names, including `protected,secure-video-record`. Its dma-buf mapping uses device DMA mapping with `DMA_ATTR_SKIP_CPU_SYNC`, and the dma-buf ops deliberately omit ordinary CPU map/vmap callbacks.

That shape is potentially useful for a future **external protected consumer sample** abstraction.

But on current Golden `/dev/dma_heap` exposes only:

- `system`
- `default_cma_region`
- `reserved`

There is no active protected TEE heap provider. More importantly, `secure-video-record` is a generic Linux/TEE pool class and is not evidence that it matches Windows secure-camera scenario `AE53FC6E-8D89-4488-9D2E-4D008731C5FD`.

It also does not provide the missing trusted worker that can map both the internal CP_CAMERA target and the external protected sample.

## Architectural result

The Windows protected IR path now has three independently preserved secure lifetimes plus one explicit transfer boundary:

1. **internal hardware target** — SecureISP-created secure section assigned to CP_CAMERA and mapped to the camera SMMU;
2. **external protected sample** — GUID-addressed VTL1 secure section created by the media stack and opened by the trustlet;
3. **secure CSI/lane ownership** — separately bracketed through QcTrEE around START/STOP;
4. **trusted transfer/processing worker** — VTL1 `QcISPTrustlet8380.dll`, holding both mappings simultaneously.

Linux CAMSS/VB2 remains the correct place for protected-sample queue policy, but it cannot own this secure-memory policy in `vd55g0.c`, and it cannot substitute HLOS memcpy for item 4.

## What E004br does not authorize

Do not yet:

- call `qcom_scm_assign_mem()`;
- query/send an unknown QSEE camera app at runtime;
- enable or load QCOMTEE;
- invent a QTEE object ID/service;
- allocate a generic `secure-video-record` heap and call it Windows parity;
- perform HLOS CPU copy between protected buffers;
- activate Linux SecureISP/CAMSS protected runtime;
- alter VD55G0 security/illumination policy.

## Next gate

The next technically justified gate is **E004bs — Linux protected execution counterpart authority**.

Static-first goal:

1. determine whether the X1E secure firmware/QTEE object graph exposes any already-signed object/service capable of seeing CP_CAMERA-owned memory and a protected consumer buffer;
2. distinguish QcTrEE's proven lane-protection service from any memory/compute object transport;
3. inspect QCOMTEE root-object/object-discovery semantics and Microsoft/Qualcomm firmware metadata without enabling it;
4. if no signed counterpart can be established statically, use same-machine Windows only to answer remaining ownership/ABI questions that static Windows evidence cannot resolve cleanly;
5. produce another verifier-backed static checkpoint before any secure runtime call.

The implementation gate remains closed until a trusted Linux execution boundary is proven rather than inferred.
