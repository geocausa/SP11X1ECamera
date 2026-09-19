#!/usr/bin/env python3
"""E004gr: strict offline neutral-chroma NV12 luma → 3ch model input.

The maintained HLOS worker outputs *full-range* sensor grayscale Y with U=V=128.
Do not use a video-range YUV color conversion (which remaps Y 16..235).
This diagnostic bridge never opens a camera, stores images, or authorizes login.
"""
import numpy as np

W=644
H=604
YLEN=W*H
NV12LEN=YLEN*3//2

class FrameRejected(ValueError):
    """Fail closed; do not include any pixel content in error messages."""

def nv12_full_range_gray_to_bgr(data):
    if type(data) is not bytes or len(data)!=NV12LEN:
        raise FrameRejected("invalid offline frame type or size")
    source=np.frombuffer(data,dtype=np.uint8)
    if not np.all(source[YLEN:]==128):
        raise FrameRejected("unexpected chroma in grayscale-only HLOS output")
    # The worker owns the neutral-chroma full-range luma contract: copying Y
    # is lossless. OpenCV COLOR_YUV2BGR_NV12 would distort full-range luma.
    y=source[:YLEN].reshape((H,W))
    bgr=np.repeat(y[:,:,None],3,axis=2).copy()
    if bgr.shape!=(H,W,3) or bgr.dtype!=np.uint8 or not bgr.flags.c_contiguous:
        raise FrameRejected("failed offline frame format")
    return bgr
