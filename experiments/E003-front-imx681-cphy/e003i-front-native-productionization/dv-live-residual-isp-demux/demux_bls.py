#!/usr/bin/env python3
from __future__ import annotations
import math, struct

MAX14_F32_BITS = 0x467ffc00  # 16383.0f
NORMALIZATION_LIMIT_BITS = 0x41fffdf4  # 31.999000549316406f
Q_GAIN_BITS = 0x44800000  # 1024.0f
BLACK_LEVEL = (602.0, 593.0, 592.0, 596.0)
CHANNEL_TERM = (1.0, 1.0, 1.0, 1.0)


def f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]


def from_bits(u: int) -> float:
    return struct.unpack('<f', struct.pack('<I', int(u) & 0xffffffff))[0]


def bits(x: float) -> int:
    return struct.unpack('<I', struct.pack('<f', f32(x)))[0]


def fsub(a: float, b: float) -> float:
    return f32(f32(a) - f32(b))


def fdiv(a: float, b: float) -> float:
    return f32(f32(a) / f32(b))


def fmul(a: float, b: float) -> float:
    return f32(f32(a) * f32(b))


def frinta_positive(x: float) -> int:
    # Scoped producer domain is strictly positive. ARM64 FRINTA rounds to
    # nearest integral value with halfway cases away from zero.
    x = f32(x)
    if not math.isfinite(x) or x < 0.0:
        raise ValueError('FRINTA positive-domain input required')
    return int(math.floor(float(x) + 0.5))


def _normalized(isp_gain: float, bls: float, channel: float) -> float:
    max14 = from_bits(MAX14_F32_BITS)
    x = fsub(max14, bls)
    x = fdiv(max14, x)
    x = fmul(x, isp_gain)
    x = fmul(x, channel)
    return x


def calculate(isp_gain: float) -> dict:
    gain = f32(isp_gain)
    if not math.isfinite(gain) or not (gain > 0.0):
        raise ValueError('finite positive isp_gain required')

    # Exact bayer0 Surface ordering from Demux141Setting::CalculateHWSetting.
    vals = [
        _normalized(gain, BLACK_LEVEL[1], CHANNEL_TERM[1]),  # calc6
        _normalized(gain, BLACK_LEVEL[3], CHANNEL_TERM[0]),  # calc7
        _normalized(gain, BLACK_LEVEL[2], CHANNEL_TERM[2]),  # calc8
        _normalized(gain, BLACK_LEVEL[0], CHANNEL_TERM[3]),  # calc9
    ]

    limit = from_bits(NORMALIZATION_LIMIT_BITS)
    vmax = max(vals)
    if vmax > limit:
        scale = fdiv(limit, vmax)
        vals = [fmul(scale, x) for x in vals]

    qgain = from_bits(Q_GAIN_BITS)
    q = [min(frinta_positive(fmul(x, qgain)), 0x7fff) for x in vals]
    calc6, calc7, calc8, calc9 = q

    reg_3b70 = ((calc6 & 0x7fff) << 16) | (calc7 & 0x7fff)
    reg_3b74 = ((calc9 & 0x7fff) << 16) | (calc8 & 0x7fff)
    return {
        'isp_gain': gain,
        'isp_gain_bits': bits(gain),
        'normalized': vals,
        'normalized_bits': [bits(x) for x in vals],
        'q10': q,
        'reg_3b70': reg_3b70,
        'reg_3b74': reg_3b74,
    }
