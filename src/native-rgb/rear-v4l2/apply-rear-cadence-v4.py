#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Remove only the extra rolling epoch wait; retain strict consumed-address proofs."""
from pathlib import Path
def apply(camss):
 p=Path(camss)/"native-rear-queue.inc";s=p.read_text()
 def sub(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a))
  s=s.replace(a,b,1)
 sub(" unsigned int idle = 0;\n int ret;",
     " unsigned int idle = 0;\n u64 profile_started = ktime_get_ns(), tick;\n"
     " u64 profile_drain=0, profile_pending=0, profile_prepare=0, profile_observe=0;\n"
     " u64 profile_epoch=0, profile_program=0, profile_collect=0, profile_retire=0;\n"
     " u32 profile_first_epoch = csid680_e008i_rear_epoch0_seq(csid);\n int ret;")
 # Time each existing stage. Instrument only the queue_run body.
 start=s.index("native_rear_queue_run(");prefix=s[:start];body=s[start:]
 def around(first,last,name):
  nonlocal body
  assert body.count(first)==1 and body.count(last)==1,(name,first,last)
  body=body.replace(first,"  tick = ktime_get_ns();\n"+first,1)
  body=body.replace(last,last+"\n  profile_"+name+" += ktime_get_ns() - tick;",1)
 around("  ret = native_rear_queue_drain(csid, pair, result->owner_epoch, cursor);",
        "  ret = native_rear_queue_drain(csid, pair, result->owner_epoch, cursor);","drain")
 around("  spin_lock_irqsave(&vfe->output_lock, flags);",
        "  spin_unlock_irqrestore(&vfe->output_lock, flags);","pending")
 around("  ret = native_rear_queue_prepare(vfe, pair, next, buffer, result->owner_epoch);",
        "  ret = native_rear_queue_prepare(vfe, pair, next, buffer, result->owner_epoch);","prepare")
 # There are two observes: first startup validation and one each generation.
 first=" ret = native_rear_queue_observe_stable(vfe, csid, pair, result, cursor);"
 assert body.count(first)==2
 body=body.replace(first," tick = ktime_get_ns();\n"+first+"\n profile_observe += ktime_get_ns() - tick;")
 around("  ret = csid680_e008i_rear_poll_next_epoch0(csid, epoch, req->epoch_timeout_us);",
        "  ret = csid680_e008i_rear_poll_next_epoch0(csid, epoch, req->epoch_timeout_us);","epoch")
 around("  ret = e008h_rear_write_slot_addresses(vfe, pair, 1);",
        "  ret = csid680_native_rear_output_update(csid, result->owner_epoch);","program")
 around("  ret = e008k_rear_collect_done(csid, pair, result->owner_epoch,",
        "                               req->done_timeout_us, cursor);","collect")
 around("  ret = native_rear_queue_retire_stable(vfe, csid, pair, result, cursor);",
        "  ret = native_rear_queue_retire_stable(vfe, csid, pair, result, cursor);","retire")
 anchor=" kfree(next);"
 assert body.count(anchor)==1
 log = (
 ' dev_info(vfe->camss->dev,\n'
 '  "NATIVE_REAR_CADENCE elapsed_ns=%llu epoch_delta=%u handoffs=%u drain_ns=%llu pending_ns=%llu prepare_ns=%llu observe_ns=%llu epoch_wait_ns=%llu program_ns=%llu collect_ns=%llu retire_ns=%llu policy_changes=0 pixel_bytes_read=0\\n",\n'
 '  ktime_get_ns()-profile_started, csid680_e008i_rear_epoch0_seq(csid)-profile_first_epoch,\n'
 '  result->queue_handoffs, profile_drain, profile_pending, profile_prepare, profile_observe,\n'
 '  profile_epoch, profile_program, profile_collect, profile_retire);\n')
 body=body.replace(anchor,anchor+"\n"+log,1)
 epoch_wait = (
 "  epoch = csid680_e008i_rear_epoch0_seq(csid);\n"
 "  tick = ktime_get_ns();\n"
 "  ret = csid680_e008i_rear_poll_next_epoch0(csid, epoch, req->epoch_timeout_us);\n"
 "  profile_epoch += ktime_get_ns() - tick;\n"
 "  if (ret) {\n"
 "   e008d_rear_release_partial(vfe, &next->dma[1]);\n"
 "   break;\n"
 "  }\n")
 assert body.count(epoch_wait)==1
 body=body.replace(epoch_wait,"",1)
 assert body.count("  u32 epoch;\n")==1
 body=body.replace("  u32 epoch;\n","",1)
 body=body.replace("policy_changes=0 pixel_bytes_read=0","policy_changes=1 pixel_bytes_read=0",1)
 p.write_text(prefix+body)
 return dict(aggregate_timing_only=True,per_frame_logging=False,queue_policy_changes=1,
             only_per_handoff_epoch_wait_removed=True,
             all10_consumed_address_proof_and_source_locked_RUP_AUP_unchanged=True,
             DMA_retirement_checks_unchanged=True,stage_names=["drain","pending","prepare","observe","epoch_wait","program","collect","retire"],
             epoch_counts_are_sensor_pipeline_IRQ_counts_not_sensor_timestamps=True)
