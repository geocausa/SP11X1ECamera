# DK static proof

Parent checkpoint: `60335de` (`camera: rebase native AEC to request4 warmup`).

The DB worker validates STATS3A generation/source/slot, then validates the paired TLBG generation/source/slot before calling native AEC. Therefore the buffers passed to `persist_failure_pair()` are already identity-checked for the current target generation.

On the native-AEC error branch, `e003i_db_schedule_fail(&ctx->schedule)` occurs before `persist_failure_pair(...)`. The persistence routine uses the existing `save_file()` helper, which fsyncs each completed file. Evidence-write failure is logged but cannot clear the latched schedule or authorize another sensor write.

The persistence call exists only in the native-AEC failure branch. The original full-success save loop remains after audit join, six-generation completion, and schedule success. Thus no disk I/O is added to a successful per-generation deadline window.

The integrated helper still has exactly one `apply_sensor_controls()` runtime call site and the same three-write scheduler constants. DK makes no AEC or sensor arithmetic change.
