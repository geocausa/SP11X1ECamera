#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Validate one isolated parameter endpoint plus the complete retained data graph."""
import re,runpy
from pathlib import Path
base=runpy.run_path(str(Path(__file__).with_name("base-route-contract.py")))
def classify(text):
 blocks=re.findall(r"(?ms)^- entity .*?(?=^- entity |\Z)",text)
 selected=[b for b in blocks if re.match(r"- entity \d+: msm_vfe1_params ",b)]
 if len(selected)!=1:raise ValueError("MISSING_OR_DUPLICATE_PARAMS_ENTITY")
 block=selected[0]
 if not re.match(r"- entity \d+: msm_vfe1_params \(1 pad, 0 links?(?:, 0 routes)?\)\n",block):
  raise ValueError("PARAMS_PAD_LINK_COUNT_DRIFT")
 nodes=re.findall(r"device node name (/dev/video\d+)",block)
 if len(nodes)!=1 or len(re.findall(r"device node name "+re.escape(nodes[0])+r"\s*$",text,re.M))!=1:
  raise ValueError("PARAMS_DEVICE_DRIFT")
 if re.findall(r"(?m)^\s*pad(\d+): (SINK|SOURCE)\s*$",block)!=[("0","SOURCE")]:
  raise ValueError("PARAMS_PAD_DIRECTION_DRIFT")
 if "->" in block or "<-" in block:raise ValueError("PARAMS_HAS_IMAGE_LINK")
 return base["classify"](text.replace(block,"",1))
