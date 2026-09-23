#!/usr/bin/env python3
"""Offline-only interpretation of verified, sparse SP11 RGB control/RAW scalars.

No camera nodes, controls, image files, boot manipulation, network, frame
data, or policy capable of commanding a live gain/exposure change. Validates
record provenance before reporting exposure headroom and uncalibrated signal.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED = {
    "front": {
        "baseline": {"exposure": 3546, "analogue_gain": 0, "digital_gain": 256},
        "trial": {"exposure": 3546, "analogue_gain": 512, "digital_gain": 512},
    },
    "rear": {
        "baseline": {"exposure": 1600, "analogue_gain": 128, "digital_gain": 1024},
        "trial": {"exposure": 3200, "analogue_gain": 512, "digital_gain": 2048},
    },
}
CHANNELS = ("R", "G0", "G1", "B")
CONTROLS = ("exposure", "analogue_gain", "digital_gain")
REAR_MODE_EXPOSURE_MAX = 3214 - 8  # fixed OV13858 current 4K mode VTS-8
FRONT_ACTIVE_EXPOSURE_MAX = 3554 - 4  # fixed IMX681 frame length-4


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _quantiles(raw: dict[str, Any], camera: str, phase: str) -> dict[str, Any]:
    q = raw["raw10_same_source_sparse_four_bayer_channels"][camera][phase]
    require(set(q) == set(CHANNELS), "INCOMPLETE_OR_UNKNOWN_BAYER_CHANNEL")
    result = {}
    for channel in CHANNELS:
        row = q[channel]
        vals = [row[k] for k in ("p01", "p50", "p95", "p99")]
        require(all(type(x) is int and 0 <= x <= 1023 for x in vals),
                "INVALID_FULL10_RAW_QUANTILES")
        require(vals == sorted(vals), "NONMONOTONIC_FULL10_RAW_QUANTILES")
        require(row["p99_minus_p01"] == vals[-1] - vals[0] and
                row["p50_minus_p01"] == vals[1] - vals[0],
                "INCONSISTENT_RAW_RANGE")
        result[channel] = dict(p01=vals[0], p50=vals[1], p95=vals[2],
                               p99=vals[3], p99_minus_p01=vals[-1]-vals[0])
    return result


def analyze(selector: dict[str, Any], scalars: dict[str, Any]) -> dict[str, Any]:
    require(scalars.get("identity") == "E004mp" and
            selector.get("status") ==
            "PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K",
            "UNSUPPORTED_OR_FAILED_PHYSICAL_RUN")
    require(scalars.get("original_images_or_hashes_exported_or_committed") is False and
            scalars.get("optical_scene_uncontrolled_and_unmatched_windows") is True,
            "UNEXPECTED_IMAGE_PRIVACY_OR_SCENE_PROVENANCE")
    require(set(selector.get("gain_trials", {})) == set(EXPECTED),
            "EXPECTED_TWO_VISIBLE_RGB_SENSOR_TRIALS")
    snapshot = {}
    for camera in ("front", "rear"):
        trial = selector["gain_trials"][camera]
        require(trial.get("camera") == camera and
                trial.get("correct_RGB_subdevice") is True and
                trial.get("driver_supported_v4l2_controls_only") is True and
                trial.get("raw_registers_directly_written") is False and
                trial.get("illumination_or_ir_enabled") is False and
                trial.get("os_system_sleep_used") is False and
                trial.get("pixel_files_saved") is False,
                "RGB_SOURCE_SAFETY_OR_PROVENANCE_NOT_VERIFIED")
        require(trial.get("baseline_controls") == EXPECTED[camera]["baseline"] and
                trial.get("modified_controls") == EXPECTED[camera]["trial"] and
                trial.get("restored_controls") == EXPECTED[camera]["baseline"],
                "NATIVE_CONTROL_CHANGE_OR_RESTORE_NOT_PINNED")
        bounds = trial.get("advertised_sensor_control_bounds", {})
        require(set(bounds) == set(CONTROLS), "INCOMPLETE_NATIVE_CONTROL_RANGES")
        for name in CONTROLS:
            limit = bounds[name]
            require(set(limit) == {"min", "max", "step"} and
                    all(type(limit[k]) is int for k in ("min", "max", "step")) and
                    limit["step"] > 0 and limit["min"] <= limit["max"],
                    "INVALID_NATIVE_CONTROL_BOUNDS")
            for phase in ("baseline", "trial"):
                value = EXPECTED[camera][phase][name]
                require(limit["min"] <= value <= limit["max"] and
                        (value-limit["min"]) % limit["step"] == 0,
                        "CONTROL_VALUE_NOT_SUPPORTED_BY_RECORDED_NATIVE_RANGE")
        active_limit = (FRONT_ACTIVE_EXPOSURE_MAX if camera == "front"
                        else REAR_MODE_EXPOSURE_MAX)
        require(bounds["exposure"]["max"] >= active_limit if camera == "front"
                else bounds["exposure"]["max"] == active_limit,
                "UNEXPECTED_ACTIVE_FRAME_EXPOSURE_ENVELOPE")
        proposed_exposure = EXPECTED[camera]["trial"]["exposure"]
        require(proposed_exposure <= active_limit, "ACTIVE_FRAME_OVERRUN")
        base = _quantiles(scalars, camera, "baseline")
        changed = _quantiles(scalars, camera, "gain")
        g = {}
        for channel in CHANNELS:
            b, a = base[channel], changed[channel]
            g[channel] = dict(
                baseline_p01=b["p01"], trial_p01=a["p01"],
                p01_change=a["p01"]-b["p01"],
                baseline_p99=b["p99"], trial_p99=a["p99"],
                p99_change=a["p99"]-b["p99"],
                baseline_p99_minus_p01=b["p99_minus_p01"],
                trial_p99_minus_p01=a["p99_minus_p01"])
        snapshot[camera] = dict(
            trial_exposure_lines=proposed_exposure,
            maximum_exposure_lines_current_fixed_frame=active_limit,
            remaining_exposure_lines_at_same_frame_timing=active_limit-proposed_exposure,
            higher_exposure_requires_reviewed_vblank_fps_change=True,
            baseline_controls=EXPECTED[camera]["baseline"],
            trial_controls=EXPECTED[camera]["trial"],
            exact_restore_verified=True,
            raw10_channel_quantile_differences=g,
            p01_is_calibrated_optical_black=False,
            spatial_pattern_is_recognizable_scene_detail=False,
            gain_or_noise_quality_assessed=False)
    rear_g0=snapshot["rear"]["raw10_channel_quantile_differences"]["G0"]
    require(rear_g0["trial_p99"]>rear_g0["baseline_p99"] and
            rear_g0["p01_change"] != 0,
            "E004MP_REAR_GAIN_RESPONSE_OR_BLACK_LEVEL_WARNING_NOT_REPRODUCED")
    return {
        "kind": "READ_ONLY_CAMERA_FREE_EXPOSURE_ENVELOPE",
        "source_run": "E004mp",
        "candidate_boot_identity": "CONSUMED_NEVER_REARM",
        "normal_rgb_capture_enabled_or_modified": False,
        "may_write_sensor_controls": False,
        "may_infer_optical_black_from_p01": False,
        "approved_to_raise_gain_or_exposure": False,
        "approved_to_enable_live_auto_exposure_or_tone_mapping": False,
        "approved_to_change_frame_timing_or_fps": False,
        "windows_oracle_comparison_is_matched": False,
        "additional_physical_evidence_required":
            "fixed_visible_lit_scene_and_separate_dark_reference_with_temporal_noise_before_gain_or_tone_policy",
        "cameras": snapshot,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Strict, camera-free, read-only SP11 RGB envelope")
    parser.add_argument("--selector-json",type=Path,required=True)
    parser.add_argument("--scalar-json",type=Path,required=True)
    opts=parser.parse_args()
    # JSON only, no photo inspection, no raw image access and no hardware APIs.
    selector=json.loads(opts.selector_json.read_text())
    scalars=json.loads(opts.scalar_json.read_text())
    print(json.dumps(analyze(selector,scalars),sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
