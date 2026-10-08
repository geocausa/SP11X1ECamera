#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Retire only the old public FULL attachment after verified live replacement."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1:raise RuntimeError("live retirement source anchor drift")
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss)
 p=camss/"camss-vfe-e008d-rear-dma.inc";t=p.read_text()
 t=once(t,"\tstruct native_rear_video_lease public_full;",
 """\tstruct native_rear_video_lease public_full;
 u64 retired_owner_epoch, retired_request_generation;
 bool public_full_retired, retired_aux_stop_proven;""")
 t=once(t,"\tunsigned int i;\n\n\t/* Retained public mappings",
 """\tunsigned int i;

 if (set->public_full_retired && !set->retired_aux_stop_proven)
  return; /* Old auxiliary allocations still belong to the live ISP. */

\t/* Retained public mappings""")
 t=once(t,"if (!vfe || !set || !out || !set->allocated)",
        "if (!vfe || !set || !out || !set->allocated || set->public_full_retired)")
 p.write_text(t)
 p=camss/"camss-vfe-e008k-rear-runner.inc";t=p.read_text()
 t=once(t,"\tbool dma_reclaimed;","\tbool dma_reclaimed;\n bool live_full_retired;")
 t=once(t,'#include "native-rear-live-observe.inc"',
        '#include "native-rear-live-observe.inc"\n#include "native-rear-live-retire.inc"')
 anchor="\tnative_rear_live_replacement_observe(vfe, csid, pair, result, done_cursor);"
 t=once(t,anchor,anchor+"\n if (req->public_video[0])\n  native_rear_live_retire_full_observe(vfe, csid, pair, result, done_cursor);")
 p.write_text(t)
 p=camss/"native-rear-reclaim.inc";t=p.read_text()
 anchor="    for (s = 0; s < E008H_REAR_SLOTS; s++) {\n        const struct e008d_rear_dma_set *set"
 t=once(t,anchor,
 """    if (result->live_full_retired != pair->dma[0].public_full_retired ||
        pair->dma[1].public_full_retired)
        return -EPROTO;

"""+anchor)
 t=once(t,"!set->full.in_flight || !native_rear_dma_full_valid(set) ||",
 """(!set->public_full_retired &&
             (!set->full.in_flight || !native_rear_dma_full_valid(set))) ||
            (set->public_full_retired &&
             (s != 0 || !native_rear_live_full_retired_valid(set,
                 &pair->frame[s], owner_epoch))) ||""")
 anchor="        pair->dma[s].full.in_flight = false;"
 t=once(t,anchor,
 """        if (pair->dma[s].public_full_retired)
            pair->dma[s].retired_aux_stop_proven = true;
"""+anchor)
 p.write_text(t)
 (camss/"native-rear-live-retire.inc").write_bytes((HERE/"native-rear-live-retire.inc").read_bytes())
 return {"live_old_public_FULL_retirement":True,"requires_actual_live_replacement_observation":True,
         "auxiliary_DMA_retained_until_four_stops":True,"fabricated_stop_facts":False,
         "VB2_completion_or_requeue":False,"continuous_capture":False}
