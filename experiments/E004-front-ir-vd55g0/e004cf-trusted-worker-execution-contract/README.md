# E004cf — trusted-worker execution contract extraction

## Result

**PASS: after the internal and external protected mappings already exist, the Windows protected-frame worker is a VTL1 CPU/memory-processing workload. Its per-frame execution path does not call IUM secure-section APIs, SoC-domain assignment, QcTrEE/QTEE/QSEE, device IO, or camera MMIO.**

The secure platform is still essential because it supplies the protected mappings and execution privilege. But the frame transform itself does not require a special camera accelerator or secure-world RPC once those mappings are available.

This gate is static-only. No Windows boot, Linux secure runtime, ownership change, protected allocation or camera activation occurred.

## 1. Exact per-frame source and destination

The existing Windows oracle chain remains:

- source = SecureISP internal VTL1 mapping at protected-image object `+0x30`;
- destination = external secure-section VTL1 mapping at `+0x90` plus serialized pixel payload offset `+0x9c`;
- dimensions = object width/height fields;
- request identity selects the worker branch.

The call is:

`FUN_1800037c8(external_mapping + payload_offset, internal_mapping, width, height, request_id, ...)`

So the worker must simultaneously read the internal target and write the external sample while normal VTL0/HLOS remains unable to access the external object.

## 2. Transfer dispatcher has three CPU branches

`FUN_1800037c8` selects among:

### Synthetic/fill branch — `FUN_1800033d8`

- fills the luma-sized destination region with decimal `100`;
- fills the following half-size region with `0x80`;
- does not consume the source pointer.

### Early-request copy branch — `FUN_180003718`

For request IDs below 10:

- copies `width * height` bytes from internal source to external destination with `FUN_180028600`;
- fills the following `width * height / 2` bytes with `0x80` using `FUN_1800290a0`.

`FUN_180028600` decompiles as an optimized overlap-aware memory copy/move routine using ordinary loads/stores and prefetch hints.

### Later SWABF/SWASF branch — `FUN_180003478`

This branch runs two post-processing passes:

1. `ImageProcessingModule_SWABF` from internal source into trustlet scratch;
2. `ImageProcessingModule_SWASF` from scratch into external destination;
3. fills the half-size tail with `0x80`.

The branch adds timing/ETW instrumentation around those passes but no protection operation.

## 3. SWABF/SWASF wrapper is in-process memory work

`FUN_180019828` constructs a processing descriptor entirely in trustlet memory.

For SWABF/SWASF it stores:

- input pointer;
- output pointer;
- dimensions;
- image span (`width * height * 3 / 2`);
- module configuration/handle state.

It then calls `FUN_18001a138`.

Its direct callees are limited to:

- stack-cookie helpers;
- logging;
- `FUN_18001a138`;
- memcpy-like `FUN_180028600`;
- memset-like `FUN_1800290a0`.

There is no secure-section or device invocation in this wrapper.

## 4. Core processing uses VTL1 CPU threads

`FUN_18001a138` initializes/coordinates an in-process worker pool using ordinary synchronization primitives:

- critical sections;
- events;
- wait/set operations;
- heap allocation;
- `CreateThread`.

The worker threads all start at `FUN_18001f170`.

That thread entry directly iterates pixels from the supplied input pointer, computes neighborhood differences/weights and writes transformed bytes to the supplied output pointer. Its only direct external dependencies are synchronization primitives:

- `EnterCriticalSection`;
- `LeaveCriticalSection`;
- `WaitForSingleObject`;
- `SetEvent`.

It has no secure-memory, SMC, device or MMIO call.

`FUN_18001f420` likewise contains explicit per-pixel arithmetic over source and destination arrays, with synchronization around four worker partitions. It is CPU code, not an accelerator submission path.

## 5. Reachable import surface

From the transfer dispatcher through depth 3, the only external imports are:

- `QueryPerformanceFrequency`;
- `QueryPerformanceCounter`.

Those are reached through the timing helper.

Expanding the SWAB core to depth 5 adds only ordinary runtime services:

- critical sections;
- events;
- thread create/wait;
- `GetLastError` / `CloseHandle`;
- malloc/free;
- exception/runtime metadata support.

The extracted worker graphs contain zero references to:

- `CreateSecureSection`;
- `OpenSecureSection`;
- `AssignMemoryToSocDomain`;
- `MapSecureIo` / `ProtectSecureIo` / `UnmapSecureIo`;
- `FlushSecureSectionBuffers`;
- `EmitSmc` / `AwaitSmc`;
- `DmaMapMemory`;
- `GetExposedSecureSection`;
- QcTrEE/QSEE/QTEE;
- device IO control.

This is the key E004cf result.

## 6. Cache/coherency contract

No per-frame transfer path contains `FlushSecureSectionBuffers`.

The extracted worker graph also contains no flush call.

The trustlet **does** call `FlushSecureSectionBuffers` during the internal target setup path after the successful `AssignMemoryToSocDomain()` operation.

Therefore the worker itself assumes that the established protected mappings and platform coherency rules make the camera-written source visible to the trusted CPU worker. It does not perform a per-frame secure-section cache maintenance operation.

A Linux implementation must not infer from this that no coherency work is ever required. The parity requirement is instead:

> whatever provider establishes the internal/external trusted mappings must present coherent CPU-visible contents to the trusted worker without reopening the pages to ordinary HLOS.

That responsibility belongs below the worker.

## 7. Minimum trusted-worker execution environment

The Windows transfer algorithm itself needs only:

1. **trusted CPU execution** outside ordinary HLOS/VTL0 access;
2. simultaneous readable mapping of the internal protected capture target;
3. simultaneous writable mapping of the external protected sample;
4. private scratch/config memory;
5. basic heap allocation;
6. threads/events/locks or an equivalent scheduling implementation;
7. ordinary memory loads/stores, memcpy/memset semantics and integer pixel arithmetic;
8. coherent visibility of camera-produced source contents.

It does **not** require, during each transfer:

- direct camera hardware programming;
- SecureISP KMD interaction;
- QcTrEE PassThrough;
- QTEE object invocation;
- SHM bridge creation;
- memory ownership assignment;
- secure-section creation/open;
- an HTP/Hexagon/DSP transform.

This substantially narrows the missing Linux component: it is a **protected CPU execution habitat with access to both protected objects**, not a proprietary image accelerator.

## 8. Windows one-shot decision

A Windows one-shot is not needed for E004cf.

Static control-flow and pixel-loop evidence directly resolves the question that matters for Linux architecture: the worker performs CPU memory processing after mappings are established and does not make a per-frame privileged service call.

A Windows trace becomes worthwhile again if we need to resolve timing, branch-selection conditions, exact image output behavior, or a runtime coherency question that static code cannot settle.

## Architectural consequence

E004cd's blocker can now be stated more precisely.

We do **not** need to discover a hidden Qualcomm camera processing service to reproduce the frame transform.

We need a trusted execution environment that can simultaneously access:

- the internal CP_CAMERA-backed source while the camera has written it;
- the external HLOS-inaccessible protected sample;

and run ordinary CPU code over them.

That opens a narrower design search than before, but it does not authorize normal Linux kernel/HLOS execution: HLOS running the same memcpy/filter code would violate E004cc's VTL0-no-access contract.

## What remains forbidden

Do not yet:

- move the worker into normal Linux kernel/userspace;
- temporarily map either protected object into HLOS;
- use HLOS memcpy as a fallback;
- guess a trusted owner VMID/service just because the algorithm is CPU-only;
- enable QCOMTEE/FF-A/Gunyah/pKVM to experiment;
- alter external/internal ownership at runtime;
- activate Linux SecureISP protected runtime.

## Next gate

Proceed to **E004cg — protected CPU-worker habitat feasibility**, static first.

Now evaluate candidate trusted execution habitats specifically against the reduced E004cf requirements:

1. can they run ordinary ARM64 CPU code/threads or an equivalent worker loop;
2. can they simultaneously access a CP_CAMERA-associated source and a separate HLOS-inaccessible destination;
3. can HLOS remain excluded for the entire transfer;
4. can they provide a reversible lifetime and coherent mappings;
5. can any candidate be tied to an actual X1E/SP11 signed or resident execution authority rather than a hypothetical transport;
6. determine whether the absence of a signed QTEE camera app remains fatal now that no special camera API is required.

Stay static unless a Windows one-shot answers a concrete ambiguity that affects this habitat selection.
