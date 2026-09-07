#!/usr/bin/env python3
"""Offline model of the proven normal exposure-count=1 Windows output boundary."""
from dataclasses import dataclass
import math

POW_BASE = 1.0299999713897705  # exact double literal loaded by Windows from widened 1.03f

@dataclass(frozen=True)
class SevenLogLanes:
    short: float
    long: float
    safe: float
    s1: float
    s2: float
    s3: float
    s4: float

    def tuple(self):
        return (self.short,self.long,self.safe,self.s1,self.s2,self.s3,self.s4)

def converge_single_exposure(lanes: SevenLogLanes) -> SevenLogLanes:
    """ConvergeSensorExposures when active exposure count == 1.

    Windows seeds internal s1 from Short, skips the multi-exposure loop, and
    replicates the same Short log into s2/s3/s4. Short/Long/Safe survive the
    aggregator unchanged on this count=1 path.
    """
    s = lanes.short
    return SevenLogLanes(lanes.short, lanes.long, lanes.safe, s, s, s, s)

def populate_output(lanes: SevenLogLanes):
    """CAECXConvergence::PopulateOutput: pow(base,log), then FCVTZU."""
    out=[]
    for v in lanes.tuple():
        x=math.pow(POW_BASE,float(v))
        if not math.isfinite(x) or x < 0:
            raise ValueError('outside proven positive finite exposure domain')
        out.append(int(x))  # positive finite Python int() == truncation toward zero
    return tuple(out)
