#!/usr/bin/env python3
"""Independent offline BPCABF411 common calculation for E007a's seven words.

Inputs are semantic interpolated region terms and normalized reserve anchors.
They are not decoded register words. Hardware/request binding is outside scope.
"""
from __future__ import annotations
import math
import struct

REGS = (0x49B8, 0x49BC, 0x49D0, 0x49D4, 0x49D8, 0x49DC, 0x49E0)

def f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]

def round_away(x):
    return int(math.copysign(math.floor(abs(x) + 0.5), x))

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def quantize(x, maximum):
    if not math.isfinite(x) or x < 0 or x > 1023:
        raise ValueError("semantic coefficient outside finite nonnegative domain")
    return clamp(round_away(f32(f32(x) * 256.0)), 0, maximum)

def inverse_segment(gap, delta):
    # Common calculation clamps both differences to at least one, including
    # flat curves. The quotient uses the ORIGINAL shift before its 4-bit clamp.
    gap = clamp(gap, 1, 4095)
    delta = clamp(delta, 1, 255)
    logs = f32(f32(f32(math.log(gap)) + f32(math.log(255))) -
               f32(math.log(delta)))
    shift = int(f32(logs / f32(math.log(2))))
    quotient = ((delta << (shift & 31)) // gap) & 65535
    return clamp(quotient, 0, 255), clamp(shift, 0, 15)

def signed_segment(start, end, denominator):
    if denominator <= 0:
        raise ValueError("zero BPC level denominator")
    delta = end - start
    shift = 10
    while shift >= 0:
        numerator = delta << shift
        quotient = math.trunc(numerator / denominator)
        if -256 <= quotient <= 256:
            value = round_away(f32(f32(numerator) / f32(denominator)))
            return clamp(value, -256, 256), shift
        shift -= 1
    raise ValueError("BPC slope not representable")

def calculate(levels, preserve, curves, anchors):
    if len(levels) != 2 or len(preserve) != 2 or any(len(c) != 2 for c in preserve):
        raise ValueError("two levels and two two-point preserve curves required")
    if len(curves) != 2 or any(len(c) != 5 for c in curves):
        raise ValueError("two five-point byte curves required")
    if len(anchors) != 5 or any(not math.isfinite(x) or x < 0 for x in anchors):
        raise ValueError("five finite nonnegative normalized anchors required")
    if anchors[-1] <= 0 or any(a > b for a, b in zip(anchors, anchors[1:])):
        raise ValueError("monotone anchors with positive normalization required")
    if any(not math.isfinite(x) for x in levels):
        raise ValueError("non-finite levels")
    lo, hi = map(f32, levels)
    if lo == hi:
        hi = f32(lo + 1.0)
    denominator = clamp(round_away(f32(hi - lo)), 0, 1023)
    # Native common helper powf(normalized anchor, 2), then truncates Q12.
    knots = [int(f32(f32(math.pow(f32(f32(x) / f32(anchors[-1])), 2.0)) *
                     4095.0)) & 65535 for x in anchors]
    state = {"signed10": [], "unsigned9": [], "nibble4": [],
             "byte_group0": [], "byte_group1": [], "nibble_group": []}
    for channel in range(2):
        p = [quantize(x, 256) for x in preserve[channel]]
        slope, shift = signed_segment(p[0], p[1], denominator)
        state["signed10"].append(slope)
        state["unsigned9"].append(p[0])
        state["nibble4"].append(shift)
        curve = [quantize(x, 255) for x in curves[channel]]
        pairs = [inverse_segment(knots[i+1] - knots[i], curve[i] - curve[i+1])
                 for i in range(4)]
        state["byte_group0"].append(curve[:4])
        state["byte_group1"].append([p[0] for p in pairs])
        state["nibble_group"].append([p[1] for p in pairs])
    return state

def pack(state):
    words = {}
    for c, reg in enumerate(REGS[:2]):
        words[reg] = ((state["signed10"][c] & 1023) |
                      (state["unsigned9"][c] << 16) |
                      (state["nibble4"][c] << 28))
    for c in range(2):
        words[REGS[2+c]] = sum(v << (i*8) for i,v in enumerate(state["byte_group0"][c]))
        words[REGS[4+c]] = sum(v << (i*8) for i,v in enumerate(state["byte_group1"][c]))
    words[REGS[6]] = sum(state["nibble_group"][c][i] << (4*(c*4+i))
                         for c in range(2) for i in range(4))
    return words
