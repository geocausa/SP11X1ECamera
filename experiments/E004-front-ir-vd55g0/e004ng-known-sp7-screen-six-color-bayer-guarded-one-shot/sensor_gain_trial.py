#!/usr/bin/python3
"""Candidate-only bounded standard V4L2 RGB sensor controls response.

Only the rear analogue gain changes versus E004mh (256->512) at the
identical supported trial exposure3200/digital gain2048. This is a new
independent single-use boot and cannot be a same-scene E004mh control.
No direct register/I2C writes, no IR/illumination/sleep. Hard refuse
unexpected baseline, missing exclusive root owner/boot token or sensor
node. Reverts precise pre-trial RGB controls before route neutralization.
On ANY uncertain write or restore, exception causes the enclosing
one-shot to reboot into protected Golden, not speculative retry.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import subprocess
import time
from typing import Callable

BASELINE={
 "front":{"exposure":3546,"analogue_gain":0,"digital_gain":256},
 "rear":{"exposure":1600,"analogue_gain":128,"digital_gain":1024},
}
TARGET={
 "front":{"exposure":3546,"analogue_gain":512,"digital_gain":512},
 "rear":{"exposure":3200,"analogue_gain":512,"digital_gain":2048},
}
CMDS=("exposure","analogue_gain","digital_gain")


def _run(argv:tuple[str,...],*,timeout:float=4)->str:
    r=subprocess.run(argv,text=True,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,check=True,timeout=timeout,close_fds=True)
    return r.stdout


def sensor_node(root:Path,camera:str)->str:
    if camera not in BASELINE:raise RuntimeError("IR_OR_UNKNOWN_SENSOR_REFUSED")
    if os.geteuid()!=0 or "sp11_camera_e004ng_rgb_session=1" not in Path("/proc/cmdline").read_text().split():
        raise RuntimeError("ROOT_AND_FRESH_UNIQUE_CAMERA_BOOT_REQUIRED")
    # Caller has already acquired the same root-private exclusive
    # RGBSession owner, verified the actual full native camera graph
    # and the active selected sensor before invoking this function.
    data=json.loads((root/"output/UNIFIED.json").read_text())
    name=data["front_sensor_device" if camera=="front" else "rear_sensor_device"]
    if not re.fullmatch(r"/dev/v4l-subdev[0-9]+",name):
        raise RuntimeError("UNEXPECTED_SENSOR_DEVICE")
    if not Path(name).is_char_device():
        raise RuntimeError("SENSOR_DEVICE_NOT_CHARACTER")
    return name


def read(node:str)->dict[str,int]:
    out={}
    for control in CMDS:
        line=_run(("v4l2-ctl","-d",node,"--get-ctrl",control)).strip()
        match=re.fullmatch(rf"{re.escape(control)}:\s*([0-9]+)",line)
        if not match:raise RuntimeError("SENSOR_V4L2_CONTROL_READBACK_NOT_EXACT")
        out[control]=int(match[1])
    return out


def query_supported_bounds(node:str,camera:str)->dict[str,dict[str,int]]:
    """Read current V4L2-advertised min/max/step; refuse guessed ranges."""
    if camera not in TARGET:raise RuntimeError("UNKNOWN_CAMERA_CONTROL_BOUNDS")
    text=_run(("v4l2-ctl","-d",node,"--list-ctrls"),timeout=5)
    bounds={}
    for line in text.splitlines():
        match=re.match(r"\s*(exposure|analogue_gain|digital_gain)\s+0x[0-9a-f]+\s+\(int\)\s*:",line)
        if not match:
            continue
        name=match[1]
        if name in bounds:raise RuntimeError("DUPLICATE_V4L2_SENSOR_CONTROL_RANGE")
        values={}
        for field in ("min","max","step"):
            m=re.search(rf"\b{field}=(-?[0-9]+)",line)
            if not m:raise RuntimeError("INCOMPLETE_NATIVE_V4L2_SENSOR_CONTROL_RANGE")
            values[field]=int(m[1])
        bounds[name]=values
    if set(bounds)!=set(CMDS):
        raise RuntimeError("EXPECTED_RGB_NATIVE_V4L2_CONTROL_RANGES_NOT_FOUND")
    for name,limits in bounds.items():
        value=TARGET[camera][name]
        if (limits["step"]<=0 or
            not limits["min"]<=value<=limits["max"] or
            (value-limits["min"])%limits["step"]):
            raise RuntimeError("TARGET_GAIN_EXPOSURE_OUTSIDE_ADVERTISED_SENSOR_RANGE")
    return bounds


def set_supported(node:str,values:dict[str,int],camera:str)->None:
    # Only exact, source-reviewed safe visible-light RGB gain/exposure
    # tuples within the pinned IMX681/OV13858 V4L2 driver ranges.
    if camera not in TARGET or values not in (TARGET[camera],BASELINE[camera]):
        raise RuntimeError("UNAPPROVED_SENSOR_CONTROL_TUPLE")
    args=tuple(f"{n}={values[n]}" for n in CMDS)
    _run(("v4l2-ctl","-d",node,"--set-ctrl",",".join(args)),timeout=6)


def perform(root:Path,camera:str,baseline_app:dict,
            probe:Callable[[],dict])->dict:
    if camera not in TARGET:raise RuntimeError("CAMERA_NOT_RGB")
    node=sensor_node(root,camera)
    initial=read(node)
    if initial!=BASELINE[camera]:
        raise RuntimeError("RGB_SENSOR_BASELINE_NOT_EXACT_REJECT_CHANGE")
    if (baseline_app.get("status")!="PASS" or
        baseline_app.get("frames")!=90 or baseline_app.get("effective_uid")!=1000):
        raise RuntimeError("BASELINE_ORDINARY_APP_NOT_VALID")
    # Independently confirm this device advertises every native
    # control's bounds before the first RGB sensor write.
    advertised_bounds=query_supported_bounds(node,camera)
    # No command issued yet if any preceding admission failed.
    set_supported(node,TARGET[camera],camera)
    modified=read(node)
    if modified!=TARGET[camera]:
        raise RuntimeError("RGB_SENSOR_CONTROL_CHANGE_READBACK_NOT_CONFIRMED")
    changed_ms=round(time.monotonic()*1000,3)
    time.sleep(0.5)
    settled_ms=round(time.monotonic()*1000,3)
    changed_app=probe()
    if (changed_app.get("status")!="PASS" or
        changed_app.get("frames")!=90 or
        changed_app.get("effective_uid")!=1000 or
        changed_app.get("pixel_files_saved") is not False):
        raise RuntimeError("GAIN_CHANGED_ORDINARY_APP_INVALID")
    restored_begin_ms=round(time.monotonic()*1000,3)
    set_supported(node,BASELINE[camera],camera)
    restored=read(node)
    if restored!=initial:
        raise RuntimeError("RGB_SENSOR_EXACT_BASELINE_RESTORE_UNCONFIRMED")
    restored_ms=round(time.monotonic()*1000,3)
    return dict(camera=camera,advertised_sensor_control_bounds=advertised_bounds,
                baseline_controls=initial,
      modified_controls=modified,restored_controls=restored,
      first_changed_ms=changed_ms,settled_ms=settled_ms,
      restore_started_ms=restored_begin_ms,restored_ms=restored_ms,
      baseline_app=dict(p99_y=baseline_app["max_sampled_p99_y"],
                        tile_std_y=baseline_app["max_sampled_tile_std_y"]),
      gain_changed_app=dict(p99_y=changed_app["max_sampled_p99_y"],
                            tile_std_y=changed_app["max_sampled_tile_std_y"]),
      effect_on_app_p99_y=round(changed_app["max_sampled_p99_y"]-
                              baseline_app["max_sampled_p99_y"],3),
      correct_RGB_subdevice=True,
      driver_supported_v4l2_controls_only=True,
      raw_registers_directly_written=False,
      illumination_or_ir_enabled=False,
      os_system_sleep_used=False,
      pixel_files_saved=False)
