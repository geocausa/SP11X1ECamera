#!/usr/bin/env python3
"""E004is: offline SP11 rear pgAA packed GRBG10 -> 1920x1080 NV12.

A conservative 2x2 GRBG tile colour proxy, NOT camera ISP IQ/CCM, libcamera
integration, pixel-accurate Windows colour or a real-time converter.
No camera/video/DRM device opened. No kernel install or hardware access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

import numpy as np
from PIL import Image, ImageOps

WIDTH=4076
HEIGHT=2806
STRIDE=5104
FRAME_BYTES=STRIDE*HEIGHT
OUT_WIDTH=1920
OUT_HEIGHT=1080
OUT_FRAME_BYTES=OUT_WIDTH*OUT_HEIGHT*3//2
REFERENCE_SHA="6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346"

def unpack_grbg10p(frame:bytes, *, width=WIDTH, height=HEIGHT, stride=STRIDE)->np.ndarray:
    """Exactly V4L2 SGRBG10P: 4 high bytes and a fifth 2-bit LSB byte.

    A row's valid payload is (width/4)*5 bytes; ignore explicit end padding.
    No inter-row pixel groups or implicit RAW10 endian assumptions.
    """
    if width<4 or width%4 or height<2 or height%2:
        raise ValueError("Bayer dimensions must be even, width divisible by 4")
    if stride < width*5//4 or stride%16:
        raise ValueError("row stride invalid for packed GRBG10")
    if len(frame) != stride*height:
        raise ValueError("rear frame length/stride invalid")
    group=np.frombuffer(frame,dtype=np.uint8).reshape(height,stride)
    group=group[:,:width*5//4].reshape(height,width//4,5)
    bits=group[:,:,4].astype(np.uint16)
    raw=np.empty((height,width),dtype=np.uint16)
    for i in range(4):
        raw[:,i::4]=(group[:,:,i].astype(np.uint16)<<2) | ((bits>>(2*i)) & 3)
    return raw

def pack_grbg10p(raw:np.ndarray, *,stride:int)->bytes:
    """Synthetic test fixture only: inverse MIPI four-pixels-per-five bytes."""
    height,width=raw.shape
    if width%4 or height%2 or stride%16 or stride<width*5//4:
        raise ValueError("invalid synthetic packed geometry")
    if raw.dtype!=np.uint16 or np.any(raw>1023):
        raise ValueError("RAW10 sample outside 0..1023")
    groups=raw.reshape(height,width//4,4)
    out=np.zeros((height,stride),dtype=np.uint8)
    p=out[:,:width*5//4].reshape(height,width//4,5)
    p[:,:,:4]=(groups>>2).astype(np.uint8)
    p[:,:,4]=(groups[:,:,0]&3 | ((groups[:,:,1]&3)<<2) |
               ((groups[:,:,2]&3)<<4) | ((groups[:,:,3]&3)<<6)).astype(np.uint8)
    return out.tobytes()

def preview_nv12_from_grbg10p(frame:bytes, *,width=WIDTH,height=HEIGHT,
                              stride=STRIDE,out_width=OUT_WIDTH,
                              out_height=OUT_HEIGHT)->bytes:
    if out_width<2 or out_height<2 or out_width%2 or out_height%2:
        raise ValueError("NV12 output needs even dimensions")
    if out_width>width//2 or out_height>height//2:
        raise ValueError("do not upsample proxy above half-resolution tiles")
    raw8=(unpack_grbg10p(frame,width=width,height=height,stride=stride)>>2).astype(np.uint8)
    # SGRBG = G R / B G. Keep 2x2 tile RGB only; do not mislabel
    # this proxy as calibrated full-resolution bilinear demosaic.
    green=((raw8[0::2,0::2].astype(np.uint16)+
            raw8[1::2,1::2].astype(np.uint16)+1)//2).astype(np.uint8)
    red=raw8[0::2,1::2]
    blue=raw8[1::2,0::2]
    rgb=np.stack((red,green,blue),axis=-1)
    image=ImageOps.fit(Image.fromarray(rgb,"RGB"),(out_width,out_height),
                       method=Image.Resampling.BILINEAR,centering=(0.5,0.5))
    ycbcr=np.asarray(image.convert("YCbCr"),dtype=np.uint8)
    y=ycbcr[:,:,0].copy()
    # Pillow's RGB->YCbCr approximates full-range BT.601. Explicit
    # 2x2 arithmetic chroma averaging produces one Cb/Cr per 2x2 luma.
    cb=((ycbcr[:,:,1].astype(np.uint16).reshape(out_height//2,2,out_width//2,2)
         .sum(axis=(1,3))+2)//4).astype(np.uint8)
    cr=((ycbcr[:,:,2].astype(np.uint16).reshape(out_height//2,2,out_width//2,2)
         .sum(axis=(1,3))+2)//4).astype(np.uint8)
    uv=np.empty((out_height//2,out_width//2,2),dtype=np.uint8)
    uv[:,:,0]=cb
    uv[:,:,1]=cr
    result=y.tobytes()+uv.tobytes()
    assert len(result)==out_width*out_height*3//2
    return result

def check_input(path:Path)->bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("input must be an ordinary, non-symlink frame file")
    with path.open("rb") as f:
        frame=f.read(FRAME_BYTES+1)
    if len(frame)!=FRAME_BYTES:
        raise ValueError("not one complete SP11 rear 4076x2806 pgAA frame")
    return frame

def private_destination(output:Path)->None:
    # Never overwrite any pre-existing output, symlink or standard location.
    absolute=output.resolve(strict=False)
    if not absolute.is_relative_to(Path("/tmp")):
        raise ValueError("offline destination must be a private /tmp path")
    if output.exists() or output.is_symlink():
        raise FileExistsError("output directory must not exist")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise ValueError("destination parent must be an existing directory")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--reference-colorbar",action="store_true",
                    help="require byte-exact prior SP11 rear colourbar evidence")
    args=ap.parse_args()
    private_destination(args.output_dir)
    frame=check_input(args.input)
    h=hashlib.sha256(frame).hexdigest()
    if args.reference_colorbar and h!=REFERENCE_SHA:
        raise ValueError("provided frame is not the accepted rear colourbar")
    result=preview_nv12_from_grbg10p(frame)
    stage=Path(tempfile.mkdtemp(prefix=".e004is-",dir=args.output_dir.parent))
    os.chmod(stage,0o700)
    try:
        out=stage/"rear-proxy-1920x1080.nv12"
        with out.open("xb") as f:
            f.write(result)
        os.chmod(out,0o600)
        manifest={"stage":"E004is","source_format":"V4L2_PIX_FMT_SGRBG10P/pgAA",
            "source_width":WIDTH,"source_height":HEIGHT,"source_stride_bytes":STRIDE,
            "source_bytes":FRAME_BYTES,"source_sha256":h,
            "accepted_colorbar_sha_matched":bool(args.reference_colorbar),
            "output_format":"NV12","output_width":OUT_WIDTH,
            "output_height":OUT_HEIGHT,"output_bytes":len(result),
            "output_sha256":hashlib.sha256(result).hexdigest(),
            "method":"2x2 GRBG tile proxy + centre-cropped 16:9 Pillow BT.601-like full-range YCbCr 2x2 UV averaging",
            "colour_calibrated":False,"pixel_parity_with_windows":False,
            "real_time_performance_proven":False,"live_camera_used":False,
            "front_qc10c_supported":False}
        (stage/"RESULT.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
        os.chmod(stage/"RESULT.json",0o600)
        stage.rename(args.output_dir)
        print(json.dumps(manifest,sort_keys=True))
    except BaseException:
        shutil.rmtree(stage)
        raise

if __name__=="__main__":main()
