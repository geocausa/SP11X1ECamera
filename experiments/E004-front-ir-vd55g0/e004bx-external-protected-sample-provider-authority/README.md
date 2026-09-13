# E004bx — external protected-sample provider authority

## Result

**PASS (negative provider-authority gate): current Golden/X1E Linux has no active or statically identified provider that can satisfy the E004bw external protected-sample contract.**

The generic Linux TEE protected DMA-BUF framework has several useful semantic properties, but there is no Qualcomm/QTEE secure-video-record provider wired into this kernel, and the only concrete protected-memory provider implementation present is OP-TEE, which registers secure-video **playback** only.

This is a static/read-only inventory. No TEE module was loaded, no QTEE/QSEE call was issued, no protected heap was created, no SCM ownership change occurred, and camera runtime stayed inactive.

## 1. What a suitable provider must satisfy

E004bw requires an external sample provider capable of representing:

1. opaque protected identity and independent lifetime;
2. allocation extent and captured extent separately;
3. request association;
4. a trusted-worker-visible mapping/object without normal-HLOS CPU visibility;
5. trusted serialization state and a non-zero pixel payload offset;
6. lifetime independent from the internal CP_CAMERA hardware target;
7. compatibility with the still-unresolved trusted internal→external worker.

A provider does not have to copy Windows' GUID implementation internally, but its observable protection/lifetime semantics must match the Windows oracle.

## 2. Generic TEE protected DMA-BUF has the right *shape*

`drivers/tee/tee_heap.c` implements a protected DMA-BUF heap abstraction.

Its exported protected buffer operations include:

- attach/detach;
- DMA map/unmap using `DMA_ATTR_SKIP_CPU_SYNC`;
- release.

They deliberately do **not** define ordinary DMA-BUF:

- `mmap`;
- `vmap`;
- `begin_cpu_access`;
- `end_cpu_access`.

That is structurally useful for E004bw because a protected sample should not become an ordinary HLOS CPU buffer.

The generic framework has names for:

- `protected,secure-video`;
- `protected,trusted-ui`;
- `protected,secure-video-record`.

But a name/enum is not a provider.

## 3. No secure-video-record provider exists in this tree

A whole-tree search for `TEE_DMA_HEAP_SECURE_VIDEO_RECORD` finds only:

- the enum declaration in `include/linux/tee_core.h`;
- the name mapping in `drivers/tee/tee_heap.c`.

There is **no registration callsite** using the record/capture heap ID.

The only TEE protected-heap registration callsites are inside OP-TEE.

A sweep across the other local SP11 kernel/source trees finds the same pattern: `secure-video-record` appears only as the generic heap-name switch, with no Qualcomm or camera provider implementation available to reuse.

## 4. OP-TEE protected memory is not X1E camera authority

Golden has:

- `CONFIG_TEE=m`;
- `CONFIG_TEE_DMABUF_HEAPS=y`;
- `CONFIG_OPTEE=m`;
- `CONFIG_OPTEE_STATIC_PROTMEM_POOL=y`.

However the OP-TEE SMC and FF-A provider paths both hard-code:

`TEE_DMA_HEAP_SECURE_VIDEO_PLAY`

when registering their protected heap.

They do not register `TEE_DMA_HEAP_SECURE_VIDEO_RECORD`.

More importantly, the X1E Denali device tree contains no `linaro,optee-tz` node, the current runtime exposes no `/dev/tee*`, no OP-TEE/FF-A module is active, and no protected TEE DMA heap exists.

Loading/probing OP-TEE merely to see whether firmware responds would cross the secure-runtime boundary and is not authorized by this experiment.

## 5. QTEE exists on X1E, but QCOMTEE is not a protected-sample provider

The X1E device tree contains fixed no-map Qualcomm secure-world regions including:

- `qtee@d80e0000` — 0x520000 bytes;
- `ta@d8600000` — 0x8a00000 bytes.

This corroborates that Qualcomm's trusted execution environment exists on the platform.

But Golden has:

`# CONFIG_QCOMTEE is not set`

and `drivers/tee/qcomtee/` contains **zero** references to:

- `tee_device_register_dma_heap`;
- protected-memory pools;
- `TEE_DMA_HEAP_SECURE_VIDEO_RECORD`.

QCOMTEE's existing ordinary shared-memory path instead allocates HLOS pages, keeps a normal kernel `kaddr`, obtains their physical address, and registers them through the TZMEM SHM bridge. That is the wrong protection class for the external protected sample.

So QTEE presence is not equivalent to external-sample provider authority.

## 6. The live `reserved` DMA heap is ordinary CMA

SP11 currently exposes:

- `system`;
- `default_cma_region`;
- `reserved`.

The `reserved` name might look promising, but it is produced by the standard CMA heap implementation. Its DMA-BUF ops explicitly include:

- CPU begin/end access;
- userspace `mmap`;
- kernel `vmap`/`vunmap`.

Therefore it is ordinary CPU-accessible CMA memory, not a protected camera sample.

## 7. Fixed camera/QTEE carveouts are not per-sample providers

The X1E device tree also reserves no-map regions named `camera`, `video`, `qtee`, and `ta`.

A fixed `no-map` carveout alone does not provide:

- per-sample identity;
- allocation/free semantics;
- request association;
- trusted mapping lifetime;
- external captured extent;
- serialization/payload metadata;
- a trusted transfer worker.

The X1E `camera_mem` label also has no Linux driver/source consumer in this tree. It is therefore reserved platform memory, not evidence of a usable protected camera heap.

## Candidate matrix

| Candidate | No normal HLOS CPU map | Active X1E provider | Camera/record authority | Trusted-worker path | Result |
|---|---:|---:|---:|---:|---|
| system DMA heap | No | Yes | No | No | reject |
| CMA `default_cma_region` / `reserved` | No | Yes | No | No | reject |
| generic TEE protected DMA-BUF | Yes structurally | No | enum only | provider-dependent | useful framework only |
| OP-TEE protected heap | Yes | No on SP11 | playback only | OP-TEE-specific | reject as camera authority |
| QCOMTEE ordinary `tee_shm` | No | QCOMTEE disabled | No | generic QTEE sharing | reject as protected sample |
| QCOMTEE protected DMA heap | potentially | **not implemented** | none found | unresolved | absent |
| fixed `camera` carveout | no HLOS linear map | reserved only | none | none | not a provider |
| fixed `qtee`/`ta` carveouts | secure-world-owned | reserved | QTEE infrastructure only | QTEE internal | not a sample provider |

## Architectural consequence

Linux now has a usable **generic abstraction** for a CPU-inaccessible protected DMA-BUF, but the provider side is the blocker.

That is important because it avoids two bad implementations:

- using ordinary `reserved`/CMA memory and calling it protected;
- registering `protected,secure-video-record` ourselves without any secure-world service that actually protects or maps the backing.

A heap name is not a security boundary.

## What remains forbidden

Do not yet:

- register a fake `secure-video-record` heap;
- load/probe OP-TEE merely to test firmware;
- enable/load QCOMTEE;
- allocate/reassign a camera protected buffer;
- use the fixed `camera_mem` carveout as a sample pool by assumption;
- call QTEE/QSEECOM/SCM for guessed services;
- activate Linux protected camera runtime.

## Next gate

The highest-value static gate is **E004by — QcTrEE MemShare/SMCInvoke service authority**.

Windows SecureISP itself only uses QcTrEE PassThrough for lane ownership, so MemShare/Invoke are not evidence for the Windows camera transfer path. But they are signed, present Qualcomm secure-world services and may reveal whether Linux QCOMTEE has an already-existing generic service capable of creating or sharing a CPU-inaccessible object with a trusted worker.

E004by should therefore statically reverse the exact SP11 `QcTrEE.sys` implementations enough to identify:

1. the secure-world service/object identity or UID opened by `MemShareService`;
2. its memory ownership/share operation semantics;
3. whether it produces opaque handles suitable for per-sample lifetime;
4. the service/object identity used by `SmcInvokeService`;
5. whether either maps onto the QCOMTEE root/client-environment object protocol already present in Linux;
6. whether these are generic infrastructure that could implement the Linux semantics without pretending Windows SecureISP directly used them.

No runtime QTEE call is required for that gate.
