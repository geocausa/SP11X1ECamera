#!/usr/bin/python3
"""Camera-free, synthetic-only GStreamer NV12 video-range transfer gate.

No device elements, sensor access, preview files, user pixels, IR or sleep.
Run separately on SP11; maintained gcc-only test.sh stays portable.
"""
from __future__ import annotations
import gi
import numpy as np
gi.require_version("Gst","1.0")
from gi.repository import Gst


def rgb_from_neutral_nv12_y(y:int)->int:
    w,h=128,64
    if not 0<=y<=255:raise ValueError("INVALID_SYNTHETIC_Y")
    p=Gst.parse_launch(
       f"appsrc name=source block=true is-live=false format=time "
       f"caps=video/x-raw,format=NV12,width={w},height={h},framerate=1/1 "
       "! videoconvert ! video/x-raw,format=RGB "
       "! appsink name=output sync=false")
    src=p.get_by_name("source")
    sink=p.get_by_name("output")
    payload=bytes([y])*(w*h)+bytes([128])*(w*h//2)
    try:
        if p.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("SYNTHETIC_PIPELINE_START_FAIL")
        buf=Gst.Buffer.new_allocate(None,len(payload),None)
        assert buf.fill(0,payload)==len(payload)
        assert src.emit("push-buffer",buf)==Gst.FlowReturn.OK
        src.emit("end-of-stream")
        sample=sink.emit("try-pull-sample",2*Gst.SECOND)
        if sample is None:raise RuntimeError("SYNTHETIC_GST_SAMPLE_MISSING")
        b=sample.get_buffer()
        assert b.get_size()==w*h*3
        ok,m=b.map(Gst.MapFlags.READ)
        if not ok:raise RuntimeError("SYNTHETIC_GST_RGB_MAP_FAILED")
        try:
            values=np.frombuffer(m.data,dtype=np.uint8)
            low,high=int(values.min()),int(values.max())
            if low!=high:raise RuntimeError("SYNTHETIC_NEUTRAL_PATCH_NOT_UNIFORM")
            return low
        finally:b.unmap(m)
    finally:p.set_state(Gst.State.NULL)


def main()->None:
    Gst.init(None)
    assert rgb_from_neutral_nv12_y(16)==0
    assert rgb_from_neutral_nv12_y(17)==0
    assert 8<=rgb_from_neutral_nv12_y(27)<=15
    for full in (0,17,27,128,255):
        video=16+(219*full+127)//255
        got=rgb_from_neutral_nv12_y(video)
        assert abs(got-full)<=4,(full,video,got)
    print("RGB_GSTREAMER_CAMERA_FREE_NV12_STUDIO_RANGE_CONTRACT=PASS FULL_RANGE_DARK_VALUES_PRESERVED_WITH_OPTIN_ENCODING")


if __name__=="__main__":main()
