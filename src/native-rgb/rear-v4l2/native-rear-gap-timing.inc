/* SPDX-License-Identifier: GPL-2.0-only */
/* Scalar timing only: never grants exposure, completion or release authority. */
struct native_rear_gap_stage { u64 last_ns, max_ns; u32 max_sequence; };
struct native_rear_gap_profile {
 u64 owner, first_ns, previous_ns, span_ns, gap_min_ns, gap_max_ns;
 u64 max_gap_prepare_ns, max_gap_observe_ns, max_gap_program_ns;
 u64 max_gap_collect_ns, max_gap_retire_ns;
 u32 completions, intervals, max_gap_sequence, long_gaps, first_long_sequence;
 struct native_rear_gap_stage prepare, observe, program, collect, retire;
};
static struct native_rear_gap_profile native_rear_gap;
static void native_rear_gap_stage_record(struct native_rear_gap_stage *s,
                                          u64 ns, u32 sequence)
{
 s->last_ns = ns;
 if (ns > s->max_ns) { s->max_ns = ns; s->max_sequence = sequence; }
}
static void native_rear_gap_complete(u64 timestamp, u32 sequence)
{
 u64 gap;
 /* V4L2 timeval exports driver completion timestamps at microsecond precision.
  * Only the same first80 buffers that the existing application requests consumes.
  * Extra completions racing STREAMOFF are intentionally outside this prefix.
  */
 if (sequence >= 80U)
  return;
 timestamp = (timestamp / 1000U) * 1000U;
 if (!sequence) {
  native_rear_gap.first_ns = timestamp;
 } else {
  gap = timestamp - native_rear_gap.previous_ns;
  native_rear_gap.intervals++;
  if (!native_rear_gap.gap_min_ns || gap < native_rear_gap.gap_min_ns)
   native_rear_gap.gap_min_ns = gap;
  if (gap > native_rear_gap.gap_max_ns) {
   native_rear_gap.gap_max_ns = gap;
   native_rear_gap.max_gap_sequence = sequence;
   native_rear_gap.max_gap_prepare_ns = native_rear_gap.prepare.last_ns;
   native_rear_gap.max_gap_observe_ns = native_rear_gap.observe.last_ns;
   native_rear_gap.max_gap_program_ns = native_rear_gap.program.last_ns;
   native_rear_gap.max_gap_collect_ns = native_rear_gap.collect.last_ns;
   native_rear_gap.max_gap_retire_ns = native_rear_gap.retire.last_ns;
  }
  if (gap > 50000000ULL) {
   if (!native_rear_gap.long_gaps)
    native_rear_gap.first_long_sequence = sequence;
   native_rear_gap.long_gaps++;
  }
 }
 native_rear_gap.previous_ns = timestamp;
 native_rear_gap.span_ns = timestamp - native_rear_gap.first_ns;
 native_rear_gap.completions++;
}
