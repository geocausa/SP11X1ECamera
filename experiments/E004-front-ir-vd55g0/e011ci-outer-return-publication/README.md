# E011CI original statistics and mode configuration attachment

Status: **PASS, bounded source-only prefix**. Base: `175f02a0124f356981585ac1bd5624eba70f91c6`.
L4 source/control initialization; L2/L3 hardware gates remain closed.

Original outer entry `0x36CBA0` now runs through the stop before `0x36D63C`.
Three SHA-pinned same-SP11 tuning sources and four owned placements pass all
12 cases. Actual original code attaches the 1664-byte statistics manager at
inner+40 and a separate 96-byte configuration object at inner+91952.
The independent model starts with the E011CH prefix snapshot and allows only
those two predicted qword stores in the entire 606264-byte inner. The complete
72-byte outer remains unchanged and the public output remains zero.
Attachments retained through the complete outer return are not yet qualified.

The configuration object comes from the original 96-byte allocation at
`0x36D52C`, whose original return is captured at `0x36D530`. It is the exact
receiver of complete 224-byte `0x395940`, which returns in each case. Two
original interface-slot312 accessors, three interface-slot8 mode-record
factory calls and three actual source-created32-byte record-slot0 accessors
per case pass exact live receiver and target checks. Original targets are
`0x3A8730`, `0x3A88E0`, and `0x3A8820`; none is replaced or given a success stub.
Complete optional configuration field semantics are not claimed.

Inherited full statistics checks still pass: 180 independent entire152-byte
records before/after attachment setters,1440 original statistics record
initializers,292 core vector initializers and516 exact cache lookups. Source
list membership, live object extents, rings, all allocation guards and entire
preexisting arena/native/serialized/mapped-image immutability pass. Exact
caller/diagnostic memory deltas and original first-kind4 descriptor search
remain checked. Count0/mode/list/context/TLS are explicit owned inputs.

The accepted OS fixture remains the E011CH single-thread owned48-byte outer
lock, with Enter/Leave import pointers redirected only to an exact object+8
recursive depth checker. The stop still holds that lock; release and
concurrency remain open. New diagnostic dispatches require exact dynamic
origin at already-qualified global16A4230. No logger16A4228 admission or new
TLS initialization-success stub is used.

Full-outer exploration reached a separate C-runtime critical section at
mapped-imageRVA16A3000, then stopped on an unmapped locale read atCC6140 when
that second lock was modeled experimentally. Neither that model nor the
extended first-source36DC58 prefix is accepted. Earlier receiver/allocation/
attachment assumptions caught by assertions are retained private and excluded.

NEXT **E011CJ** qualifies the remaining ordinary fields after36D63C and the
diagnostic/C-runtime environment, then final outer-inner attachment, public
output publication, complete outer return and lock release. Actual live Default
input producers, filename lifetime/destruction/reuse, full baseline bootstrap/
preflight, RS policy, independent enabled WM16 IRQ/consumed IOVA/DMA/IOMMU
retirement and optical parity remain open. Native rear runtime denied;
optional AI/effects/HDR/catalogue deferred.

Accepted job `job_inS4McuZVHMi2RE-8gAZZnCy` exited0 (18:16:38–18:18:10 UTC,
2026-10-02). See [RESULT](RESULT.json), [scalar matrix](ATTACHMENT-SAFE.json),
[Golden guard](GUARD-SAFE.json), [next scope](NEXT-SOURCE.json) and the
[independently written verifier](source-private.py). Original DLL/tuning/
disassembly and private excluded probes stay on SP11. Only original instruction
execution in guarded owned Unicorn memory was used; no Windows driver invocation,
Start/deployment/reboot/MMIO/kernel/C change or Linux image test occurred.
Golden FullIOv19c/all3 protected payload hashes and historical checkouts remain
unchanged. Rollback: revert source-only files, retain private excluded probes.
