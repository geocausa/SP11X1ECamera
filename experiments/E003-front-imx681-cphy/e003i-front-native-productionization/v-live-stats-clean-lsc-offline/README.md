# E003i-V — live TL_BG evidence into clean stats-only LSC

Status: **PASS (offline)**.

V consumes the six corrected E003i-U `0xF020` snapshots as source-generation evidence only. It strips the 32-byte generation header, parses the exact `0xF000` Titan680 payload through stage N, then feeds the full parsed object into the same clean stage-M / stage-K Tintless-LSC backend with fresh locally constructed configuration, descriptors, wrapper/core and sequential temporal carry.

No U generation is called request4/request5/request6. Trigger/interpolation state is an explicit independent fixture: both the historical `0.342` and `0.0` ratio fixtures were run over the same six live generations. Four hostile-state/output-seed counterfactuals converge byte-identically for each fixture. Each fixture produces six distinct LSC0 outputs; reversing the source-generation order changes the final temporal output; and changing the trigger fixture changes all six outputs. This proves both live stats and trigger state are effective, separate clean-room inputs.

This checkpoint **does not authorize dynamic R5/R6 substitution**. The remaining boundary is exact source-generation/request selection plus live trigger-state acquisition. Source generation remains explicitly distinct from request ID. No camera runtime, module load, MMIO, reboot or V4L2 operation occurs in V.
