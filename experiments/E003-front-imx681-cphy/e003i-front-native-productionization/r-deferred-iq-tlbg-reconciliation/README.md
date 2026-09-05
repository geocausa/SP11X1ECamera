# E003i-R — reconcile deferred live IQ with generation-tagged TL_BG

Status: **static PASS; runtime not yet executed**.

The mutable external CAMSS worktree had drifted back to the E003i-D pre-deferred-IQ `camss.c` before E003i-Q was applied. The durable E003i-L patch/manifest remained correct in Git. This checkpoint rebases and reapplies E003i-L on top of the accepted E003i-Q generation-tagged TL_BG source.

Resulting contract:

- request4 is the only IQ capsule required before STREAMON;
- request5/request6 are accepted on the same exclusive V4L2 fd while the live worker is active and are consumed at their steady Epoch0 gates;
- all six E003i-Q TL_BG publication points remain present before aux-slot retirement/reuse;
- TL_BG stays a read-only latest snapshot with explicit generation/source sequence, not a request-count FIFO;
- the reconciliation adds no new camera MMIO operations;
- Golden ABI module build passes.

This checkpoint changes source composition only. It does not by itself authorize a same-boot retry, alter persistent Golden, or claim runtime validation of late IQ control writes / TL_BG reads.
