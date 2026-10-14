# Fresh standard RAW sustained/starvation qualification11
Reuse audit docs/UPSTREAM-RAW-STRESS-PRIOR-AUDIT-20261014.json verifies native
ae80/83/84 actual600-frame records and600/600 recovery after1s/5s freezes,
plus the earlier1803-frame native RAW run. No old hardware identity is replayed.

Kernel26/DT29/PHY31/CAMSS33 remain byte-identical to qualified10. New lab-only,
read-only observer snapshots the matched owned FULL VFE1 RDI0 under locks:
active pipeline/PM/module ownership, empty FIFO/no pending buffers, WM-paused
software state and actual CFG0 readback. No register, queue, DMA or PM writes.
44 actual observer cases/compiler ASAN/UBSAN, three compiled unsafe mutations,
strict ARM649776-byte module/style PASS. Helper is excluded from upstream ABI.

Planned900-frame standard RAW baseline plus180 after1s and180 after5s consumer
SIGSTOP/SIGCONT. Actual stopped-process state and empty/paused WM observed before
resume; exact12672000-byte planes, monotonic driver completion timestamps and
dequeued sequence continuity required. Intentional stalls may lose sensor frames:
completion sequence is not an independent hardware sensor-frame counter.
Pixels are discarded locally by default v4l2-ctl. No pixel files/hash/spatial export.
Real child stop/resume and observer-refusal/timeout/reap behavior is tested with
scalar fixtures. Any failure skips core route mutation/unload and returns Golden.
Complete23-signature camera/kernel guard includes unexpected missing buffers and
invalid completion routing;10 retained final/return logs also pass that guard.
One-use11, unique private module tree,180s independent watchdog,120s observer bound.
No OS suspend/hibernate, image-quality/ISP/libcamera/IPA/full-fault/release claim.
Provenance/public GPL source may be reused with attribution; private tuning stays
out, and whole series attribution/bindings/API/generalisation review remains open.
