#!/usr/bin/env python3
"""Offline model of the Windows CAnalyzer target-SI arithmetic.

This intentionally models only the scalar producer closed by E003i-BD.
The source exposure scalar is already in the Windows linear exposure
coordinate selected by sourceType; downstream convergence/arbitration is
proved by prior stages.
"""
from __future__ import annotations
import math
import struct

EPS_BITS = 0x33D6BF95

def f32(value: float) -> float:
    return struct.unpack('<f', struct.pack('<f', float(value)))[0]

def from_bits(bits: int) -> float:
    return struct.unpack('<f', struct.pack('<I', bits))[0]

EPS = from_bits(EPS_BITS)

# Tuning exposure type -> internal seven-lane enum, as implemented by
# UtilExposureTypeTuning2Enum @ 0x180388630.
TUNING_TO_INTERNAL = (0, 2, 1, 3, 4, 5, 6, 3)
INTERNAL_NAMES = ('Short', 'Long', 'Safe', 'S1', 'S2', 'S3', 'S4')
TUNING_NAMES = tuple(INTERNAL_NAMES[i] for i in TUNING_TO_INTERNAL)

def source_lane(source_type: int) -> int:
    if not 0 <= source_type < len(TUNING_TO_INTERNAL):
        raise ValueError(f'unsupported sourceType {source_type}')
    return TUNING_TO_INTERNAL[source_type]

def target_si(source_exposure: float, measured_luma: float, target_low: float) -> int:
    """Reproduce the normal positive finite Windows SI path.

    ARM64 path:
      denom = max(measured_luma, 0x33d6bf95f)
      ratio = float32(target_low / denom)
      product = double(source_exposure) * double(ratio)
      SI = FCVTZU(product)
    """
    measured = f32(measured_luma)
    target = f32(target_low)
    denom = measured if measured > EPS else EPS
    ratio = f32(target / denom)
    product = float(source_exposure) * float(ratio)
    if not math.isfinite(product) or product < 0.0:
        raise ValueError('model scope is positive finite exposure products')
    return int(product)

if __name__ == '__main__':
    print(f'EPS_BITS=0x{EPS_BITS:08x}')
    print(f'EPS={EPS:.17g}')
    print('TUNING_TO_INTERNAL=' + ','.join(map(str, TUNING_TO_INTERNAL)))
    print('TUNING_NAMES=' + ','.join(TUNING_NAMES))
    print('EXAMPLE_SI=' + str(target_si(25_000_000.0, 1.0, 50.0)))
