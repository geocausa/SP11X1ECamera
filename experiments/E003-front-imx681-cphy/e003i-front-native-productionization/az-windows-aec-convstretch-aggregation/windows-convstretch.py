#!/usr/bin/env python3
"""Clean-room model of the Windows request-local ConvStretch aggregation boundary.

Scope:
  interpolated stretch core -> 0x14 runtime record -> AggregateStretchOutput
  -> filtered/quantized stretch -> Short/Safe/Long BasicSafe lane update.

This deliberately stops before GetExposureInfo / DRCStretchAggregator.
"""
from __future__ import annotations
from dataclasses import dataclass
import math, struct


def f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]


def fadd(a,b): return f32(f32(a)+f32(b))
def fsub(a,b): return f32(f32(a)-f32(b))
def fmul(a,b): return f32(f32(a)*f32(b))
def fdiv(a,b): return f32(f32(a)/f32(b))

def u32(x:int)->int: return x & 0xffffffff

ONE03=f32(struct.unpack('<f',struct.pack('<I',0x3f83d70a))[0])
EPS=f32(struct.unpack('<f',struct.pack('<I',0x33d6bf95))[0])
RECIP_LOG_ONE03=f32(1.0 / math.log(ONE03))


def log103_f32(x:float)->float:
    # DeviceMFT path is logf(x) followed by the shared float32 reciprocal-log scale.
    return fmul(f32(math.log(f32(x))), RECIP_LOG_ONE03)


def pow103_f32(x:float)->float:
    return f32(math.pow(ONE03, f32(x)))


def frinta_f32(x:float)->float:
    x=f32(x)
    if x >= 0: return f32(math.floor(x+0.5))
    return f32(math.ceil(x-0.5))


@dataclass
class StretchRecord:
    weight: float = 0.0        # runtime +0x00
    offset: float = 0.0        # runtime +0x04, FinalOff in the Windows log
    comp: float = 0.0          # runtime +0x08
    temp_weight: float = 0.0   # runtime +0x0c
    negative: int = 0          # runtime +0x10

    def normalized(self):
        return StretchRecord(f32(self.weight),f32(self.offset),f32(self.comp),f32(self.temp_weight),1 if self.negative else 0)


def materialize_record(stretch_type:int, weight:float, stretch_factor_offset:float,
                       comp:float, temp_weight:float)->StretchRecord:
    raw=f32(stretch_factor_offset)
    if stretch_type == 0:
        if abs(f32(raw)) < EPS:
            off=f32(0.0)
        else:
            if raw <= 0.0:
                raise ValueError('stretch_type 0 logarithmic factor must be positive unless effectively zero')
            off=log103_f32(raw)
    else:
        off=raw
    return StretchRecord(f32(weight),off,f32(comp),f32(temp_weight),1 if off < 0.0 else 0)


def _slot(head:int, rel:int, capacity:int)->int:
    # Mirrors 32-bit ADD followed by unsigned divide/remainder in the DeviceMFT.
    return u32(u32(head)+u32(rel)) % capacity


def aggregate_stretch_output(records:list[StretchRecord], active_count:int, agg_type:int,
                             direction_mode:int, target_negative:bool,
                             head:int=0)->StretchRecord:
    """Mirror AggregateStretchOutput's ring/sort/select behavior.

    `records` is the full runtime ring and therefore supplies the capacity used by UDIV/MSUB.
    ComputeTargetStretchOutput resets head to zero for the request, but head remains an argument
    here so the ring arithmetic is explicit and testable.
    """
    capacity=len(records)
    if capacity <= 0: raise ValueError('runtime ring capacity must be positive')
    if active_count < 0 or active_count > capacity: raise ValueError('invalid active_count')
    if agg_type < 0 or agg_type >= 5: raise ValueError('Windows treats aggregation type >=5 as invalid')
    ring=[r.normalized() for r in records]

    if agg_type == 0:
        tw=f32(0.0); so=f32(0.0); comp=f32(0.0); temp=f32(0.0)
        for rel in range(active_count):
            r=ring[_slot(head,rel,capacity)]
            accept = direction_mode == 0 or (direction_mode == 1 and r.negative == int(target_negative))
            if not accept: continue
            tw=fadd(tw,r.weight)
            so=fadd(so,fmul(r.offset,r.weight))
            comp=fadd(comp,fmul(r.comp,r.weight))
            temp=fadd(temp,fmul(r.temp_weight,r.weight))
        if tw > 0.0:
            so=fdiv(so,tw); comp=fdiv(comp,tw); temp=fdiv(temp,tw)
        else:
            so=comp=temp=f32(0.0)
        # Windows caller zero-initializes the output; mode 0 never writes output +0.
        return StretchRecord(0.0,so,comp,temp,0)

    # Modes 1/2 sort the active request records by FinalOff (+4).
    # Modes 3/4 sort them by Weight (+0). Bubble-sort swaps the complete 0x14 records.
    key = (lambda r:r.weight) if agg_type in (3,4) else (lambda r:r.offset)
    for outer in range(max(0,active_count-1)):
        for inner in range(max(0,active_count-outer-1)):
            a=_slot(head,inner,capacity); b=_slot(head,inner+1,capacity)
            if key(ring[a]) > key(ring[b]): ring[a],ring[b]=ring[b],ring[a]

    selected=-1
    if agg_type == 3:  # ascending Weight endpoint 0
        if active_count:
            r=ring[_slot(head,0,capacity)]
            if direction_mode == 0 or (direction_mode == 1 and r.negative == int(target_negative)):
                selected=0
    elif agg_type == 4:  # ascending Weight endpoint count-1
        if active_count:
            rel=active_count-1; r=ring[_slot(head,rel,capacity)]
            if direction_mode == 0 or (direction_mode == 1 and r.negative == int(target_negative)):
                selected=rel
    else:
        # Modes 1/2 first sort by offset. Windows then scans for first strictly-positive offset.
        first_positive=-1
        for rel in range(active_count):
            if ring[_slot(head,rel,capacity)].offset > 0.0:
                first_positive=rel; break
        if agg_type == 1:
            if not target_negative:
                selected=first_positive
            elif active_count:
                first=ring[_slot(head,0,capacity)]
                selected=u32(first_positive-1) if first.offset < 0.0 else -1
        else: # agg_type == 2
            if not target_negative:
                if active_count:
                    rel=active_count-1
                    selected=rel if ring[_slot(head,rel,capacity)].offset > 0.0 else -1
            elif active_count:
                selected=-1 if ring[_slot(head,0,capacity)].offset > 0.0 else 0

    if selected == -1:
        # Exact fallback written at 0x1803d01a8..1b4; +0 remains caller's zero.
        return StretchRecord(0.0,0.0,1.0,0.5,0).normalized()
    return ring[_slot(head,selected,capacity)].normalized()


@dataclass(frozen=True)
class StretchLaneResult:
    short_log: float
    safe_log: float
    long_log: float
    pred_gain: float
    short_stretch: float
    safe_stretch: float
    filtered_offset: float


def apply_aggregated_stretch(basic_safe_log:float, previous_delta:float,
                             aggregate:StretchRecord, minimum_step:float)->StretchLaneResult:
    """Mirror ComputeTargetStretchOutput after AggregateStretchOutput.

    Windows logger ABI establishes the three displayed lanes as:
      +0xa0 Short, +0xb0 Safe, +0xa8 Long.
    """
    a=aggregate.normalized()
    filtered=fadd(fmul(fsub(1.0,a.temp_weight),previous_delta), fmul(a.temp_weight,a.offset))

    # Windows constructs one log1.03 step from logf(1.03f)*reciprocal and suppresses
    # sub-step offsets before quantization.
    one_step=log103_f32(ONE03)
    if abs(f32(filtered)) < float(one_step):
        short=f32(0.0)
    else:
        q=f32(minimum_step)
        if not (q > 0.0 and q <= 1.0): q=f32(0.5)
        short=fmul(frinta_f32(fdiv(filtered,q)),q)

    pred=f32(1.0)
    if short < 0.0:
        pred=pow103_f32(fmul(abs(short),a.comp))
    log_pred=log103_f32(pred)
    safe_stretch=fadd(short,log_pred)

    return StretchLaneResult(
        short_log=float(basic_safe_log)+float(short),
        safe_log=float(basic_safe_log)+float(safe_stretch),
        long_log=float(basic_safe_log),
        pred_gain=pred,
        short_stretch=short,
        safe_stretch=safe_stretch,
        filtered_offset=filtered)
