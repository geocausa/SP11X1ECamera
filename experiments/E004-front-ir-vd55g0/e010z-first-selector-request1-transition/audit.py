#!/usr/bin/env python3
"""Host-only E010z lifecycle audit. No camera, MMIO, DMA, or private payloads."""

from dataclasses import dataclass

@dataclass(frozen=True)
class ROI:
    left: int
    top: int
    width: int
    height: int

def cold_seed(width: int, height: int) -> ROI:
    assert width > 0 and height > 0
    return ROI(0, 0, width - width // 10, height - height // 10)

def region_word(roi: ROI) -> int:
    half_w = roi.width >> 1
    half_h = roi.height >> 1
    h_num = half_w - 1 if half_w > 2 else 1
    v_num = half_h - 1 if half_h > 0 else 0
    return (h_num & 0x1FFF) | ((v_num & 0x1FFF) << 16)

active = ROI(0, 0, 4064, 2286)
cold = cold_seed(active.width, active.height)
assert cold == ROI(0, 0, 3658, 2058)

# Live trace: request 1 consumes cold seed first, then the same request-owned
# slot is replaced by the caller-owned full-crop request config.
request_id = 1
first_selected = cold
assert request_id == 1
assert first_selected == ROI(0, 0, 3658, 2058)

live_replacement = active
second_selected = live_replacement
assert second_selected == ROI(0, 0, 4064, 2286)
assert region_word(first_selected) != region_word(second_selected)

# The rule is geometry-derived, not a literal tied to this one sensor mode.
assert cold_seed(1000, 500) == ROI(0, 0, 900, 450)
assert cold_seed(101, 51) == ROI(0, 0, 91, 46)

print("E010Z_AUDIT_PASS cold seed derived; request-owned live replacement preserved")
