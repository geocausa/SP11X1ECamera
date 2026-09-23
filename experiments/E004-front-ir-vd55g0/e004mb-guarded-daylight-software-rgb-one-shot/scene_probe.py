#!/usr/bin/python3
"""Finite unprivileged RGB daylight scene probe: scalar statistics ONLY.

Runs solely in a fresh guarded E004mb camera candidate and holds no
physical sensor/media FD: the independently managed publisher owns CAMSS.
No photos, pixels, tiles, pixel hashes, scene classification or images
are written to disk. Does not modify exposure, gain, IR or graph.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import time
import numpy as np

DEVICES={"front":("/dev/video91",1920,1080),
         "rear":("/dev/video90",3840,2160)}
BOOT_TOKEN="sp11_camera_e004mb_rgb_session=1"

def stats_from_y(y:np.ndarray)->dict[str,float]:
    """Use sparse luma samples. Return scalar aggregate, never a tile grid."""
    if y.ndim!=2 or min(y.shape)<48 or y.dtype!=np.uint8:
        raise ValueError("INVALID_LUMA_SAMPLE")
    ys=y[::16,::16].astype(np.float32,copy=True)
    p=np.percentile(ys,(1,10,50,90,95,99))
    row_edges=np.abs(np.diff(ys,axis=0))
    col_edges=np.abs(np.diff(ys,axis=1))
    tiles=[]
    for part in np.array_split(ys,12,axis=0):
        for cell in np.array_split(part,16,axis=1):
            tiles.append(float(cell.mean()))
    a=np.array(tiles,dtype=np.float32)
    return {
        "mean_y":round(float(ys.mean()),3),
        "p1_y":round(float(p[0]),3),
        "p10_y":round(float(p[1]),3),
        "median_y":round(float(p[2]),3),
        "p90_y":round(float(p[3]),3),
        "p95_y":round(float(p[4]),3),
        "p99_y":round(float(p[5]),3),
        "fraction_y_above_32":round(float(np.mean(ys>32)),5),
        "fraction_y_above_64":round(float(np.mean(ys>64)),5),
        "fraction_y_below_20":round(float(np.mean(ys<20)),5),
        "spatial_tile_means_std_y":round(float(a.std()),3),
        "spatial_tile_means_span_y":round(float(a.max()-a.min()),3),
        "adjacent_sparse_sample_diff_y":round(
            float((row_edges.mean()+col_edges.mean())/2),3),
    }

def run(camera:str,frames:int)->dict:
    if camera not in DEVICES or not isinstance(frames,int) or not 1<=frames<=120:
        raise ValueError("CAMERA_OR_FRAME_BOUND_INVALID")
    if os.geteuid()!=1000 or BOOT_TOKEN not in Path("/proc/cmdline").read_text().split():
        raise RuntimeError("EXACT_FRESH_GUARDED_UID1000_CAMERA_BOOT_REQUIRED")
    # Import GI only in the live entrypoint. Unit-testing stats is camera-free.
    import gi
    gi.require_version("Gst","1.0")
    from gi.repository import Gst
    dev,w,h=DEVICES[camera]
    Gst.init(None)
    pipe=Gst.parse_launch(
        f"v4l2src device={dev} io-mode=mmap num-buffers={frames} "
        f"! video/x-raw,format=NV12,width={w},height={h},framerate=30/1 "
        f"! videoconvert ! video/x-raw,format=I420,width={w},height={h} "
        "! appsink name=framesink sync=false max-buffers=3 drop=false"
    )
    sink=pipe.get_by_name("framesink")
    bus=pipe.get_bus()
    snapshots=[]
    seen=0
    start=time.monotonic()
    try:
        if pipe.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("DEVICE_PLAYING_FAILED")
        while seen<frames and time.monotonic()-start<30:
            sample=sink.emit("try-pull-sample",Gst.SECOND)
            if sample is None:
                err=bus.pop_filtered(Gst.MessageType.ERROR)
                if err is not None:
                    detail,_=err.parse_error()
                    raise RuntimeError("CAPTURE_ERROR:"+str(detail)[:200])
                if sink.get_property("eos"):
                    break
                continue
            b=sample.get_buffer()
            caps=sample.get_caps().get_structure(0)
            if b.get_size()!=w*h*3//2 or caps.get_string("format")!="I420":
                raise RuntimeError("BAD_REAL_RGB_FRAME_LAYOUT")
            if seen%15==0 or seen==frames-1:
                ok,mapping=b.map(Gst.MapFlags.READ)
                if not ok:raise RuntimeError("FRAME_MAPPING_FAILED")
                try:
                    y=np.frombuffer(mapping.data,dtype=np.uint8,
                                    count=w*h).reshape(h,w)
                    s=stats_from_y(y)
                    s["frame_index"]=seen
                    snapshots.append(s)
                finally:
                    b.unmap(mapping)
            seen+=1
        if seen!=frames:
            raise RuntimeError("INCOMPLETE_REAL_SCENE_PROBE_FRAMES")
        extra=sink.emit("try-pull-sample",Gst.SECOND)
        if extra is not None:
            raise RuntimeError("UNEXPECTED_EXTRA_FRAME")
        msg=bus.timed_pop_filtered(2*Gst.SECOND,
                                  Gst.MessageType.EOS|Gst.MessageType.ERROR)
        if msg is None or msg.type!=Gst.MessageType.EOS:
            raise RuntimeError("NO_NORMAL_V4L2_APP_EOS")
        maximum=max(s["p99_y"] for s in snapshots)
        texture=max(s["spatial_tile_means_std_y"] for s in snapshots)
        highlighted=max(s["fraction_y_above_32"] for s in snapshots)
        return {"status":"PASS","camera":camera,"frames":seen,
                "effective_uid":os.geteuid(),
                "format":f"I420_{w}x{h}",
                "sparse_snapshots":snapshots,
                "max_sampled_p99_y":maximum,
                "max_sampled_tile_std_y":texture,
                "max_sampled_fraction_above32":highlighted,
                "statistical_scene_contrast_present":
                    bool(maximum>=40 and texture>=4 and highlighted>=.02),
                "note":"Scalar sparse-luma contrast indicators only; not proof of recognizable content, colour accuracy or Windows parity.",
                "pixel_files_saved":False,
                "pixel_hashes_or_tile_grid_exported":False,
                "camera_route_or_controls_changed":False,
                "os_system_sleep_used":False,
                "ir_illumination_enabled":False}
    finally:
        pipe.set_state(Gst.State.NULL)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--camera",choices=DEVICES,required=True)
    parser.add_argument("--frames",type=int,default=90)
    a=parser.parse_args()
    try:
        out=run(a.camera,a.frames)
        print(json.dumps(out,sort_keys=True),flush=True)
    except Exception as error:
        print(json.dumps({"status":"FAIL","error":str(error)[:280]}),flush=True)
        raise SystemExit(1)
