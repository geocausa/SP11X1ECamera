#!/usr/bin/env python3
"""Clean float32 port of QcDeviceMFT8380.dll FUN_1809276e8.

Input: 7 source knots, 7 destination knots.
Output: 15 cubic coefficients for segments 1..5, three floats/segment.
"""
from __future__ import annotations
import struct

def f32(v):
    return struct.unpack("<f", struct.pack("<f", float(v)))[0]

def tmc141_coeff(src, dst):
    if len(src) != 7 or len(dst) != 7:
        raise ValueError("TMC141 requires 7 source and 7 destination knots")
    x=[f32(v) for v in src]; y=[f32(v) for v in dst]
    dx=[f32(x[i+1]-x[i]) for i in range(6)]
    sec=[f32(f32(y[i+1]-y[i])/dx[i]) for i in range(6)]
    m=[f32(0.0)]*6

    c=f32(f32(f32(dx[0]+dx[0])+dx[1])*sec[0]-f32(dx[0]*sec[1]))
    c=f32(c/f32(dx[0]+dx[1]))
    if not ((f32(sec[0]*sec[1]) >= 0.0 or abs(c) <= abs(f32(sec[0]*f32(3.0))))
            and f32(sec[0]*c) >= 0.0):
        c=f32(0.0)
    m[0]=c

    for i in range(1,5):
        a=f32(f32(dx[i-1]+dx[i-1])+dx[i])
        b=f32(f32(dx[i]+dx[i])+dx[i-1])
        m[i]=f32(f32(a+b)/f32(f32(a/sec[i])+f32(b/sec[i-1])))

    c=f32(f32(f32(dx[5]+dx[5])+dx[4])*sec[5]-f32(dx[5]*sec[4]))
    c=f32(c/f32(dx[5]+dx[4]))
    if not ((f32(sec[5]*sec[4]) >= 0.0 or abs(c) <= abs(f32(sec[5]*f32(3.0))))
            and f32(sec[5]*c) >= 0.0):
        c=f32(0.0)
    m[5]=c

    out=[]
    for i in range(1,6):
        h=dx[i]; s=sec[i]; mi=m[i]; mj=m[i+1] if i < 5 else m[5]
        out += [
            mi,
            f32(f32(f32(s*f32(3.0))-f32(mi+mi)-mj)/h),
            f32(f32(f32(mi-f32(s+s)+mj)/h)/h),
        ]
    return out

def pack_coeff(src, dst):
    v=tmc141_coeff(src,dst)
    return struct.pack("<15f", *v)
