# E007n — rear TMC141 unfiltered call-site input oracle

Parent: E007m consumed/inconclusive plus the E007k static TMC141 contract.

Status: **PREPARED / NOT YET CONSUMED**.

E007m proved the two source-locked BL breakpoints resolve and the rear 4K holder streams, but its inherited request/mode early-exit logic prevented every dump. E007n therefore makes no request-ID or mode assumption.

It breaks at QcDeviceMFT8380+0x9241C0 and +0x924258, increments a private hit index, logs the candidate request/site/mode metadata, and captures the first 40 call-site input states. The only target-resume command is one final gc after all dump commands have been considered.

Each bounded H01..H40 state may contain TUNE, RUNTIME, DESC, the processed 1024-float HIST, PRE_SRC/PRE_DST/PRE_COEF and bounded optional COMMON/CTRL/FACE slices. The two callsites remain mutually exclusive branches of the same solver call.

No optical pixels are copied. Raw values stay private.

Offline acceptance will determine the real request/mode mapping from the captured runtime state, reproduce semantic SRC/DST, compare against the already accepted E007j post-solver vectors, and regenerate COEF with E007k. Captured-state replay is not accepted.
