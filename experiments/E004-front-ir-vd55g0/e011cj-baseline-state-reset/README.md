# E011CJ original post-attachment baseline state reset

Status: **PASS, bounded source-only reset**. Base: `64bf7bd01c70b2219189fece5648efc7db096cf9`.

Original outer entry `0x36CBA0` reaches the E011CI attachment boundary at
`0x36D63C`, then resumes unchanged original instructions through the stop before
`0x36D784`, the next allocation call. The new 328-byte prefix has no original
allocation, publication or lock release. Three SHA-pinned same-SP11 sources and
four owned placements pass 12 unmodified cases, plus 12 explicit poison fixtures.
Only the prescribed reset fields are poisoned at the boundary. This validates
actual resets of nonzero state; it does not establish real-world object reuse.

The independent schema predicts three exact zero-fill calls (352,352,1608 bytes),
51 original scalar store chunks, and the internal pointer inner+91816 to
inner+92976. A complete 606264-byte inner comparison admits only these predicted
writes. The full arena comparison preserves every other byte, including every
other existing object and gap. All allocation guards, native heap, serialized
source, mapped image and exact caller/TLS deltas remain checked. Original store
sites, scalar values and receiver offsets are checked as they execute. Field
names and full optional-field semantics remain unqualified.

The actual 1664-byte statistics manager at inner+40 and distinct 96-byte mode
configuration at inner+91952 are retained to this stop. The 72-byte outer is
unchanged, public output remains zero, and the explicitly owned single-thread
outer lock remains held. Complete outer return/release and concurrency are open.
Inherited checks pass 360 independent entire152-byte records,2880 original
statistics initializers,584 core vector initializers and1032 cache lookups. No
numeric callback or new TLS-initialization success substitute is admitted.

Separate private full-tail exploration still stops in the uninitialized CRT
fixture: original CC6120/CC6130 read null image globals16A2A58/16A2A50 before
CC6140 attempts an8-byte read at address24. The second CRT-lock model at16A3000
is exploratory and excluded. These observations identify missing fixture
state, not a Windows/Linux camera failure. No null-page mapping or guessed
locale object is added. The earlier first-source36DC58 extension is also excluded.

NEXT **E011CK** independently qualifies the remaining original object/module/
context/cache producers from36D784, then the CRT environment before final outer
attachment/output publication/return and balanced lock release. Actual live
Default producers, filename lifetime/destruction/reuse, full bootstrap/preflight,
RS policy, independently enabled WM16 IRQ-consumed IOVA-DMA-IOMMU retirement and
optical parity stay open. Native rear runtime remains denied; clean controllable
front/back baseline first, optional AI/effects/HDR/catalogue deferred.

Accepted job `job_jxG0wgZ9UzJFCze74d1hrQyW` exited0 (18:44:17–18:47:22 UTC,
2026-10-02). See [RESULT](RESULT.json), [scalar matrix](BASELINE-SAFE.json),
[Golden guard](GUARD-SAFE.json), [next scope](NEXT-SOURCE.json) and the
[independently written verifier](source-private.py). DLL/tuning/disassembly and
excluded probes stay private on SP11. Execution uses guarded owned Unicorn
memory, with no Windows-driver invocation, Start/deployment/reboot/MMIO/C/kernel
change or Linux image test. Golden FullIOv19c/all3 payload hashes and historical
checkouts remain unchanged. Rollback: revert this source-only checkpoint and
retain the accepted E011CI baseline and private excluded probes.
