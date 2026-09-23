#!/usr/bin/python3
"""Root-only finite preview from the existing RGB loopback, locally sealed.

One local PNG per opt-in visible-light camera, without raw IR, network,
image data in stdout/logs, or any committed/exported photo. Golden is untouched.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import stat
import time
from PIL import Image

CANDIDATE="e004nb"
BOOT_TOKEN="sp11_camera_e004nb_rgb_session=1"
MODES={"front":("/dev/video91",1920,1080),
       "rear":("/dev/video90",3840,2160)}
ROOT=Path("/var/lib/sp11-camera-e004nb")


def save_rgb_png(rgb:bytes, width:int, height:int, output:Path)->dict:
    """No optical image on stdout, and no overwrite or symlink traversal."""
    if (width,height) not in ((1920,1080),(3840,2160)) or len(rgb)!=width*height*3:
        raise ValueError("UNEXPECTED_RGB_PREVIEW_LAYOUT")
    fd=os.open(output,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        with os.fdopen(fd,"wb") as f:
            im=Image.frombytes("RGB",(width,height),rgb)
            im.save(f,format="PNG",compress_level=3)
            f.flush()
            os.fsync(f.fileno())
        mode=stat.S_IMODE(output.stat().st_mode)
        if mode!=0o600:raise RuntimeError("PRIVATE_IMAGE_MODE_MISMATCH")
        return {"format":"PNG","dimensions":[width,height],
                "private_local_path":str(output),
                "image_saved_locally_only":True,"mode_octal":"0600",
                "image_bytes_returned_or_logged":False}
    except BaseException:
        try:output.unlink()
        except FileNotFoundError:pass
        raise


def run(camera:str,stage:str="baseline")->dict:
    if stage not in ("baseline","gain"):
        raise RuntimeError("UNEXPECTED_PREVIEW_STAGE")
    if camera not in MODES or os.geteuid()!=0 or (
        BOOT_TOKEN not in Path("/proc/cmdline").read_text().split()):
        raise RuntimeError("EXACT_FRESH_ROOT_RGB_BOOT_REQUIRED")
    private=ROOT/"private-optical"
    if (not private.is_dir() or private.is_symlink() or
        stat.S_IMODE(private.stat().st_mode)!=0o700 or
        private.stat().st_uid!=0):
        raise RuntimeError("ROOT_PRIVATE_OPTICAL_FOLDER_NOT_SEALED")
    node,w,h=MODES[camera]
    import gi
    gi.require_version("Gst","1.0")
    from gi.repository import Gst
    Gst.init(None)
    pipeline=Gst.parse_launch(
        f"v4l2src device={node} io-mode=mmap num-buffers=8 "
        f"! video/x-raw,format=NV12,width={w},height={h},framerate=30/1 "
        f"! videoconvert ! video/x-raw,format=RGB,width={w},height={h} "
        "! appsink name=preview sync=false max-buffers=2 drop=false")
    sink=pipeline.get_by_name("preview")
    bus=pipeline.get_bus()
    seen=0
    chosen=None
    begin=time.monotonic()
    try:
        if pipeline.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("VISIBLE_RGB_PREVIEW_START_FAILED")
        while seen<8 and time.monotonic()-begin<18:
            sample=sink.emit("try-pull-sample",Gst.SECOND)
            if sample is None:
                error=bus.pop_filtered(Gst.MessageType.ERROR)
                if error is not None:raise RuntimeError("VISIBLE_RGB_PREVIEW_GST_ERROR")
                continue
            buf=sample.get_buffer()
            caps=sample.get_caps().get_structure(0)
            if (caps.get_string("format")!="RGB" or
                caps.get_value("width")!=w or caps.get_value("height")!=h or
                buf.get_size()!=w*h*3):
                raise RuntimeError("PREVIEW_RGB_STRIDE_OR_GEOMETRY_UNEXPECTED")
            if seen==6:
                ok,mapped=buf.map(Gst.MapFlags.READ)
                if not ok:raise RuntimeError("PREVIEW_GST_BUFFER_MAP_FAILED")
                try:chosen=bytes(mapped.data)
                finally:buf.unmap(mapped)
            seen+=1
        if seen!=8 or chosen is None:
            raise RuntimeError("PREVIEW_FRAME_COUNT_NOT_BOUNDED")
        msg=bus.timed_pop_filtered(3*Gst.SECOND,Gst.MessageType.EOS|Gst.MessageType.ERROR)
        if msg is None or msg.type!=Gst.MessageType.EOS:
            raise RuntimeError("PREVIEW_NO_CLEAN_EOS")
    finally:
        pipeline.set_state(Gst.State.NULL)
    path=private/(camera+"-"+stage+"-private.png")
    saved=save_rgb_png(chosen,w,h,path)
    return {"camera":camera,"stage":stage,"source":"real_named_rgb_loopback",
            "frames_read":seen,"frame_saved_from_index":6,
            "visible_light_only":True,"sensor_controls_written":False,
            "ir_streamed_or_illuminated":False,"os_system_sleep":False,
            **saved}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--camera",choices=MODES,required=True)
    p.add_argument("--stage",choices=("baseline","gain"),default="baseline")
    a=p.parse_args()
    try:
        print(json.dumps(run(a.camera,a.stage),sort_keys=True))
    except Exception as ex:
        print(json.dumps({"status":"FAIL","error":type(ex).__name__}))
        raise SystemExit(1)
