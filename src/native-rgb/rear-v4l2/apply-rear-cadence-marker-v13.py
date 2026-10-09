#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
def apply(camss):
 p=Path(camss)/"native-rear-generation-hook.inc";s=p.read_text()
 old=r'dev_info(camss->dev, "NATIVE_REAR_GENERATION_ATTEMPT identity=53 consumed=1\n");'
 new=r'dev_info(camss->dev, "NATIVE_REAR_GENERATION_ATTEMPT identity=53 consumed=1 session=%u\n", native_rear_generation_sessions.attempted);'
 assert s.count(old)==1
 p.write_text(s.replace(old,new,1))
 return dict(explicit_kernel_session_marker=True,identity=53,strict_session_scope=True,
             old_log_ring_history_not_required=True,current_session_marker_still_required=True)
