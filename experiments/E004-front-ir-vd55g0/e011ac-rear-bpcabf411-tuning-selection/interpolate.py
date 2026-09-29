#!/usr/bin/env python3
"""Independent float-field BPC region interpolation; no hardware access."""
import math,struct
FIELD_COUNT=107
EPSILON=1e-6
def f32(value):
    value=struct.unpack("<f",struct.pack("<f",value))[0]
    if not math.isfinite(value):raise ValueError("nonfinite binary32 input or arithmetic")
    return value
def interpolate(lower,upper,ratio):
    if len(lower)!=FIELD_COUNT or len(upper)!=FIELD_COUNT:
        raise ValueError("107 region fields required")
    r=f32(ratio)
    same=lower is upper
    a=[f32(x) for x in lower];b=[f32(x) for x in upper]
    if same:return list(a)
    if 0<r<1:
        # Inputs/ratio are binary32, but native FCVT -> FSUB/FMUL/FADD
        # computes in binary64, then FCVT rounds once to binary32. No FMA.
        return [f32((float(y)-float(x))*float(r)+float(x)) for x,y in zip(a,b)]
    if abs(r)<EPSILON:return list(a)
    if abs(r-1)<EPSILON:return list(b)
    raise ValueError("ratio outside native interpolation edge tolerance")
