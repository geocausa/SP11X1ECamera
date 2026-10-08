#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Add explicit old auxiliary retirement, retaining ledgers/commands until stop."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1:raise RuntimeError("auxiliary retirement source anchor drift")
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss)
 p=camss/"camss-vfe-e008d-rear-dma.inc";t=p.read_text()
 t=once(t,"bool public_full_retired, retired_aux_stop_proven;",
        "bool public_full_retired, retired_aux_stop_proven, auxiliary_live_retired;")
 p.write_text(t)
 p=camss/"camss-vfe-e008k-rear-runner.inc";t=p.read_text()
 t=once(t,"bool live_full_retired;","bool live_full_retired, live_aux_retired;")
 t=once(t,'#include "native-rear-live-retire.inc"',
        '#include "native-rear-live-retire.inc"\n#include "native-rear-live-aux-retire.inc"')
 anchor="  native_rear_live_retire_full_observe(vfe, csid, pair, result, done_cursor);"
 t=once(t,anchor,anchor+"\n if (req->public_video[0])\n  native_rear_live_retire_aux_observe(vfe, csid, pair, result, done_cursor);")
 p.write_text(t)
 p=camss/"native-rear-reclaim.inc";t=p.read_text()
 anchor="    for (s = 0; s < E008H_REAR_SLOTS; s++) {\n        const struct e008d_rear_dma_set *set"
 t=once(t,anchor,
 """    if (result->live_aux_retired != pair->dma[0].auxiliary_live_retired ||
        pair->dma[1].auxiliary_live_retired ||
        (result->live_aux_retired &&
         !native_rear_live_aux_retired_valid(&pair->dma[0], &pair->frame[0],
                                             owner_epoch)))
        return -EPROTO;

"""+anchor)
 t=once(t,"        for (i = 0; i < E008D_REAR_AUX_COUNT; i++) {",
 """        if (set->auxiliary_live_retired)
            continue; /* Exact zero allocations already checked above. */
        for (i = 0; i < E008D_REAR_AUX_COUNT; i++) {""")
 p.write_text(t)
 (camss/"native-rear-live-aux-retire.inc").write_bytes((HERE/"native-rear-live-aux-retire.inc").read_bytes())
 return {"live_old_auxiliary_output_retirement":True,
         "exact_completed_allocation_and_live_replacement_required":True,
         "old_ledger_and_command_arenas_retained_until_stop":True,
         "replacement_DMA_retained":True,"fabricated_stop_facts":False,
         "VB2_completion_or_requeue":False,"continuous_capture":False}
