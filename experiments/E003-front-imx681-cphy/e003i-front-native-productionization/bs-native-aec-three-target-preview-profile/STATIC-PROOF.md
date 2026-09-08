# BS proof boundary

BS is a native API reduction over already-proven BR/BC semantics; it introduces no new live-Windows claim.

The relevant native dataflow is mechanically constrained:

- `basic_safe()` reads only `target_log[E003I_LANE_SAFE]`;
- `get_exposure_info()` indexes `target_log[t]`, and the only calls use `t=0` (Short) and `t=1` (Long);
- after DRC aggregation, the active single-exposure tail overwrites final lanes 3..6 with final Short before PopulateOutput.

BC independently pins that final-lane overwrite to Windows `activeExposureCount == 1`. BR is fresh-verified before BS differential testing.

The BS wrapper therefore copies exactly three public target doubles into a zeroed private seven-lane carrier. A 2048-state differential corpus randomizes all four hidden BR target lanes twice per state and proves both BR variants and BS are byte-identical over the complete output struct.

Full seven-lane history records are intentionally retained. Locked/snapshot/preflash/HDR/multi-exposure modes remain outside this checkpoint.
