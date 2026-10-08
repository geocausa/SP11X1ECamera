#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Initialize buffer waitqueue before publication of any video callbacks."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
def apply(camss):
 spec=importlib.util.spec_from_file_location("rear_queue_base",HERE/"apply-rear-queue.py")
 base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
 result=base.apply(camss)
 p=Path(camss)/"camss-video.c";t=p.read_text()
 anchor="\tinit_waitqueue_head(&video->x1e_pix_iq_wait);"
 assert t.count(anchor)==1
 t=t.replace(anchor,anchor+"\n\tinit_waitqueue_head(&video->x1e_pix_buf_wait);",1)
 p.write_text(t);result["buffer_waitqueue_initialized_at_video_registration"]=True
 return result
