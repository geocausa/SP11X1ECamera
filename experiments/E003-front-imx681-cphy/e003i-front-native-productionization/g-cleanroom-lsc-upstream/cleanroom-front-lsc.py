#!/usr/bin/env python3
from __future__ import annotations
import hashlib, struct
from pathlib import Path
import numpy as np

PAYLOAD_BYTES = 0xDD0
SAMPLES = 221
CHANNELS = 4
GRID_W = 17
GRID_H = 13
PAD_W = 19
PAD_H = 15
FULL_W = 4048
FULL_H = 3152
ACTIVE_W = 3840
ACTIVE_H = 2160
CROP_X = 104
CROP_Y = 496
OUT_CELL_X_HALF = 120
OUT_CELL_Y_HALF = 96
OUT_Y_CENTER_ADJUST_HALF = 36
CLAMP_MIN = np.float32(1.0)
CLAMP_MAX = np.float32(15.99899959564209)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def f32(v) -> np.float32:
    return np.float32(v)


def add(a,b): return f32(f32(a)+f32(b))
def sub(a,b): return f32(f32(a)-f32(b))
def mul(a,b): return f32(f32(a)*f32(b))
def div(a,b): return f32(f32(a)/f32(b))


def interpolate_leaf(a: bytes, b: bytes, ratio: float) -> bytes:
    if len(a) != 0xDF0 or len(b) != 0xDF0:
        raise ValueError('LSC leaf size drift')
    ratio = struct.unpack('<f', struct.pack('<f', float(ratio)))[0]
    af = struct.unpack('<884f', a[:PAYLOAD_BYTES])
    bf = struct.unpack('<884f', b[:PAYLOAD_BYTES])
    out = bytearray(0xDF0)
    for i,(av,bv) in enumerate(zip(af,bf)):
        # DeviceMFT interpolation callback: float32 endpoints/ratio -> float64 expression -> one float32 store.
        v = struct.unpack('<f',struct.pack('<f',(float(bv)-float(av))*float(ratio)+float(av)))[0]
        struct.pack_into('<f',out,i*4,v)
    if a[PAYLOAD_BYTES:] != b[PAYLOAD_BYTES:]:
        raise ValueError('LSC leaf tail mismatch')
    out[PAYLOAD_BYTES:] = a[PAYLOAD_BYTES:]
    return bytes(out)


def parse_otp(slot: bytes):
    if len(slot) != 0xDF0:
        raise ValueError('OTP slot size drift')
    hdr = struct.unpack_from('<3I',slot,0)
    if hdr != (1,3,221):
        raise ValueError(f'OTP header drift: {hdr!r}')
    channels=[]
    for off in (0x0C,0x380,0x6F4,0xA68):
        ch=struct.unpack_from('<221f',slot,off)
        if not all(v == float(int(v)) and 0 < v <= 65535 for v in ch):
            raise ValueError('OTP channel is not u16-as-float32')
        channels.append(tuple(ch))
    if slot[0xDDC:] != bytes(0x14):
        raise ValueError('OTP tail drift')
    return channels


def calibrate(x22: bytes, golden: tuple[float,...], otp_channels) -> bytes:
    if len(x22) != 0xDF0 or len(golden) != 884:
        raise ValueError('calibration input size drift')
    x=struct.unpack('<884f',x22[:PAYLOAD_BYTES])
    e=[v for ch in otp_channels for v in ch]
    out=[0.0]*884
    for i in range(221):
        out[i]=mul(div(golden[i],e[i]),x[i])
        g1=mul(div(golden[221+i],e[221+i]),x[221+i])
        g2=mul(div(golden[442+i],e[442+i]),x[442+i])
        gg=mul(add(g1,g2),f32(0.5))
        out[221+i]=gg
        out[442+i]=gg
        out[663+i]=mul(div(golden[663+i],e[663+i]),x[663+i])
    return struct.pack('<884f',*out)+x22[PAYLOAD_BYTES:]


def catmull_weights(t):
    t=f32(t); t2=mul(t,t); t3=mul(t2,t)
    w0=mul(sub(sub(add(t2,t2),t3),t),f32(0.5))
    w1=mul(add(sub(mul(t3,f32(3.0)),mul(t2,f32(5.0))),f32(2.0)),f32(0.5))
    w2=mul(add(sub(mul(t2,f32(4.0)),mul(t3,f32(3.0))),t),f32(0.5))
    w3=mul(sub(t3,t2),f32(0.5))
    return w0,w1,w2,w3


def h4(p,w):
    z=add(mul(p[0],w[0]),mul(p[1],w[1]))
    z=add(z,mul(p[2],w[2]))
    z=add(z,mul(p[3],w[3]))
    return z


def resample_channel(channel) -> bytes:
    if len(channel) != SAMPLES:
        raise ValueError('channel sample count drift')
    src=np.asarray(channel,dtype=np.float32).reshape(GRID_H,GRID_W)
    pad=np.zeros((PAD_H,PAD_W),dtype=np.float32)
    pad[1:14,1:18]=src
    # Surface creates a one-cell linear-extrapolation border around the 17x13 mesh.
    for r in range(1,14):
        pad[r,0]=sub(add(pad[r,1],pad[r,1]),pad[r,2])
        pad[r,18]=sub(add(pad[r,17],pad[r,17]),pad[r,16])
    for c in range(PAD_W):
        pad[0,c]=sub(add(pad[1,c],pad[1,c]),pad[2,c])
        pad[14,c]=sub(add(pad[13,c],pad[13,c]),pad[12,c])

    src_pitch_x=div(f32(FULL_W//2-1),f32(16.0))
    src_pitch_y=div(f32(FULL_H//2-1),f32(12.0))
    x0=CROP_X//2
    # 12*96 = 1152 half-res pixels; center over active 1080 => subtract 36.
    y0=CROP_Y//2-OUT_Y_CENTER_ADJUST_HALF
    out=np.empty((GRID_H,GRID_W),dtype=np.float32)

    for iy in range(GRID_H):
        py=f32(y0+iy*OUT_CELL_Y_HALF)
        v=div(add(py,src_pitch_y),src_pitch_y)
        iv=int(np.floor(v)); fy=sub(v,f32(iv)); wy=catmull_weights(fy)
        for ix in range(GRID_W):
            px=f32(x0+ix*OUT_CELL_X_HALF)
            u=div(add(px,src_pitch_x),src_pitch_x)
            iu=int(np.floor(u)); fx=sub(u,f32(iu)); wx=catmull_weights(fx)
            if iy in (0,GRID_H-1) or ix in (0,GRID_W-1):
                # Surface border branch is bilinear, not Catmull-Rom.
                omx=sub(f32(1.0),fx)
                top=add(mul(pad[iv,iu+1],fx),mul(pad[iv,iu],omx))
                omy=sub(f32(1.0),fy)
                z=mul(top,omy)
                bot=add(mul(pad[iv+1,iu+1],fx),mul(pad[iv+1,iu],omx))
                z=add(z,mul(bot,fy))
            else:
                hc=h4(pad[iv,iu-1:iu+3],wx)
                hp=h4(pad[iv-1,iu-1:iu+3],wx)
                hn=h4(pad[iv+1,iu-1:iu+3],wx)
                h2=h4(pad[iv+2,iu-1:iu+3],wx)
                z=mul(hc,wy[1])
                z=add(z,mul(hp,wy[0]))
                z=add(z,mul(hn,wy[2]))
                z=add(z,mul(h2,wy[3]))
            z=f32(max(CLAMP_MIN,z)); z=f32(min(CLAMP_MAX,z))
            out[iy,ix]=z
    return out.astype('<f4').tobytes()


def resample_x23(x23: bytes) -> bytes:
    if len(x23) != 0xDF0:
        raise ValueError('x23 size drift')
    vals=struct.unpack('<884f',x23[:PAYLOAD_BYTES])
    return b''.join(resample_channel(vals[c*221:(c+1)*221]) for c in range(CHANNELS))
