#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Declared reversible live readback overlay; no new control/register writes."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
def transforms():
 return [
 ('#include "native-rear-sensor-controls-v2.inc"\n\n',''), # handled separately by existing builder, not part of overlay
 ]
def overlay():
 return [
 ('#include <linux/module.h>','#include <linux/module.h>\n#include <linux/ktime.h>'),
 ('\tstruct v4l2_ctrl *test_pattern;\n','\tstruct v4l2_ctrl *test_pattern;\n\tbool native_control_streaming;\n'),
 ('static int ov13858_set_ctrl(struct v4l2_ctrl *ctrl)','#include "native-rear-live-control-readback.inc"\n\nstatic int ov13858_set_ctrl(struct v4l2_ctrl *ctrl)'),
 ('\tpm_runtime_put(ov13858->dev);\n\n\treturn ret;\n}\n\nstatic const struct v4l2_ctrl_ops',
  '\tif (!ret && ov13858->native_control_streaming &&\n\t    (ctrl->id == V4L2_CID_EXPOSURE || ctrl->id == V4L2_CID_ANALOGUE_GAIN))\n\t\tret = native_rear_live_control_readback(ov13858, ctrl);\n\n\tpm_runtime_put(ov13858->dev);\n\n\treturn ret;\n}\n\nstatic const struct v4l2_ctrl_ops'),
 ('\t\tret = ov13858_start_streaming(ov13858);\n\t\tif (ret)\n\t\t\tgoto err_rpm_put;\n\t} else {\n\t\tov13858_stop_streaming(ov13858);',
  '\t\tret = ov13858_start_streaming(ov13858);\n\t\tif (ret)\n\t\t\tgoto err_rpm_put;\n\t\tov13858->native_control_streaming = true;\n\t} else {\n\t\tov13858->native_control_streaming = false;\n\t\tov13858_stop_streaming(ov13858);')
 ]
def apply_sensor(p):
 t=p.read_text()
 for old,new in overlay():
  assert t.count(old)==1,(p.name,old);t=t.replace(old,new,1)
 p.write_text(t)
 (p.parent/"native-rear-live-control-readback.inc").write_bytes((HERE/"native-rear-live-control-readback.inc").read_bytes())
def undo_sensor(t):
 for old,new in reversed(overlay()):
  assert t.count(new)==1,new;t=t.replace(new,old,1)
 return t
