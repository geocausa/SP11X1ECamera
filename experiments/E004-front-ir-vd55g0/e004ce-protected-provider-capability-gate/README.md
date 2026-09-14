# E004ce — compile-only protected-provider capability gate

## Result

**PASS: the CAMSS protected-pipeline compile contract now encodes the provider properties that must all be proven before any external protected-sample backend can be considered parity-ready, while preserving byte-identical executable `.text` and zero runtime effect.**

E004ce does not select, instantiate or invoke a backend. It contains no allocator, VMID, service UID, secure transport, heap name, ownership call, runtime selector or fallback implementation.

## Why this gate exists

E004cd established that Linux already has useful pieces:

- a protected DMA-BUF façade;
- a low-level memory ownership reassignment primitive;
- multiple generic trusted/hypervisor transports.

But none of those pieces alone is the Windows protected-sample provider.

The dangerous failure mode is therefore not only a crash. It is an implementation that *looks* secure because it uses a protected-sounding heap or secure-world primitive, while still allowing normal HLOS CPU access or lacking a trusted worker.

E004ce makes that impossible to paper over in the abstract contract.

## Required provider capabilities

A future provider must prove all six capabilities:

1. `HLOS_ACCESS_REVOKED`
   - ordinary HLOS CPU read/write/execute access is hardware-enforced away for the protected lifetime;
2. `TRUSTED_OWNER_RESOLVED`
   - the concrete trusted owner identity is known from authority, not guessed;
3. `TRUSTED_WORKER_VISIBLE`
   - the trusted worker can actually map/use the external sample while HLOS remains excluded;
4. `RELEASE_PATH_RESOLVED`
   - ownership/mapping can be reversed safely at object teardown;
5. `NO_HLOS_TRANSFER_FALLBACK`
   - there is no temporary normal-HLOS memcpy or remap escape hatch;
6. `EXTERNAL_TARGET_DISTINCT`
   - the external protected consumer sample remains separate from the internal camera hardware target.

The required mask is compile-time fixed to `0x3f` solely as a local bitset consistency check. It is **not** a firmware ABI or runtime selector.

## Provider phase

The representation has only three abstract phases:

- `UNBOUND`;
- `AUTHORITY_INCOMPLETE`;
- `PARITY_READY`.

`PARITY_READY` is a semantic state only. No code transitions into it in E004ce.

## Explicit negative state

`camss_protected_provider_capability_contract` carries fields that make unsafe shortcuts visible:

- `runtime_binding_authorized`;
- `concrete_trusted_owner_resolved`;
- `concrete_release_authority_resolved`;
- `external_reuses_internal_target`;
- `hlos_transfer_fallback_allowed`.

A real backend should only ever become bindable when the required capability set is complete and the unsafe booleans remain false.

E004ce deliberately does **not** implement the runtime predicate yet. That would require a real backend instance and authority that do not exist.

## Mechanical zero-runtime proof

E004ce uses the same production CAMSS preimage as E004bq/E004bu/E004bw:

- `camss-video.c` SHA-256 `2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4`;
- `camss-video.h` SHA-256 `69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982`.

Both baseline and scaffold build with:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

Their executable `.text` sections are byte-for-byte identical:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`

The only production C changes are:

- include the compile-contract header;
- call an inline function containing only `BUILD_BUG_ON()` assertions.

No generated module was installed or loaded.

## Concrete backend leak check

The new contract and newly added C lines contain zero references to concrete implementation choices such as:

- Qualcomm ownership APIs or VMIDs;
- QCOMTEE/QSEECOM;
- FF-A;
- Gunyah;
- pKVM;
- TEE shared-memory objects;
- protected heap names;
- camera domain IDs;
- service UIDs.

This keeps provider authority separate from the interface shape.

## Architectural consequence

The codebase now has three independently encoded protected-camera boundaries:

1. **internal capture-target lifetime/visibility** — E004bu;
2. **external protected-sample identity/extent/lifetime** — E004bw;
3. **provider readiness / security capability gate** — E004ce.

That is enough structure to add a real backend later without letting allocator choice, hardware-target ownership and external consumer identity collapse into one object.

## What remains forbidden

Do not yet:

- instantiate `camss_protected_provider_capability_contract` in runtime code;
- set `runtime_binding_authorized`;
- add a concrete owner ID, permission, service UID or secure transport;
- call memory-ownership or SHM-bridge APIs;
- register a protected-record heap;
- add HLOS copy fallback;
- reuse the internal hardware target as the external sample;
- activate Linux SecureISP protected runtime.

## Next gate

Proceed to **E004cf — trusted-worker execution contract extraction**, static first.

The provider blocker is now precisely the worker side, so extract the exact Windows VTL1 worker requirements from `QcISPTrustlet8380.dll`:

1. enumerate the worker's direct dependencies after both secure mappings already exist;
2. separate pure memory/format work from IUM/secure-kernel calls;
3. identify whether the transfer algorithms require any camera hardware or secure-world service during the copy itself;
4. characterize source/destination visibility and cache/flush assumptions;
5. determine the minimum execution environment a Linux trusted worker would need;
6. use a Windows one-shot only if static code cannot resolve a behavior that changes that minimum environment.

No Linux secure runtime call is authorized by E004cf.
