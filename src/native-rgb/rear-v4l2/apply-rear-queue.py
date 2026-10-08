#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Integrate persistent rear output queue after guarded startup retirement."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 assert t.count(a)==1,("queue source anchor drift",a)
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss)
 (camss/"native-rear-queue.inc").write_bytes((HERE/"native-rear-queue.inc").read_bytes())
 p=camss/"camss-video.h";t=p.read_text();t=once(t,"\tint x1e_pix_worker_ret;","\tint x1e_pix_worker_ret;\n\tu32 native_rear_completed, native_rear_live_completed;\n\tstruct camss_buffer *native_rear_inflight[2];");p.write_text(t)
 p=camss/"camss-vfe-e008k-rear-runner.inc";t=p.read_text()
 t=once(t," bool live_full_retired, live_aux_retired, live_commands_retired;"," bool live_full_retired, live_aux_retired, live_commands_retired;\n u32 queue_handoffs;\n bool queue_starved;")
 anchor="static int\ne008k_rear_pair_stop_release("
 t=once(t,anchor,'#include "native-rear-queue.inc"\n\n'+anchor)
 anchor="\n\tret = e008k_rear_pair_stop_release(\n\t\tcamss, vfe, csid, csiphy, req->sensor, pair, video_entity,"
 t=once(t,anchor,"\n if (req->public_video[0]) {\n  ret = native_rear_queue_run(vfe, csid, pair, req, result, &done_cursor);\n  if (ret)\n   goto out_pin;\n }\n"+anchor)
 p.write_text(t)
 # Preparation belongs to original BUS setup, not to rotating allocations.
 p=camss/"native-rear-reclaim.inc";t=p.read_text()
 t=once(t,"        !pair->dma[0].prepared_disabled ||","        (!result->queue_handoffs && !pair->dma[0].prepared_disabled) ||\n        (result->queue_handoffs && (!pair->dma[0].public_full_retired ||\n                                  pair->dma[0].prepared_disabled)) ||")
 p.write_text(t)
 # New worker transfers all owned pointers through its video queue state.
 p=camss/"native-rear-public-worker.inc";t=p.read_text()
 t=once(t," struct camss_buffer *buffer[2] = {};"," struct camss_buffer **buffer = video->native_rear_inflight;")
 t=once(t," spin_lock_irqsave(&vfe->output_lock, flags);"," video->native_rear_completed = video->native_rear_live_completed = 0;\n memset(video->native_rear_inflight, 0, sizeof(video->native_rear_inflight));\n spin_lock_irqsave(&vfe->output_lock, flags);")
 a=t.index(" for (s = 0; s < 2; s++) {");b=t.index(" WRITE_ONCE(video->x1e_pix_runner_stopped",a)
 t=t[:a]+""" for (s = 0; s < 2; s++) {
  bool success = !ret && !READ_ONCE(video->x1e_pix_stop_requested);
  native_rear_public_complete(video, s, false, success);
 }
"""+t[b:]
 t=t.replace("ret, ret ? 0U : 2U);","ret, video->native_rear_completed);")
 t=once(t," WRITE_ONCE(video->x1e_pix_stop_requested, true);"," WRITE_ONCE(video->x1e_pix_stop_requested, true);\n wake_up_all(&video->x1e_pix_buf_wait);")
 p.write_text(t)
 # camss.c cannot use VFE translation-unit static helper.
 hook=camss/"native-rear-generation-hook.inc";t=hook.read_text()
 helper= (HERE/"native-rear-queue.inc").read_text()
 start=helper.index("static void native_rear_queue_complete(");end=helper.index("\nstatic int\nnative_rear_queue_drain",start)
 completion=helper[start:end].replace("native_rear_queue_complete","native_rear_public_complete")
 t=once(t,'#include "native-rear-public-worker.inc"',completion+'\n#include "native-rear-public-worker.inc"');hook.write_text(t)
 return dict(persistent_rear_queue=True,early_VB2_after_old_FULL_and8aux_retired=True,exact_replacement_consumed_addresses_required=True,startup_command_resubmission=False,adaptive_IPA=False)
