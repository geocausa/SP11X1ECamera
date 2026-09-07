#!/usr/bin/env python3
"""Clean-room normal type-0/type-1 CAECXConvergence::GetExposureInfo model.

The model is intentionally the non-null steady history path used by ordinary
RunConvProcesss calls GetExposureInfo(0) and GetExposureInfo(1).
"""
from __future__ import annotations
from dataclasses import dataclass
import math, struct


def f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]

ONE03 = f32(1.03)
RECIP_LOG_ONE03 = f32(1.0 / math.log(ONE03))
RELATIVE_EQUAL_EPS_D = struct.unpack('<d', bytes.fromhex('000000a0f2d77a3e'))[0]
TOL_ONE_GUARD = f32(struct.unpack('<f', struct.pack('<I', 0x3f800001))[0])


def log103_linear(x: float) -> float:
    if x <= 0:
        raise ValueError('history exposure must be positive')
    # DeviceMFT uses a float-returning log helper then multiplies by the shared
    # float32 reciprocal ln(1.03f), finally promoting to double.
    return float(f32(f32(math.log(f32(x))) * RECIP_LOG_ONE03))


def drc_adjust_log(exposure_type: int, drc_gain: float) -> float:
    if exposure_type == 0 and f32(drc_gain) > f32(1.0):
        return log103_linear(f32(drc_gain))
    return 0.0


@dataclass(frozen=True)
class HistoryLane:
    safe_linear: int
    lane_linear: int
    drc_gain_f32: float = 1.0

    def safe_log(self) -> float:
        return log103_linear(float(self.safe_linear))
    def adjusted_lane_log(self, exposure_type: int) -> float:
        return log103_linear(float(self.lane_linear)) + drc_adjust_log(exposure_type, self.drc_gain_f32)


@dataclass(frozen=True)
class GetExposureInfoInputs:
    exposure_type: int                  # normal path: 0 Short or 1 Long
    target_lane_log: float              # convergence +0x20 (t0) / +0x28 (t1)
    target_safe_log: float              # convergence +0x30
    drc_safe_log: float                 # convergence +0xf8, seeded from post-stretch Safe
    history1: HistoryLane               # GetInternalFrameHistory(1)
    history2: HistoryLane               # GetInternalFrameHistory(2)
    drc_speed_f32: float                # ConvBase interpolated core +0x08
    minimum_step_f32: float             # runtime config +0x2c
    tolerance_steps: int                # ConvBase +0x14
    state_flag: int = 0                 # convergence state[type] at +0x2ac+4*type


@dataclass(frozen=True)
class GetExposureInfoResult:
    output_log: float
    target_relative: float
    history_relative: float
    relative_error: float
    history_lane_motion: float
    target_lane_motion: float
    direction_same: bool
    smoothing_applied: bool
    minimum_step_clamped: bool
    snapped_to_target: bool
    candidate_before_final_guards: float
    candidate_after_direction_guard: float
    candidate_after_target_bound: float
    safe_distance_limit: float


def compute(i: GetExposureInfoInputs) -> GetExposureInfoResult:
    t = int(i.exposure_type)
    if t not in (0, 1):
        raise ValueError('BB scopes normal GetExposureInfo types 0 and 1 only')

    h1_lane = i.history1.adjusted_lane_log(t)
    h2_lane = i.history2.adjusted_lane_log(t)
    h1_safe = i.history1.safe_log()

    target_relative = float(i.target_safe_log) - float(i.target_lane_log)
    history_relative = h1_safe - h1_lane
    relative_error = target_relative - history_relative
    near_equal_relative = abs(relative_error) < RELATIVE_EQUAL_EPS_D

    history_motion = h1_lane - h2_lane
    target_motion = float(i.target_lane_log) - h1_lane
    direction_same = (history_motion * target_motion) >= 0.0

    # Default carry-forward path: preserve history's lane-to-safe separation,
    # but anchor it at the current DRC Safe baseline.
    candidate = float(i.drc_safe_log) - history_relative
    smoothing = False
    min_clamped = False

    # 0x1803d1e74..1f68. If the target lane is already within integer tolerance
    # and state[type]==1, Windows bypasses smoothing. Otherwise smoothing occurs
    # only when temporal direction agrees and the relative target actually changed.
    force_carry = (abs(float(i.target_lane_log) - h1_lane) < float(i.tolerance_steps)
                   and int(i.state_flag) == 1)
    if (not force_carry) and direction_same and not near_equal_relative:
        step = float(f32(i.drc_speed_f32)) * relative_error
        min_step = float(f32(i.minimum_step_f32))
        if abs(step) < min_step:
            step = min_step if step > 0.0 else -min_step
            min_clamped = True
        new_relative = history_relative + step
        candidate = float(i.drc_safe_log) - new_relative
        smoothing = True

    # Residual target snap. Since tolerance is integer and must be < 0x3f800001,
    # the useful normal case is tolerance==1.
    snapped = False
    if (abs(candidate - float(i.target_lane_log)) < float(i.tolerance_steps)
            and float(i.tolerance_steps) < float(TOL_ONE_GUARD)):
        candidate = float(i.target_lane_log)
        snapped = True

    before = candidate

    # Final temporal direction gate: do not move the lane opposite the target
    # relative to history. Falling back means retaining the adjusted history lane.
    if (candidate - h1_lane) * (float(i.target_lane_log) - h1_lane) >= 0.0:
        directed = candidate
    else:
        directed = h1_lane

    # Do not overshoot the current target lane.
    if float(i.target_lane_log) - h1_lane > 0.0:
        bounded = min(directed, float(i.target_lane_log))
    else:
        bounded = max(directed, float(i.target_lane_log))

    # Final DRC-Safe distance cap uses the larger magnitude of current target
    # relative separation and previous history relative separation.
    limit = max(abs(target_relative), abs(history_relative))
    if abs(float(i.drc_safe_log) - bounded) > limit:
        bounded = float(i.drc_safe_log) + (limit if bounded > float(i.drc_safe_log) else -limit)

    return GetExposureInfoResult(
        output_log=bounded,
        target_relative=target_relative,
        history_relative=history_relative,
        relative_error=relative_error,
        history_lane_motion=history_motion,
        target_lane_motion=target_motion,
        direction_same=direction_same,
        smoothing_applied=smoothing,
        minimum_step_clamped=min_clamped,
        snapped_to_target=snapped,
        candidate_before_final_guards=before,
        candidate_after_direction_guard=directed,
        candidate_after_target_bound=(min(directed,float(i.target_lane_log)) if float(i.target_lane_log)-h1_lane>0.0 else max(directed,float(i.target_lane_log))),
        safe_distance_limit=limit)
