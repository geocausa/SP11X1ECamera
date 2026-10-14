# Typed coherent CDM command owner

Source35 reuses the retained native coherent allocator, complete DMA extent
checks and unused-only cleanup. The prior-work audit is
docs/UPSTREAM-COMMAND-OWNER-PRIOR-AUDIT-20261014.json; source34 submission
and source33 RAW hardware results remain distinct.

The opaque program object allocates one padded coherent page from the supplied
parent DMA device, pins the CAMSS module and device, validates the full32-bit
extent and builds the retained independent1204-byte REG_CONT minimum program.
Its CPU pointer is not published by the API, and no raw payload is accepted.
One program may exist per power owner. Owner/request/allocation identities
remain immutable. Parent power then CDM mutexes serialize all operations.

Submission consumes the software attempt and transfers pre-acquired independent
allocation/device/module holds to the backend retention callback. Once retained,
success, timeout and pre-STORE/late faults all refuse destroy/rewrite/retry.
A second backend allocation-identity check also rejects destruction if the
program retained flag is lost. No production exposed-command release API exists.
Unused or refused-before-retention allocations unwind in reverse order and
zero the coherent memory before free.

A detach-readiness predicate refuses outstanding programs, PM/hardware state
and faults. It has no runtime parent caller and does not veto the kernel's void
platform remove. Device/module references do not protect devres IRQ/mapping/
clock handles from unbind. The parent must provide actual pre-detach exclusion
or a resource-retaining teardown design, keep power/backend/handle storage live
and wire that admission before any hardware test. The existing binding is
managed; this gap is explicit and remains open.

The pure compiler headers are reused with unchanged functional code. Two need
whitespace-only kernel style corrections in this package; normalized code
matches originals and all three strict module builds are byte identical.
The compiler's hypothetical CFA/precision/bypass/optical domains remain
unqualified. The owner does not complete PIX/CSID/BUS/params/stats/libcamera/IPA
startup, and the sleepable submission cannot be called in IRQ params context.

prepare.py/build-worker.py reuse the sparse immutable-parent overlay and
strict ARM64 kernel26 ABI MO build. test-owner.py executes the complete actual
owner C, actual headers, independent compiler and actual submission bodies
against the retained hosted MMIO/IRQ adapter. Four allocation fault stages,
DMA-range/identity/alias/admission/cleanup gates, completion faults and missing
retained-flag refusal are covered. Eight compiled unsafe mutations must fail
under GCC/Clang ASan/UBSan. Fixture-only simulated reboot frees mock retained
memory; this is not a production free path or physical retirement proof.
Intentional mutation tests use a per-process core limit0.

qualify.py checks all source/module/model/compiler/replay pins and no-runtime
call references, then writes docs/UPSTREAM-CDM21-COMMAND-OWNER-20261014.json.
No install/load/MMIO/physical DMA/reboot occurs. The standard unsigned patch
still needs author DCO/signoff; CAMSS new-file advisory has been reviewed.
Original provenance/attribution and full series bindings/API review stay open.

Next audit/reuse the native resource mapping and retained standard CDM binding/
power ownership, implement real parent lifetime and detach handling, then
complete independent PIX startup and qualify a guarded physical transaction.
