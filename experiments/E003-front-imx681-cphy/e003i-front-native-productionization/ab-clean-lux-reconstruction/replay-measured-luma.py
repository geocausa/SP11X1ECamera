#!/usr/bin/env python3
"""Replay the normal front FrameSA measured-luma path from an AEC_BE raw fixture.

This implements the statically proved DeviceMFT path:
  Titan680 AEC_BE 32x32 -> ComputeLuma -> LumaBE16x16 ->
  FrameLumaBE16x16 calculator with meter-bank ID 1 (Equally Weighted).

The local oracle fixture is intentionally not committed; it is SHA-pinned in
FIXTURE-MANIFEST.json.
"""
import argparse
import hashlib
import struct
from pathlib import Path

MASK34 = 0x3FFFFFFFF
RAW_STRIDE = 0x50
REGIONS_X = 32
REGIONS_Y = 32
REGIONS = REGIONS_X * REGIONS_Y
PIXELS_PER_CHANNEL = 1980
OUT_X = 16
OUT_Y = 16
OUT_REGIONS = OUT_X * OUT_Y

# Captured/static exact float32 values.
R_COEFF_BITS = 0x3E991687  # 0.299f
G_COEFF_BITS = 0x3F1645A2  # 0.587f
B_COEFF_BITS = 0x3DE978D5  # 0.114f
# ConfigureSS: 1 / 2^(18-8) / 1980, rounded to float32.
SCALE_BITS = 0x3504655E
AA_EXPECTED_BITS = 0x41F4042B


def from_bits(bits: int) -> float:
    return struct.unpack('<f', struct.pack('<I', bits))[0]


def f32(value: float) -> float:
    return struct.unpack('<f', struct.pack('<f', float(value)))[0]


def bits(value: float) -> int:
    return struct.unpack('<I', struct.pack('<f', f32(value)))[0]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def per_region_luma(raw: bytes) -> list[float]:
    if len(raw) != REGIONS * RAW_STRIDE:
        raise ValueError(f'expected {REGIONS * RAW_STRIDE:#x} bytes, got {len(raw):#x}')

    r_coeff = from_bits(R_COEFF_BITS)
    g_coeff = from_bits(G_COEFF_BITS)
    b_coeff = from_bits(B_COEFF_BITS)
    scale = from_bits(SCALE_BITS)
    out: list[float] = []

    for i in range(REGIONS):
        ro = i * RAW_STRIDE
        # The active Titan680 parser maps q0,q3,q1,q2 to R,B,Gr,Gb.
        q = [struct.unpack_from('<Q', raw, ro + 8 * j)[0] & MASK34 for j in range(10)]
        r_sum, b_sum, gr_sum, gb_sum = q[0], q[3], q[1], q[2]

        # AA fixture has no missing/saturated samples in these four channels.
        counts = [struct.unpack_from('<H', raw, ro + off)[0]
                  for off in (0x06, 0x1e, 0x0e, 0x16)]
        if counts != [PIXELS_PER_CHANNEL] * 4:
            raise ValueError(f'region {i}: unsupported channel counts {counts}')

        # ARM64 ComputeLuma promotes float coefficients and integer sums to
        # double, performs separate mul/add operations, multiplies by the
        # float32 scale promoted to double, then rounds once to float32.
        value = float(g_coeff) * float(gr_sum + gb_sum) * 0.5
        value = value + float(r_coeff) * float(r_sum)
        value = value + float(b_coeff) * float(b_sum)
        value = value * float(scale)
        out.append(f32(value))
    return out


def downsample_16x16(luma32: list[float]) -> list[float]:
    # Runtime output mapping proved by CAECXCoreGridStatsOut::ComputeLuma:
    # y=floor(flat_index / 64), x=floor((flat_index % 32) * 0.5).
    # Each 2x2 output cell is accumulated as a float32 running mean.
    values = [f32(0.0)] * OUT_REGIONS
    counts = [0] * OUT_REGIONS
    for i, value in enumerate(luma32):
        out_index = (i // 64) * OUT_X + int((i % REGIONS_X) * 0.5)
        counts[out_index] += 1
        old = values[out_index]
        delta = f32(value - old)
        step = f32(delta / f32(float(counts[out_index])))
        values[out_index] = f32(step + old)
    if min(counts) != 4 or max(counts) != 4:
        raise AssertionError(f'unexpected 32x32 -> 16x16 counts: {min(counts)}..{max(counts)}')
    return values


def equally_weighted_mean(values: list[float]) -> float:
    # Stats calculator uses separate float32 multiply and add; weight is 1.0f.
    weight_sum = f32(0.0)
    weighted_sum = f32(0.0)
    for value in values:
        weight = f32(1.0)
        weight_sum = f32(weight_sum + weight)
        product = f32(weight * value)
        weighted_sum = f32(weighted_sum + product)
    return f32(weighted_sum / weight_sum)


def replay(raw: bytes) -> float:
    return equally_weighted_mean(downsample_16x16(per_region_luma(raw)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('raw', type=Path)
    ap.add_argument('--expected-bits', type=lambda x: int(x, 0), default=AA_EXPECTED_BITS)
    args = ap.parse_args()

    raw = args.raw.read_bytes()
    result = replay(raw)
    result_bits = bits(result)
    print(f'raw_bytes={len(raw)} raw_sha256={sha256(raw)}')
    print(f'grid={REGIONS_X}x{REGIONS_Y} output={OUT_X}x{OUT_Y} pixels_per_channel={PIXELS_PER_CHANNEL}')
    print(f'coeff_bits=0x{R_COEFF_BITS:08x},0x{G_COEFF_BITS:08x},0x{B_COEFF_BITS:08x} scale_bits=0x{SCALE_BITS:08x}')
    print('meter_bank_id=1 meter_name=Equally Weighted')
    print(f'measured_luma={result:.17g} bits=0x{result_bits:08x}')
    passed = result_bits == args.expected_bits
    print(f'expected_bits=0x{args.expected_bits:08x} pass={passed}')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
