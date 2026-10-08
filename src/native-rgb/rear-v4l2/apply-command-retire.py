#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Add guarded live command retirement; keep exact retired tombstone to stop."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1:raise RuntimeError("command retirement source anchor drift")
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss)
 for n in ("native-rear-command-retired.inc","native-rear-command-retire.inc"):
  (camss/n).write_bytes((HERE/n).read_bytes())
 p=camss/"camss-vfe-e008l-rear-command-dma.inc";t=p.read_text()
 t=once(t," bool receipt_faulted;",""" bool receipt_faulted;
 bool live_retired;
 u64 retired_owner;
 u32 retired_BL_count;
 struct native_rear_bl_receipt retired_last;""")
 t=once(t,"static int\ne008l_rear_packet_sizing(",
        '#include "native-rear-command-retired.inc"\n\nstatic int\ne008l_rear_packet_sizing(')
 anchor="\tif (set->hardware_exposed && !rtcdm_stopped)\n\t\treturn -EBUSY;"
 t=once(t,anchor,anchor+"""
 if (set->live_retired &&
     !native_rear_live_commands_retired_valid(set, set->retired_owner))
  return -EPROTO;""")
 p.write_text(t)
 p=camss/"camss-vfe-e008k-rear-runner.inc";t=p.read_text()
 t=once(t," bool live_full_retired, live_aux_retired;",
        " bool live_full_retired, live_aux_retired, live_commands_retired;")
 t=once(t,'#include "native-rear-command-observe.inc"',
        '#include "native-rear-command-observe.inc"\n#include "native-rear-command-retire.inc"')
 anchor="\tret = e008k_rear_pipeline_pm_get(video_entity);"
 t=once(t,anchor,""" if (req->public_video[0]) {
  ret = native_rear_command_allocations_check(req, pair, owner_epoch);
  if (ret)
   goto out_release_clean_pair;
 }

"""+anchor)
 anchor="\tnative_rear_live_replacement_observe(vfe, csid, pair, result, done_cursor);"
 t=once(t,anchor,""" if (req->public_video[0]) {
  ret = native_rear_command_allocations_check(req, pair, owner_epoch);
  if (ret)
   goto out_pin;
 }
"""+anchor)
 anchor=" native_rear_command_receipts_observe(vfe, csid, pair, req, result, done_cursor);"
 t=once(t,anchor,anchor+"""
 if (req->public_video[0])
  native_rear_live_retire_commands_observe(vfe, csid, pair, req, result, done_cursor);""")
 p.write_text(t)
 p=camss/"camss-vfe-e008n-rear-single-use.inc";t=p.read_text()
 anchor="\tret = e008l_rear_command_release(vfe, commands, true);"
 t=once(t,anchor,""" if (result->transaction.live_commands_retired != commands->live_retired ||
     (commands->live_retired &&
      !native_rear_live_commands_retired_valid(commands,
                                              result->transaction.owner_epoch))) {
  ret = -EPROTO;
  goto out_pin;
 }
"""+anchor)
 p.write_text(t)
 return {"live_completed_command_arena_retirement":True,
         "all22_exact_receipts_and_current_owner_required":True,
         "all12_command_CPU_allocations_cross_type_disjoint":True,
         "all_command_slabs_disjoint_from20_output_DMA_spans":True,
         "pre_hardware_and_pre_output_retire_admission":True,
         "retired_tombstone_checked_before_post_stop_cleanup":True,
         "command_rewrite_address_reuse_or_VB2_delivery":False,
         "continuous_capture":False}
