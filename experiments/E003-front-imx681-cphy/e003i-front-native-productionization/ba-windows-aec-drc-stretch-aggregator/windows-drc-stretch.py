#!/usr/bin/env python3
"""Clean-room CAECXConvergence::DRCStretchAggregator model.

Input blocks are already in Windows log1.03 coordinates. This stage does not
reconstruct GetExposureInfo; it consumes the seven-lane DRC block it produces.
"""
from dataclasses import dataclass, replace
import math, struct

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
ONE03=f32(1.03)

def pow103(delta): return f32(math.pow(ONE03,f32(delta)))
def log103_ratio(r): return f32(math.log(f32(r))/math.log(ONE03))

@dataclass(frozen=True)
class Lanes:
    # Windows memory ordering: Short, Long, Safe, s1..s4.
    short: float
    long: float
    safe: float
    s1: float
    s2: float
    s3: float
    s4: float
    def full_from(self,other:'Lanes')->'Lanes': return other

@dataclass(frozen=True)
class AggResult:
    lanes: Lanes
    pred_gain: float
    stretch_ratio: float
    drc_ratio: float
    branch: str


def aggregate(normal:Lanes,drc:Lanes,pred_gain:float,policy:int)->AggResult:
    pred=f32(pred_gain)
    stretch=pow103(normal.safe-normal.short)
    drcr=pow103(normal.safe-drc.short)

    # 0x1803d21ac..c4: Long is seeded from DRC unconditionally before policy.
    out=replace(normal,long=drc.long)

    one=f32(1.0)
    if stretch < one:
        return AggResult(out,pred,stretch,drcr,'invalid-stretch-ratio')
    if drcr <= one:
        return AggResult(out,pred,stretch,drcr,'normal-predictive')
    if stretch <= one: # effectively the unity boundary after the previous checks
        return AggResult(drc,one,stretch,drcr,'use-drc')

    # Both DRC and stretch ratios are > 1.
    if policy == 0:
        if drcr >= stretch:
            return AggResult(drc,one,stretch,drcr,'drc-greater-than-stretch')
        # Keep current stretch block (with DRC Long already seeded) and consume
        # overlapping predictive gain when possible.
        if drcr <= pred:
            return AggResult(out,f32(pred/drcr),stretch,drcr,'drc-below-pred-adjust-pg')
        return AggResult(out,one,stretch,drcr,'drc-above-pred-pg-unity')
    if policy == 1:
        # Cascade the current stretch separation onto the DRC block.
        delta=log103_ratio(stretch)
        casc=replace(drc,short=drc.short-float(delta))
        return AggResult(casc,pred,stretch,drcr,'cascade-pred-and-drc')
    if policy == 2:
        return AggResult(out,pred,stretch,drcr,'stretch-predictive-only')
    return AggResult(out,pred,stretch,drcr,'invalid-policy')
