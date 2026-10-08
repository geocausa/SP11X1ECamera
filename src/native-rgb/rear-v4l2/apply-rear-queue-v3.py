#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Integrate source-locked output RUP/AUP after address readbacks."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
def apply(camss):
 spec=importlib.util.spec_from_file_location("rear_queue_base",HERE/"apply-rear-queue-v2.py")
 base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
 result=base.apply(camss);camss=Path(camss)
 (camss/"native-rear-queue.inc").write_bytes((HERE/"native-rear-queue-rup.inc").read_bytes())
 (camss/"native-rear-output-update.inc").write_bytes((HERE/"native-rear-output-update.inc").read_bytes())
 p=camss/"camss-csid-680.c";t=p.read_text();anchor='#include "native-rear-csid-config.inc"'
 assert t.count(anchor)==1
 p.write_text(t.replace(anchor,anchor+'\n#include "native-rear-output-update.inc"',1))
 p=camss/"camss-e008k-rear-bridge.h";t=p.read_text();anchor="int csid680_native_rear_configure(struct csid_device *csid);"
 assert t.count(anchor)==1
 p.write_text(t.replace(anchor,anchor+"\nint csid680_native_rear_output_update(struct csid_device *, u64);",1))
 p=camss/"camss-vfe-e008k-rear-runner.inc";t=p.read_text();anchor=" u32 queue_handoffs;"
 assert t.count(anchor)==1
 p.write_text(t.replace(anchor," u32 queue_handoffs, queue_updates;",1))
 result["source_locked_RUP_AUP_after_all10_address_readbacks"]=True
 result["RUP_AUP_value"]=0x01f501f5
 return result
