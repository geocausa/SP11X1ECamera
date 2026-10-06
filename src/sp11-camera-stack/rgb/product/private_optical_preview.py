#!/usr/bin/python3
"""Root-only finite visual gate for the current SP11 RGB product path.

Captures one rendered RGB PNG from the already-running named loopback endpoint.
Optical pixels stay root-private on the SP11 and are never logged or committed.
"""
from __future__ import annotations
import argparse,json,os,stat,time
from pathlib import Path
from PIL import Image

BOOT_TOKEN="sp11_camera_rgb_product=1"
MODES={"front":("/dev/video91",1920,1080),"rear":("/dev/video90",3840,2160)}
ROOT=Path("/var/lib/sp11-camera-rgb")


def save_rgb_png(rgb:bytes,width:int,height:int,output:Path)->dict:
    if (width,height) not in ((1920,1080),(3840,2160)) or len(rgb)!=width*height*3:
        raise ValueError("UNEXPECTED_RGB_PREVIEW_LAYOUT")
    fd=os.open(output,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        with os.fdopen(fd,"wb") as f:
            Image.frombytes("RGB",(width,height),rgb).save(f,format="PNG",compress_level=3)
            f.flush();os.fsync(f.fileno())
        s=output.stat()
        if s.st_uid!=0 or stat.S_IMODE(s.st_mode)!=0o600:
            raise RuntimeError("PRIVATE_IMAGE_OWNERSHIP_OR_MODE_MISMATCH")
        return {"format":"PNG","dimensions":[width,height],"private_local_path":str(output),
                "image_saved_locally_only":True,"mode_octal":"0600","image_bytes_returned_or_logged":False}
    except BaseException:
        try: output.unlink()
        except FileNotFoundError: pass
        raise


def run(camera:str)->dict:
    if camera not in MODES or os.geteuid()!=0 or BOOT_TOKEN not in Path("/proc/cmdline").read_text().split():
        raise RuntimeError("EXACT_RGB_PRODUCT_BOOT_REQUIRED")
    private=ROOT/"private-optical"
    if (not private.is_dir() or private.is_symlink() or private.stat().st_uid!=0 or
        stat.S_IMODE(private.stat().st_mode)!=0o700):
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
    sink=pipeline.get_by_name("preview");bus=pipeline.get_bus();seen=0;chosen=None;begin=time.monotonic()
    try:
        if pipeline.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("VISIBLE_RGB_PREVIEW_START_FAILED")
        while seen<8 and time.monotonic()-begin<18:
            sample=sink.emit("try-pull-sample",Gst.SECOND)
            if sample is None:
                if bus.pop_filtered(Gst.MessageType.ERROR) is not None:
                    raise RuntimeError("VISIBLE_RGB_PREVIEW_GST_ERROR")
                continue
            buf=sample.get_buffer();caps=sample.get_caps().get_structure(0)
            if (caps.get_string("format")!="RGB" or caps.get_value("width")!=w or
                caps.get_value("height")!=h or buf.get_size()!=w*h*3):
                raise RuntimeError("PREVIEW_RGB_STRIDE_OR_GEOMETRY_UNEXPECTED")
            if seen==6:
                ok,mapped=buf.map(Gst.MapFlags.READ)
                if not ok: raise RuntimeError("PREVIEW_GST_BUFFER_MAP_FAILED")
                try: chosen=bytes(mapped.data)
                finally: buf.unmap(mapped)
            seen+=1
        if seen!=8 or chosen is None: raise RuntimeError("PREVIEW_FRAME_COUNT_NOT_BOUNDED")
        msg=bus.timed_pop_filtered(3*Gst.SECOND,Gst.MessageType.EOS|Gst.MessageType.ERROR)
        if msg is None or msg.type!=Gst.MessageType.EOS: raise RuntimeError("PREVIEW_NO_CLEAN_EOS")
    finally:
        pipeline.set_state(Gst.State.NULL)
    path=private/(camera+"-current-product.png")
    saved=save_rgb_png(chosen,w,h,path)
    return {"status":"PASS_CURRENT_PRODUCT_OPTICAL_RENDER_CAPTURED","camera":camera,
            "source":"real_named_rgb_loopback","frames_read":seen,"frame_saved_from_index":6,
            "visible_light_only":True,"sensor_controls_written":False,"ir_streamed_or_illuminated":False,
            **saved}


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--camera",choices=MODES,required=True);a=p.parse_args()
    try: print(json.dumps(run(a.camera),sort_keys=True))
    except Exception as ex:
        print(json.dumps({"status":"FAIL","error":type(ex).__name__}),flush=True);raise SystemExit(1)
