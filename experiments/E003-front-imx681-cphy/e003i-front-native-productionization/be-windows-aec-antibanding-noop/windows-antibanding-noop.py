#!/usr/bin/env python3
"""Clean-room ABI/layout model for the pinned IMX681 metering antibanding gate.

Only the disabled-path identity is modeled. Enabled-branch interpolation is deliberately
left for a later stage because the pinned IMX681 tuning does not authorize/require it.
"""
from dataclasses import dataclass

U32 = 4
F32 = 4
DESC = 8                 # runtime trigger descriptor: two u32 values
SER_VEC = 8              # compact Parameter Bin: count + 32-bit symbol reference
NATIVE_VEC = 16          # ARM64 ABI: count/pad + native pointer

@dataclass(frozen=True)
class BlockLayout:
    compact_size: int
    native_size: int

# Nested adjustment payload:
#   enable, adjustEnable, adjustmentValue, 3 trigger descriptors, interpolation vector.
# Compact: 3*4 + 3*8 + 8 = 0x2c.
# Native:  3*4 + 3*8 = 0x24, align vector to 8 -> 0x28, +0x10 = 0x38.
AUX = BlockLayout(compact_size=0x2C, native_size=0x38)

# ADRC priority: enable + exitFactor + AUX.
ADRC = BlockLayout(compact_size=0x34, native_size=0x40)
# Luma priority: enable + clamp + exit; AUX is 8-byte aligned after the 12-byte header.
LUMA = BlockLayout(compact_size=0x38, native_size=0x48)

COMPACT_ADRC_START = 0x84
NATIVE_ADRC_START = 0xC0
COMPACT_LUMA_START = COMPACT_ADRC_START + ADRC.compact_size
NATIVE_LUMA_START = NATIVE_ADRC_START + ADRC.native_size
COMPACT_TAIL_START = COMPACT_LUMA_START + LUMA.compact_size
NATIVE_TAIL_START = NATIVE_LUMA_START + LUMA.native_size

assert COMPACT_LUMA_START == 0xB8
assert NATIVE_LUMA_START == 0x100
assert COMPACT_TAIL_START == 0xF0
assert NATIVE_TAIL_START == 0x148

# Relevant field mappings within those blocks.
COMPACT_ADRC_ENABLE = 0x84
COMPACT_ADRC_EXIT_FACTOR = 0x88
NATIVE_ADRC_ENABLE = 0xC0
NATIVE_ADRC_EXIT_FACTOR = 0xC4

COMPACT_LUMA_ENABLE = 0xB8
COMPACT_LUMA_CLAMP = 0xBC
COMPACT_LUMA_EXIT = 0xC0
NATIVE_LUMA_ENABLE = 0x100
NATIVE_LUMA_CLAMP = 0x104
NATIVE_LUMA_EXIT = 0x108


def apply_pinned(short: int, long: int, safe: int, *, luma_enable: int = 0,
                 adrc_enable: int = 0) -> tuple[int, int, int]:
    """Pinned IMX681 path: both top-level modifiers are disabled, so identity."""
    if luma_enable or adrc_enable:
        raise ValueError('enabled antibanding branches are outside the BE pinned-path model')
    return short, long, safe
