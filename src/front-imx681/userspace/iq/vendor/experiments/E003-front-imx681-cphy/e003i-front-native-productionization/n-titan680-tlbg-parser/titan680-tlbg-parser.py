#!/usr/bin/env python3
from __future__ import annotations
import struct

TITAN680_VERSION = 0x60800
REGIONS = 32 * 24
RAW_RECORD_BYTES = 0x50
RAW_BYTES = REGIONS * RAW_RECORD_BYTES
PARSED_HEADER_BYTES = 0x20
PARSED_RECORD_BYTES = 0x64
PARSED_FULL_BYTES = PARSED_HEADER_BYTES + REGIONS * PARSED_RECORD_BYTES
PARSED_BOUNDED_BYTES = 0x12BEC
BIT_DEPTH = 18
CHANNEL_THRESHOLD = 0x3FFFF
BLACK_LEVEL_STRETCH = 1.0
SUM_MASK = 0x3FFFFFFFF

# Titan680 special path in QcDeviceMFT8380.dll FUN_1805f23a0.
# Each tuple is (parsed-record offset, raw-record offset) for a 64-bit sum.
_SUM_MAP = (
    (0x00, 0x00),
    (0x08, 0x18),
    (0x10, 0x08),
    (0x18, 0x10),
    (0x20, 0x20),
    (0x32, 0x28),
    (0x3A, 0x40),
    (0x42, 0x30),
    (0x4A, 0x38),
    (0x52, 0x48),
)
# (parsed-record offset, raw-record offset) for a 16-bit count.
_COUNT_MAP = (
    (0x28, 0x06),
    (0x2A, 0x1E),
    (0x2C, 0x0E),
    (0x2E, 0x16),
    (0x30, 0x26),
    (0x5A, 0x2E),
    (0x5C, 0x46),
    (0x5E, 0x36),
    (0x60, 0x3E),
    (0x62, 0x4E),
)

def _u16(b,o): return struct.unpack_from('<H', b, o)[0]
def _u32(b,o): return struct.unpack_from('<I', b, o)[0]
def _u64(b,o): return struct.unpack_from('<Q', b, o)[0]

def parse_titan680_tlbg(raw: bytes,
                        bit_depth: int = BIT_DEPTH,
                        thresholds=(CHANNEL_THRESHOLD,) * 4,
                        black_level_stretch: float = BLACK_LEVEL_STRETCH) -> bytes:
    """Translate one Titan680 Tintless-BG client buffer into CamX parsed ABI.

    Surface/Titan680 enters the parser's hardware-version 0x60800 branch, which
    forces flags=3 and consumes 0x50 raw bytes for each of 768 regions.  Sums
    are masked to 34 bits then multiplied by the black-level stretch.  The
    proven front stream has stretch=1.0, making the integer mapping exact.
    """
    if len(raw) < RAW_BYTES:
        raise ValueError(f'raw TL_BG buffer too short: {len(raw)} < {RAW_BYTES}')
    if len(thresholds) != 4:
        raise ValueError('need four channel thresholds')
    out = bytearray(PARSED_FULL_BYTES)
    struct.pack_into('<II', out, 0x00, 3, REGIONS)
    struct.pack_into('<I', out, 0x08, int(bit_depth))
    for i,v in enumerate(thresholds): struct.pack_into('<I', out, 0x0c + 4*i, int(v))
    struct.pack_into('<f', out, 0x1c, float(black_level_stretch))
    for i in range(REGIONS):
        rb = i * RAW_RECORD_BYTES
        pb = PARSED_HEADER_BYTES + i * PARSED_RECORD_BYTES
        for po,ro in _SUM_MAP:
            v = _u64(raw, rb + ro) & SUM_MASK
            # Native code converts masked integer -> float, multiplies, then -> int64.
            # For the validated front contract stretch is exactly 1.0f.
            if black_level_stretch == 1.0:
                z = v
            else:
                z = int(float(v) * float(black_level_stretch))
            struct.pack_into('<Q', out, pb + po, z & 0xffffffffffffffff)
        for po,ro in _COUNT_MAP:
            struct.pack_into('<H', out, pb + po, _u16(raw, rb + ro))
    return bytes(out)

def synthesize_raw_from_bounded_parsed(parsed: bytes) -> bytes:
    """Build one deterministic raw image that forward-parses to `parsed`.

    This is an offline proof adapter, not a production acquisition path.  The
    Windows oracle is intentionally bounded to 0x12bec, so bytes beyond that
    boundary in the final parsed record are unknown and are represented by 0.
    """
    if len(parsed) != PARSED_BOUNDED_BYTES:
        raise ValueError(f'expected bounded parsed object {PARSED_BOUNDED_BYTES:#x} bytes')
    if _u32(parsed,0) != 3 or _u32(parsed,4) != REGIONS:
        raise ValueError('parsed flags/region count drift')
    if _u32(parsed,8) != BIT_DEPTH:
        raise ValueError('parsed bit depth drift')
    if tuple(_u32(parsed,0x0c+4*i) for i in range(4)) != (CHANNEL_THRESHOLD,)*4:
        raise ValueError('parsed channel threshold drift')
    if struct.unpack_from('<f',parsed,0x1c)[0] != BLACK_LEVEL_STRETCH:
        raise ValueError('parsed black-level stretch drift')
    raw = bytearray(RAW_BYTES)
    for i in range(REGIONS):
        rb = i * RAW_RECORD_BYTES
        pb = PARSED_HEADER_BYTES + i * PARSED_RECORD_BYTES
        for po,ro in _SUM_MAP:
            if pb + po + 8 <= len(parsed):
                struct.pack_into('<Q', raw, rb + ro, _u64(parsed, pb + po) & SUM_MASK)
        for po,ro in _COUNT_MAP:
            if pb + po + 2 <= len(parsed):
                struct.pack_into('<H', raw, rb + ro, _u16(parsed, pb + po))
    return bytes(raw)
