# E008e — rear startup-order Windows oracle

Parent Git: 5fb0e6a3eda1a05cf0347dcc5820f8f42fed5cca (E008d).

Status: WINDOWS ORACLE PASS / SAFE REDUCTION ONLY / NO LINUX REAR ISP RUNTIME.

## Purpose

E008d deliberately stopped with all ten rear VFE1 write masters disabled after
installing Linux-owned addresses. The remaining blocker was the exact Windows
startup order across RT-CDM work, BUS configuration/enable/address programming,
CSID start and later request work.

A fresh one-shot same-SP11 Windows Rear Color / VideoRecord / NV12
3840x2160 session was observed from external SP7 KDNET. Only event ordering was
retained. No pixel payload, DMA contents or Windows IOVA value was committed.

## Accepted runtime

The holder opened the OEM rear 4K stream, returned Success, exposed 91 valid
4K frame handles during the bounded hold, stopped cleanly and returned to the
protected Golden Linux boot. WINDOWS-RUNTIME.json is the durable runtime
record. The private raw KD log remains off-repo; SAFE-ORDER.json is its
redacted deterministic event reduction.

The accepted broad order is:

1. first RT-CDM batch, count 4;
2. ten BUS configuration callbacks;
3. nine BUS enable callbacks (FULL is one resource with two planes);
4. ten initial address writes;
5. second RT-CDM batch, count 6;
6. CSID start call;
7. ISP start completion;
8. later address writes / count-6 RT-CDM batches;
9. BUS disables at stop.

E008e intentionally did not identify resource IDs or distinguish the two
selector-2 call sites. E008f narrows those points.

## Safety

This checkpoint is observation-only. No Linux native rear ISP runtime was
performed. The Windows staging identity was consumed and must not be reused.
IR illumination / Hello were not enabled. The protected Golden kernel was
restored.
