#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Replace finite rear scalar event history with a consumed SPSC event queue."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1:raise RuntimeError("rear event queue source anchor drift")
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss)
 p=camss/"camss-csid-680.c";t=p.read_text()
 t=once(t,'#include "camss-csid-e008i-rear-observer.inc"','#include "native-rear-event-queue.inc"');p.write_text(t)
 (camss/"native-rear-event-queue.inc").write_bytes((HERE/"native-rear-event-queue.inc").read_bytes())
 p=camss/"camss-csid.h";t=p.read_text()
 t=once(t,"\tu32 e008i_rear_done_count;","\tu32 e008i_rear_done_count;\n\tu32 native_rear_done_consumed;");p.write_text(t)
 p=camss/"camss-e008i-rear-observer.h";t=p.read_text()
 t=once(t,"#endif /* CAMSS_E008I_REAR_OBSERVER_H */",
        "int csid680_e008i_rear_retire_event(struct csid_device *csid, u32 index, u64 owner);\n\n#endif /* CAMSS_E008I_REAR_OBSERVER_H */");p.write_text(t)
 p=camss/"camss-vfe-e008k-rear-runner.inc";t=p.read_text()
 t=once(t,"\t\t\t(*cursor)++;",
        "\t\t\tret = csid680_e008i_rear_retire_event(csid, *cursor, owner_epoch);\n\t\t\tif (ret)\n\t\t\t\treturn ret;\n\t\t\t(*cursor)++;");p.write_text(t)
 return {"scalar_event_storage_reused_only_after_checked_consumption":True,
         "SPSC_release_acquire_publication":True,"history_capacity":16,
         "overflow_and_counter_wrap_fail_closed":True,
         "live_image_mapping_retirement_authority":False}
