#!/usr/bin/env python3
"""Replay the live normal-front FrameSA measured-luma path from AEC_BE raw.

The live Windows path proved by AB23/AB26 is:
  Titan680 AEC_BE 32x32
    -> CAECXCoreGridStatsOut::ComputeLuma
    -> checkerboard cell selection (mask 0xf000003c)
    -> FrameLumaBE16x16 descriptor (mask 0x10)
    -> two selected source cells per 2x2 output bin, float32 running mean
    -> FrameSA / meter-bank ID 1 (Equally Weighted), float32 accumulation.

The raw oracle fixtures are intentionally local-only.  Their hashes and the
compact live provenance are recorded by the experiment metadata.
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

# Exact live/static float32 values.
R_COEFF_BITS = 0x3E991687  # 0.299f
G_COEFF_BITS = 0x3F1645A2  # 0.587f
B_COEFF_BITS = 0x3DE978D5  # 0.114f
# ConfigureSS: 1 / 2^(18-8) / 1980, rounded to float32.
SCALE_BITS = 0x3504655E

# AB26 live selection law.  The selected-mask array is a 32x32 checkerboard:
# exactly 512 cells are 0xf000003c and 512 are zero.  The active normal
# FrameLuma descriptor carries mask 0x10, which intersects 0xf000003c; the
# other observed descriptor carries mask 0x02 and does not intersect it.
SELECTED_CELL_MASK = 0xF000003C
FRAME_LUMA_DESCRIPTOR_MASK = 0x00000010
OTHER_DESCRIPTOR_MASK = 0x00000002
SELECTED_PARITY = 0  # selected iff (row + column) % 2 == 0


def from_bits(value: int) -> float:
    return struct.unpack('<f', struct.pack('<I', value))[0]


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
        # Titan680 parser mapping proved against AB23 and the byte-exact AA
        # parser fixture: q0,q3,q1,q2 -> R,B,Gr,Gb respectively.
        q = [struct.unpack_from('<Q', raw, ro + 8 * j)[0] & MASK34 for j in range(10)]
        r_sum, b_sum, gr_sum, gb_sum = q[0], q[3], q[1], q[2]

        counts = [struct.unpack_from('<H', raw, ro + off)[0]
                  for off in (0x06, 0x1E, 0x0E, 0x16)]
        if counts != [PIXELS_PER_CHANNEL] * 4:
            raise ValueError(f'region {i}: unsupported channel counts {counts}')

        # ARM64 ComputeLuma promotes the float coefficients and integer sums
        # to double, uses separate operations, multiplies by the promoted
        # float32 scale, then rounds once to float32.
        value = float(g_coeff) * float(gr_sum + gb_sum) * 0.5
        value = value + float(r_coeff) * float(r_sum)
        value = value + float(b_coeff) * float(b_sum)
        value = value * float(scale)
        out.append(f32(value))
    return out


def selected_for_frame_luma(index: int) -> bool:
    row, col = divmod(index, REGIONS_X)
    # This is the compact equivalent of the AB26 live mask test
    #   cell_mask[index] & FRAME_LUMA_DESCRIPTOR_MASK != 0
    # for the observed normal-front checkerboard mask array.
    return ((row + col) & 1) == SELECTED_PARITY


def downsample_frame_luma_16x16(luma32: list[float]) -> list[float]:
    if len(luma32) != REGIONS:
        raise ValueError(f'expected {REGIONS} luma cells, got {len(luma32)}')

    values = [f32(0.0)] * OUT_REGIONS
    counts = [0] * OUT_REGIONS

    for i, value in enumerate(luma32):
        if not selected_for_frame_luma(i):
            continue

        row, col = divmod(i, REGIONS_X)
        out_index = (row // 2) * OUT_X + (col // 2)
        counts[out_index] += 1

        # Exact mode-0 producer update: float32 incremental mean.
        old = values[out_index]
        delta = f32(value - old)
        step = f32(delta / f32(float(counts[out_index])))
        values[out_index] = f32(old + step)

    if min(counts) != 2 or max(counts) != 2:
        raise AssertionError(
            f'unexpected selected 32x32 -> 16x16 counts: {min(counts)}..{max(counts)}')
    return values


def equally_weighted_mean(values: list[float]) -> float:
    # FrameSA calculator uses separate float32 multiply/add accumulation.
    weight_sum = f32(0.0)
    weighted_sum = f32(0.0)
    for value in values:
        weight = f32(1.0)
        weight_sum = f32(weight_sum + weight)
        product = f32(weight * value)
        weighted_sum = f32(weighted_sum + product)
    return f32(weighted_sum / weight_sum)


def replay(raw: bytes) -> float:
    return equally_weighted_mean(downsample_frame_luma_16x16(per_region_luma(raw)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('raw', type=Path)
    ap.add_argument(
        '--expected-bits', type=lambda x: int(x, 0), default=None,
        help='optional expected float32 bits; when supplied, mismatch exits non-zero')
    args = ap.parse_args()

    raw = args.raw.read_bytes()
    result = replay(raw)
    result_bits = bits(result)

    print(f'raw_bytes={len(raw)} raw_sha256={sha256(raw)}')
    print(f'grid={REGIONS_X}x{REGIONS_Y} output={OUT_X}x{OUT_Y} pixels_per_channel={PIXELS_PER_CHANNEL}')
    print(f'coeff_bits=0x{R_COEFF_BITS:08x},0x{G_COEFF_BITS:08x},0x{B_COEFF_BITS:08x} scale_bits=0x{SCALE_BITS:08x}')
    print(f'selected_cell_mask=0x{SELECTED_CELL_MASK:08x} descriptor_mask=0x{FRAME_LUMA_DESCRIPTOR_MASK:08x} selected_parity={SELECTED_PARITY}')
    print('selected_cells=512 selected_cells_per_output_bin=2 meter_bank_id=1 meter_name=Equally Weighted')
    print(f'measured_luma={result:.17g} bits=0x{result_bits:08x}')

    if args.expected_bits is None:
        return 0

    passed = result_bits == args.expected_bits
    print(f'expected_bits=0x{args.expected_bits:08x} pass={passed}')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
