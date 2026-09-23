#!/usr/bin/env python3
"""E004mw source-only *offline* bounded RGB preview brightness planner.

No camera, sensor, V4L2, firmware, network, files, writes, frame pixels
or image hashes. An output is a non-executable scalar experiment plan,
NEVER approval to change a control on the live sensor. A future distinct
single-use physical candidate must supply independent exact native
control readback/ranges, native frame timing and lock/route safety.

Fixed current 30fps SP11 front/rear native modes ONLY. Neither darker
backgrounds nor p01 of optical RAW10 are calibrated black. A median
or spread cannot identify objects, white reference or actual noise.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Literal

PROFILES={
    "front":{
        "baseline":(3546,0,256),"trial":(3546,512,512),
        "active_exposure_max":3550,"active_exposure_min":4,
    },
    "rear":{
        "baseline":(1600,128,1024),"trial":(3200,512,2048),
        "active_exposure_max":3206,"active_exposure_min":4,
    }
}
CONTROL_NAMES=("exposure","analogue_gain","digital_gain")
MIN_GOOD_TRIAL_MEDIAN=90
MAX_GOOD_TRIAL_P99=215
MIN_GOOD_TRIAL_SPREAD=8
MAX_CLIP_FRACTION=0.001
MIN_STABLE_FRAMES=30
MAX_FRAME_INTERVAL_MS=100.0


@dataclass(frozen=True)
class ScalarObservation:
    camera:str
    native_controls:tuple[int,int,int]
    sequence:int
    monotonic_ms:float
    p01_y:int
    p50_y:int
    p99_y:int
    fraction_y_ge235:float
    native_source_fps:float
    source_sequence_gaps:int
    neutral_IR_off:bool
    native_frame_timing_unchanged:bool
    native_sensor_bounds_readback_verified:bool
    exclusive_RGB_route_owner:bool
    ordinary_visible_app_uid:int=1000


@dataclass(frozen=True)
class Plan:
    action:Literal["HOLD","TRIAL_ELIGIBLE","REVERT_ELIGIBLE","BLOCKED"]
    reason:str
    control_profile:Literal["baseline","trial","none"]
    eligible_for_live_control_write:bool=False
    scene_detail_colour_or_sensor_noise_proven:bool=False
    optical_black_calibrated:bool=False


@dataclass
class BrightnessPlanner:
    camera:str
    prior_sequence:int|None=None
    prior_ms:float|None=None
    observed_mode:str|None=None
    stable_frames:int=0
    probed_this_session:bool=False
    baseline_p50:int|None=None
    permanently_blocked:bool=False

    def __post_init__(self)->None:
        if self.camera not in PROFILES:raise ValueError("ONLY_FRONT_REAR_RGB")

    def _blocked(self,why:str)->Plan:
        self.permanently_blocked=True
        self.stable_frames=0
        return Plan("BLOCKED",why,"none")

    def observe(self,s:ScalarObservation)->Plan:
        if self.permanently_blocked:
            return Plan("BLOCKED","PREVIOUS_SOURCE_OR_SENSOR_SAFETY_ERROR","none")
        if s.camera!=self.camera:
            return self._blocked("FRONT_REAR_OR_IR_CAMERA_MISMATCH")
        if (type(s.sequence)!=int or s.sequence<0 or
            type(s.monotonic_ms) not in (float,int) or
            not isfinite(s.monotonic_ms) or not 0<s.monotonic_ms<1.0e12 or
            type(s.native_source_fps) not in (float,int) or
            not isfinite(s.native_source_fps) or
            type(s.source_sequence_gaps)!=int or s.source_sequence_gaps!=0 or
            not 29.0<=s.native_source_fps<=31.5):
            return self._blocked("ACTUAL_SOURCE_FPS_SEQUENCE_OR_TIMESTAMP_INVALID")
        if (s.ordinary_visible_app_uid!=1000 or
            not s.neutral_IR_off or
            not s.native_frame_timing_unchanged or
            not s.native_sensor_bounds_readback_verified or
            not s.exclusive_RGB_route_owner):
            return self._blocked("USER_VISIBLE_ROUTE_IR_NATIVE_BOUNDS_OR_FPS_NOT_VERIFIED")
        if (not isinstance(s.native_controls,tuple) or
            len(s.native_controls)!=3 or
            not all(type(v)==int and v>=0 for v in s.native_controls) or
            s.native_controls not in (PROFILES[self.camera]["baseline"],
                                      PROFILES[self.camera]["trial"])):
            return self._blocked("SENSOR_REGISTER_READBACK_NOT_AN_EXACT_VERIFIED_PROFILE")
        if (type(s.p01_y)!=int or type(s.p50_y)!=int or type(s.p99_y)!=int or
            not 16<=s.p01_y<=s.p50_y<=s.p99_y<=235 or
            type(s.fraction_y_ge235) not in (float,int) or
            not isfinite(s.fraction_y_ge235) or
            not 0<=s.fraction_y_ge235<=1):
            return self._blocked("INVALID_STUDIO_RANGE_SCALAR_HISTOGRAM")
        if self.prior_sequence is not None:
            dt=s.monotonic_ms-self.prior_ms
            if s.sequence!=self.prior_sequence+1 or not 0<dt<=MAX_FRAME_INTERVAL_MS:
                return self._blocked("SOURCE_DROPPED_REPEATED_OR_NON_MONOTONIC")
        self.prior_sequence=s.sequence
        self.prior_ms=s.monotonic_ms
        mode="baseline" if s.native_controls==PROFILES[self.camera]["baseline"] else "trial"
        if self.observed_mode!=mode:
            if self.observed_mode=="trial" and mode=="baseline":
                # A successful, independently read-back restore is legal.
                pass
            elif self.observed_mode=="baseline" and mode=="trial":
                if not self.probed_this_session:
                    return self._blocked("UNREQUESTED_HIGH_GAIN_PROFILE_SWITCH")
            elif self.observed_mode is not None:
                return self._blocked("UNEXPECTED_SENSOR_PROFILE_TRANSITION")
            self.observed_mode=mode
            self.stable_frames=0
        self.stable_frames+=1
        if mode=="baseline":
            if self.probed_this_session:
                return Plan("HOLD","ALREADY_TRIED_KNOWN_PROFILE_ONCE_NO_OSCILLATION","baseline")
            if s.fraction_y_ge235>MAX_CLIP_FRACTION or s.p99_y>=225:
                return Plan("HOLD","BRIGHT_OR_CLIPPED_SCENE_NEVER_INCREASE_GAIN","baseline")
            if s.p50_y>45 or s.p99_y>=75:
                self.stable_frames=0
                return Plan("HOLD","BASELINE_NOT_CONSISTENTLY_DARK","baseline")
            if self.stable_frames<MIN_STABLE_FRAMES:
                return Plan("HOLD","WAIT_FOR_THIRTY_STABLE_REAL_SOURCE_FRAMES","baseline")
            self.baseline_p50=s.p50_y
            self.probed_this_session=True
            self.stable_frames=0
            return Plan("TRIAL_ELIGIBLE",
                "ONE_TIME_ALREADY_PHYSICALLY_TESTED_FIXED_FPS_RGB_PROFILE_ONLY;"
                "NO_SENSOR_WRITE_AUTHORIZED;DARK_OR_LENS_BLOCKED_STILL_UNPROVEN",
                "trial")
        if not self.probed_this_session:
            return self._blocked("TRIAL_READBACK_WITHOUT_PRIOR_SAFELY_OBSERVED_BASELINE")
        if s.fraction_y_ge235>MAX_CLIP_FRACTION or s.p99_y>=225:
            return Plan("REVERT_ELIGIBLE",
                        "OVEREXPOSED_OR_CLIPPING_RESTORE_EXACT_BASELINE_NO_WRITE_AUTHORIZED",
                        "baseline")
        if self.stable_frames<MIN_STABLE_FRAMES:
            return Plan("HOLD","TRIAL_WAIT_THIRTY_STABLE_REAL_FRAMES","trial")
        if (s.p50_y<MIN_GOOD_TRIAL_MEDIAN or
            s.p99_y>MAX_GOOD_TRIAL_P99 or
            s.p99_y-s.p01_y<MIN_GOOD_TRIAL_SPREAD or
            self.baseline_p50 is None or
            s.p50_y-self.baseline_p50<25):
            return Plan("REVERT_ELIGIBLE",
                        "TRIAL_STILL_DARK_FLAT_OR_UNVERIFIED_DISPLAY_QUALITY;"
                        "NO_FURTHER_SENSOR_GAIN_OR_BLACK_LIFT",
                        "baseline")
        return Plan("HOLD",
                    "KNOWN_RGB_TRIAL_HAS_SUSTAINED_DISPLAY_BRIGHTNESS_ONLY;"
                    "NO_PROOF_OF_SCENE_DETAIL_COLOUR_TRUE_SNR_OR_EXPOSURE_CALIBRATION",
                    "trial")
