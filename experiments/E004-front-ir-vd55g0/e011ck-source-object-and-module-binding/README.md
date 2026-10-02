# E011CK original source object and module binding

Status: **PASS, bounded source-only prefix**. Base: `c4c9d4c2055160883d4bc1a0dbb864a886a15ae3`.

Original entry36CBA0 reaches the independently checked E011CJ stop before36D784,
then resumes unchanged instructions through the stop before36DC58. Three pinned
same-SP11 sources and four owned placements pass12 unmodified cases plus12
explicit scalar poison fixtures. No original numeric callback is replaced.

Original code creates1088-byte and120-byte objects and attaches them at inner+16
and inner+24. Independent full payload models check both objects: predicted
vtable/inner/child links, constants and every remaining zero byte. The1088 object
has six source-created488-byte child links and a48-byte zero buffer. The120 object
links original240/880-byte children. The exact17-allocation sequence, extents,
liveness and guards pass. Complete488/32/240/880 child payload semantics are not
claimed; these accepted models do not establish real object reuse or destruction.

Two actual additional GetTag returns, with exact original manager, name literal,
owned mode and count0 arguments, match independently built core cache entries26
(aecxface440-byte object) and31 (aecxmetering624-byte object). Original field links
are inner+592 -> face+352, inner+1192 -> face+408, inner+1792 -> metering+392 and
inner+2392 -> metering+448. Seventeen predicted original stores per case are
checked by site/offset/width/value and an independent entire606264-byte inner
comparison. All previous arena objects and gaps except that predicted inner
delta remain unchanged; only exact guarded new allocation payloads are admitted.

Original394048/39C1F8/370728 calls return under exact receivers;370728 uses actual
core+3840 and scalar arguments7/2. Three additional interface-slot312 accesses
per case execute original3A8730 after exact live receiver/target checks. Original
36DC54 calls F5DF00, which is strcmp, not memcpy. Each actual pair of7-byte
source strings compares equal without altering either input. An earlier private
probe's copy label was corrected before acceptance; E011BH supplies prior helper
authority. No source strings or original instruction text are exported.

Totals:24 independent whole-inner and1088/120 models,72 original helper returns,
48 additional source module returns,72 additional accessors,24 original equality
comparisons and408 guarded new allocations/exact inner store chunks. Inherited
360 independent152-byte records,2880 statistics initializers,584 core initializers
and1032 core cache lookups pass; including the additional returns gives1080 total
GetTag lookups. Native heap, serialized source, mapped image, exact caller/TLS
deltas and every allocation guard remain checked.

The original statistics+40 and mode+91952 links remain intact at this stop;
outer unchanged/public output zero/owned single-thread lock held. First-source
exploration to36DE04 reaches conditional context fields, including source symbol
IDs; it lacks the complete independent matrix model and is excluded. The528-byte
context selection producer remains unqualified. Earlier CRT null-global/read24
and second-lock probes also remain excluded. They are environment limitations,
not evidence of a Windows/Linux camera failure. No guessed locale object/null
mapping/TLS success/numeric stub or logger16A4228 admission is used.

NEXT **E011CL** qualifies conditional context fields after36DC58 and CRT source/
OS/global ownership before final output publication/outer-inner link/whole return
and balanced lock release. Actual live Default/filename/destruction/reuse, full
bootstrap/preflight/RS policy, independently enabled WM16 IRQ-consumed IOVA-DMA-
IOMMU retirement and optical parity remain open. Native rear runtime denied;
clean controllable front/back first, optional AI/effects/HDR/catalogue deferred.

Accepted job `job_tWe1wYE6U6NQ_PjpyMkIslGM` exited0,19:11:46–19:15:22 UTC,
2026-10-02. See [RESULT](RESULT.json), [scalar matrix](BINDING-SAFE.json),
[Golden guard](GUARD-SAFE.json), [next scope](NEXT-SOURCE.json) and the
[independently written verifier](source-private.py). Originals and excluded
probes stay private on SP11. Guarded owned Unicorn execution only: no Windows
driver invocation/Start/reboot/deployment/MMIO/C/kernel change or Linux image
test. Golden FullIOv19c/all3 payload hashes and historical checkouts unchanged.
Rollback: revert this source-only checkpoint; retain E011CJ and private probes.
