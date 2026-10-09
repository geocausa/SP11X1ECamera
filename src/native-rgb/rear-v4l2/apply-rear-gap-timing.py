#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Add scalar completion-prefix and handoff timing; preserve all queue tokens."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def apply(camss):
 camss=Path(camss);p=camss/"native-rear-queue.inc";s=p.read_text()
 def tagged(body):
  return "\n/* GAP_TIMING_BEGIN */\n#ifdef __KERNEL__\n"+body+"\n#endif\n/* GAP_TIMING_END */\n"
 def sub(old,new):
  nonlocal s
  assert s.count(old)==1,(old,s.count(old))
  s=s.replace(old,new,1)
 sub("#define NATIVE_REAR_QUEUE_INC\n","#define NATIVE_REAR_QUEUE_INC\n"+tagged('#include "native-rear-gap-timing.inc"'))
 sub("  buffer->vb.vb2_buf.timestamp = ktime_get_ns();",
     "  buffer->vb.vb2_buf.timestamp = ktime_get_ns();"+tagged("  native_rear_gap_complete(buffer->vb.vb2_buf.timestamp, buffer->vb.sequence);"))
 sub(" native_rear_queue_complete(video, 0, true, true);\n next = kzalloc",
     tagged(" memset(&native_rear_gap, 0, sizeof(native_rear_gap));\n native_rear_gap.owner = result->owner_epoch;")+" native_rear_queue_complete(video, 0, true, true);\n next = kzalloc")
 for stage in ["prepare","program","collect","retire"]:
  anchor="  profile_"+stage+" += ktime_get_ns() - tick;"
  sub(anchor,anchor+tagged("  native_rear_gap_stage_record(&native_rear_gap."+stage+", ktime_get_ns()-tick, video->native_rear_completed);"))
 anchor=" profile_observe += ktime_get_ns() - tick;\n  if (ret) {"
 sub(anchor," profile_observe += ktime_get_ns() - tick;"+tagged("  native_rear_gap_stage_record(&native_rear_gap.observe, ktime_get_ns()-tick, video->native_rear_completed);")+"  if (ret) {")
 log = (
 ' dev_info(vfe->camss->dev,\n'
 '  "NATIVE_REAR_GAP_TIMING owner=%llu completions=%u intervals=%u span_ns=%llu gap_min_ns=%llu gap_max_ns=%llu max_gap_sequence=%u long_gaps=%u first_long_sequence=%u prepare_max_ns=%llu prepare_max_sequence=%u observe_max_ns=%llu observe_max_sequence=%u program_max_ns=%llu program_max_sequence=%u collect_max_ns=%llu collect_max_sequence=%u retire_max_ns=%llu retire_max_sequence=%u max_gap_prepare_ns=%llu max_gap_observe_ns=%llu max_gap_program_ns=%llu max_gap_collect_ns=%llu max_gap_retire_ns=%llu prefix_buffers=80 long_gap_threshold_ns=50000000 timestamp_precision_ns=1000 policy_changes=0 pixel_bytes_read=0\\n",\n'
 '  native_rear_gap.owner, native_rear_gap.completions, native_rear_gap.intervals,\n'
 '  native_rear_gap.span_ns, native_rear_gap.gap_min_ns, native_rear_gap.gap_max_ns,\n'
 '  native_rear_gap.max_gap_sequence, native_rear_gap.long_gaps, native_rear_gap.first_long_sequence,\n'
 '  native_rear_gap.prepare.max_ns, native_rear_gap.prepare.max_sequence,\n'
 '  native_rear_gap.observe.max_ns, native_rear_gap.observe.max_sequence,\n'
 '  native_rear_gap.program.max_ns, native_rear_gap.program.max_sequence,\n'
 '  native_rear_gap.collect.max_ns, native_rear_gap.collect.max_sequence,\n'
 '  native_rear_gap.retire.max_ns, native_rear_gap.retire.max_sequence,\n'
 '  native_rear_gap.max_gap_prepare_ns, native_rear_gap.max_gap_observe_ns,\n'
 '  native_rear_gap.max_gap_program_ns, native_rear_gap.max_gap_collect_ns, native_rear_gap.max_gap_retire_ns);')
 sub(" kfree(next);\n/* FULL_CACHE_BEGIN */"," kfree(next);"+tagged(log)+"/* FULL_CACHE_BEGIN */")
 p.write_text(s);(camss/"native-rear-gap-timing.inc").write_bytes((HERE/"native-rear-gap-timing.inc").read_bytes())
 return dict(scalar_timing_only=True,per_frame_logs=False,first80_application_prefix=True,
             stage_maxima_include_all_rolling_handoffs=True,policy_changes=0,
             all_original_queue_source_tokens_unchanged=True,timing_release_authority=False,pixel_bytes_read=0)
