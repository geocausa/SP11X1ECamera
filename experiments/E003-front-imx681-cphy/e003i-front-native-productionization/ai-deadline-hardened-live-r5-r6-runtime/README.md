# E003i-AI — deadline-hardened bounded live R5/R6 runtime

Status: **prepared fresh one-shot runtime; not yet executed.**

AI is the fresh runtime after AH proved the expanded CCT/AEC selector live but missed the deferred request5 handoff. AH reached STREAMON, captured G1-G3, computed the correct R5 (`493117d0…6ca5`), then received `-EBUSY` because the runner had already crossed its non-blocking R5 Epoch0 gate and unwound. AH was consumed, not retried, and Golden return passed.

AI changes no camera kernel code and preserves the accepted deferred-IQ ingress. The only producer changes are deadline hardening: CPU11 affinity, nice -20 under the already-root live child, fixture-free synthetic prewarm before READY, exact temporal/Tintless reset after prewarm, cyclic-GC disablement, and deferral of child snapshot/capsule/manifest writes and per-generation logging until after R5/R6 have both been submitted. It does not use an RT scheduling policy.

The mandatory Golden prearm gate SHA-pins the producer and hardware assets, re-runs the fixture-free all-CPU contention proof, and replays the exact consumed-AH G1-G3 evidence. That evidence must still generate R5 `493117d029bac7910b41292e738685fdfe5a22ec52676fb415a27bfbb3c46ca5` and predicted R6 `dac798043c9d14e8118bbed803bb2b3aa7f1a7532d2e4838ee88790c69c18115`. Retained-Z R5/R6 identities must also remain unchanged.

R4 is generated template-free before STREAMON. R5 comes only from live G2 paired TL_BG+3A and R6 only from live G3. The parent independently captures six QC10C frames and paired generation-tagged stats. Any scheduling, pairing, FIFO, provider, ordering, stream, or kernel-health failure consumes the one-shot authorization; no same-boot retry is permitted and return to Golden is mandatory.
