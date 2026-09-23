#!/usr/bin/python3
"""Camera-free synthetic exact HD/4K NV12 BT.601 producer metadata contract.

Current SP11 raw Bayer->NV12 matrices use provisional BT.601-like
Y=77R+150G+29B and U/V=601-like integer coefficients. Existing high
resolution v4l2loopback publishers do not tag colorspace and the
ordinary GStreamer decoder may guess BT.709 at 1080p/4K.
This probe uses synthetic color patches and in-memory buffers ONLY:
appsrc -> videoconvert -> RGB appsink. No V4L2 device, camera, RAW
photo, network, display, file, pixel array or image hash exported.
A successful format/matrix test is NOT sensor color calibration.
"""
from __future__ import annotations
import gi
gi.require_version("Gst","1.0")
from gi.repository import Gst

DIMENSIONS=((128,64),(1920,1080),(3840,2160))
SYNTHETIC_RGB={
    "neutral":(128,128,128),
    "red":(192,32,32),
    "green":(32,192,32),
    "blue":(32,32,192),
    "muted_warm":(200,140,110),
}


def source_601_nv12(rgb:tuple[int,int,int])->tuple[int,int,int]:
    r,g,b=rgb
    assert all(isinstance(x,int) and 0<=x<=255 for x in rgb)
    clip=lambda a:max(0,min(255,a))
    y=clip((77*r+150*g+29*b+128)>>8)
    u=clip(128+((-43*r-85*g+128*b+128)>>8))
    v=clip(128+((128*r-107*g-21*b+128)>>8))
    studio_y=lambda x:16+(219*x+127)//255
    studio_uv=lambda x:128+(1 if x>=128 else -1)*(
                                (abs(x-128)*224+127)//255)
    return studio_y(y),studio_uv(u),studio_uv(v)


def decoded_RGB(w:int,h:int,source:tuple[int,int,int],
                colorimetry:str|None)->tuple[int,int,int]:
    if w<64 or h<32 or (w&1) or (h&1):
        raise ValueError("EVEN_GEOMETRY_REQUIRED")
    y,u,v=source
    if not all(0<=x<=255 for x in source):
        raise ValueError("VIDEO_RANGE_BYTES_INVALID")
    extra="" if colorimetry is None else ",colorimetry="+colorimetry
    caps=f"video/x-raw,format=NV12,width={w},height={h},framerate=1/1"+extra
    pipeline=Gst.parse_launch(
        f'appsrc name=source is-live=false block=true format=time '
        f'caps="{caps}" ! videoconvert ! video/x-raw,format=RGB '
        '! appsink name=output sync=false max-buffers=1 drop=false'
    )
    src=pipeline.get_by_name("source")
    sink=pipeline.get_by_name("output")
    assert src is not None and sink is not None
    buf=Gst.Buffer.new_allocate(None,w*h*3//2,None)
    assert buf.fill(0,bytes([y])*(w*h)+bytes([u,v])*(w*h//4))==w*h*3//2
    try:
        if pipeline.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("SYNTHETIC_NO_CAMERA_GSTREAMER_PIPE_FAILED")
        if src.emit("push-buffer",buf)!=Gst.FlowReturn.OK:
            raise RuntimeError("SYNTHETIC_APP_SRC_FAILED")
        src.emit("end-of-stream")
        sample=sink.emit("try-pull-sample",5*Gst.SECOND)
        if sample is None:raise RuntimeError("SYNTHETIC_APP_SINK_MISSING")
        out=sample.get_buffer()
        if out.get_size()!=w*h*3:raise RuntimeError("SYNTHETIC_RGB_GEOMETRY_CHANGED")
        ok,mapped=out.map(Gst.MapFlags.READ)
        if not ok:raise RuntimeError("SYNTHETIC_RGB_MAP_FAILED")
        try:
            position=((h//2)*w+(w//2))*3
            result=tuple(int(x) for x in bytes(mapped.data[position:position+3]))
            return result
        finally:
            out.unmap(mapped)
    finally:
        pipeline.set_state(Gst.State.NULL)


def verify()->None:
    Gst.init(None)
    for name,rgb in SYNTHETIC_RGB.items():
        src=source_601_nv12(rgb)
        old=decoded_RGB(128,64,src,None)
        good=decoded_RGB(128,64,src,"bt601")
        assert old==good,(name,old,good)
        # Fixed camera-free mock scene and integer studio-matrix rounding.
        assert max(abs(a-b) for a,b in zip(good,rgb))<=6,(name,rgb,good)
    for w,h in DIMENSIONS[1:]:
        red=source_601_nv12(SYNTHETIC_RGB["red"])
        automatic=decoded_RGB(w,h,red,None)
        explicit601=decoded_RGB(w,h,red,"bt601")
        explicit709=decoded_RGB(w,h,red,"bt709")
        assert automatic==explicit709,(w,h,automatic,explicit709)
        assert automatic!=explicit601,(w,h,automatic,explicit601)
        assert max(abs(a-b) for a,b in zip(explicit601,SYNTHETIC_RGB["red"]))<=6
        assert abs(automatic[0]-explicit601[0])>=10
        print("SP11_SYNTHETIC_ONLY_HD_4K_BT601_ENCODER_UNTAGGED_DECODER_MISMATCH",
              f"{w}x{h}","automatically_BT709_red",automatic,
              "explicit_BT601_red",explicit601,
              "NO_CAMERA_PHOTO_OR_IMAGE_PIXELS_FROM_USER=YES")
    print("SP11_SYNTHETIC_NV12_EXPLICIT_BT601_COLOUR_METADATA_CONTRACT=PASS "
          "FRONT_1080P_REAR_4K_UNTAGGED_MATRIX_MISMATCH_IDENTIFIED")


if __name__=="__main__":verify()
