#!/usr/bin/env python3
"""Clean-room model of the non-null steady-state Windows AEC BasicSafe kernel.

This deliberately stops before ConvStretch / DRCStretchAggregator / settle logic.
The function consumes values after Windows has already selected/interpolated the
request-local ConvBase node.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import struct


def f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]


ONE03_F32 = f32(struct.unpack('<f', struct.pack('<I', 0x3F83D70A))[0])
FLOAT_EPS_GUARD = f32(struct.unpack('<f', struct.pack('<I', 0x33D6BF95))[0])
TOL_ONE_GUARD = f32(struct.unpack('<f', struct.pack('<I', 0x3F800001))[0])


@dataclass(frozen=True)
class BasicSafeInputs:
    target_safe_log: float
    previous_safe_log: float          # GetInternalFrameHistory(1), history +0x78
    previous2_safe_log: float         # GetInternalFrameHistory(2), history +0x78
    delayed_safe_log: float           # GetInternalFrameHistory(cameraContext+0x8ec), +0x78
    previous_delta_f32: float         # history(1) +0x17c
    pipeline_delay: int               # camera/context byte +0x8ec
    base_speed_f32: float             # interpolated ConvBase core +0x00
    base_capping_f32: float           # interpolated ConvBase core +0x04
    drc_speed_f32: float              # interpolated ConvBase core +0x08 (reported, not used here)
    capping_type: int                 # request-local ConvBase +0x18
    tolerance_steps: int              # request-local ConvBase +0x14
    minimum_step_f32: float           # convergence runtime/config +0x2c
    intolerance_gate: bool = False    # runtime +0x2b4 == 1
    small_delta_exemption: bool = False  # virtual state query(arg=3) == 1


@dataclass(frozen=True)
class BasicSafeResult:
    output_log: float
    lanes: tuple[float, ...]
    target_delta: float
    delayed_delta: float
    temporal_motion: float
    candidate_step: float
    capping_step: float
    selected_step: float
    applied_step: float
    direction_ok: bool
    skipped_for_intolerance: bool
    snapped_to_target: bool
    minimum_step_clamped: bool

    def as_dict(self):
        d = asdict(self)
        d['lanes'] = list(self.lanes)
        return d


def _f32_absdiff(a: float, b: float) -> float:
    # Mirrors FCVT-to-S + FSUB + FABS in the DeviceMFT guard.
    return f32(abs(f32(f32(a) - f32(b))))


def compute_basic_safe(i: BasicSafeInputs) -> BasicSafeResult:
    if i.pipeline_delay <= 0:
        raise ValueError('pipeline_delay must be positive on the non-null steady path')

    prev_delta = f32(i.previous_delta_f32)
    base_speed = f32(i.base_speed_f32)
    base_capping = f32(i.base_capping_f32)
    _ = f32(i.drc_speed_f32)  # part of the same core tuple, used downstream not in BasicSafe step.
    minimum_step = f32(i.minimum_step_f32)

    target_delta = float(i.target_safe_log) - float(i.previous_safe_log)
    delayed_delta = float(i.target_safe_log) - float(i.delayed_safe_log)
    temporal_motion = float(i.previous_safe_log) - float(i.previous2_safe_log)
    direction_ok = (temporal_motion * target_delta) >= 0.0

    # 0x1803ce934..0x1803ce9d8: explicit "Skip safe convergence" branch.
    if (abs(target_delta) < float(i.tolerance_steps)
            and i.intolerance_gate
            and abs(prev_delta) <= 0.0):
        out = float(i.previous_safe_log)
        return BasicSafeResult(
            output_log=out, lanes=(out,)*7,
            target_delta=target_delta, delayed_delta=delayed_delta,
            temporal_motion=temporal_motion,
            candidate_step=0.0, capping_step=0.0, selected_step=0.0,
            applied_step=0.0, direction_ok=direction_ok,
            skipped_for_intolerance=True, snapped_to_target=False,
            minimum_step_clamped=False)

    # Interpolated ConvBase core tuple is float32, promoted to double for the step math.
    candidate = float(base_speed) * target_delta

    # 0x1803ce9e4..0x1803cea4c: three Windows capping modes.
    if i.capping_type == 0:
        cap = float(base_capping) * delayed_delta
    elif i.capping_type == 1:
        sign = -1.0 if target_delta < 0.0 else 1.0
        cap = sign * float(base_capping)
    else:
        cap = delayed_delta / float(i.pipeline_delay)

    # 0x1803cea50..0x1803cea6c: fabs both and keep the lower-magnitude signed step.
    step = cap if abs(candidate) > abs(cap) else candidate
    snapped = False

    # If the prospective residual falls inside the request-local tolerance and the
    # float32 delta changed, Windows snaps exactly to target. 0x3f800001 makes this
    # branch possible only for integer tolerance 0 or 1.
    changed_from_previous_delta = _f32_absdiff(step, prev_delta) >= FLOAT_EPS_GUARD
    if (changed_from_previous_delta
            and float(i.tolerance_steps) < TOL_ONE_GUARD
            and abs(float(i.target_safe_log) - (step + float(i.previous_safe_log))) < float(i.tolerance_steps)):
        step = target_delta
        snapped = True

    # 0x1803ceac4..0x1803ceb40: enforce runtime minimum step while outside that
    # threshold, except for the exact small-delta/history-match exemption.
    min_clamped = False
    if abs(step) < float(minimum_step) and abs(target_delta) > float(minimum_step):
        history_match = _f32_absdiff(step, prev_delta) < FLOAT_EPS_GUARD
        if not (i.small_delta_exemption and history_match):
            step = float(minimum_step) if step > 0.0 else -float(minimum_step)
            min_clamped = True

    # 0x1803ceb44..0x1803ceb64: direction reversal suppresses convergence update.
    applied = step if direction_ok else 0.0
    out = float(i.previous_safe_log) + applied
    return BasicSafeResult(
        output_log=out, lanes=(out,)*7,
        target_delta=target_delta, delayed_delta=delayed_delta,
        temporal_motion=temporal_motion,
        candidate_step=candidate, capping_step=cap, selected_step=step,
        applied_step=applied, direction_ok=direction_ok,
        skipped_for_intolerance=False, snapped_to_target=snapped,
        minimum_step_clamped=min_clamped)
