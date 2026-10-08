#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Add a read-only first live replacement observation; release policy unchanged."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1:raise RuntimeError("rear live observation source anchor drift")
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss);p=camss/"camss-vfe-e008k-rear-runner.inc";t=p.read_text()
 t=once(t,"\tbool dma_reclaimed;\n};","\tbool dma_reclaimed;\n};\n\n#include \"native-rear-live-observe.inc\"")
 t=once(t,"\tresult->both_frames_complete = true;","\tresult->both_frames_complete = true;\n\tnative_rear_live_replacement_observe(vfe, csid, pair, result, done_cursor);")
 p.write_text(t);(camss/"native-rear-live-observe.inc").write_bytes((HERE/"native-rear-live-observe.inc").read_bytes())
 return {"live_replacement_observation_only":True,"all_ten_WM_live_readback":True,"DMA_release_or_reuse_authority":False,"hardware_IRQ_ack_control_writes":0}
