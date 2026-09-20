#!/usr/bin/env python3
"""Offline E004hg negative checks; no model, camera, runtime or PMIC required."""
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hg_bench",HERE/"benchmark_offline.py")
b=importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
failures=0
for bad in ([1]*7,[1]*9,[],[-1]*8,[1]*7+[1.0],[False]*8):
    try:b.stats(bad)
    except AssertionError:failures+=1
    else:raise AssertionError("E004HG_BAD_TIMING_SAMPLES_ACCEPTED")
assert failures==6
values=[5,40,7,15,9,20,25,10]
record=b.stats(values)
assert record["samples"]==8
assert record["minimum_ms"]==0.0 and record["median_ms"]==0.0
assert record["p95_nearest_rank_ms"]==0.0
assert b.stats([1000000*i for i in range(1,9)])=={
    "samples":8,"minimum_ms":1.0,"median_ms":4.5,
    "p95_nearest_rank_ms":8.0,"maximum_ms":8.0}
result=json.loads((HERE/"evidence/RESULT.json").read_text())
for key in ("native_ir_emitter_authorized",
            "consented_real_user_enrolled_or_authenticated",
            "face_authentication_accuracy_threshold_or_liveness_proven",
            "identical_repeated_input_is_new_capture_or_liveness",
            "new_windows_kd_camera_pmic_led_or_login_activity",
            "physical_led_current_irradiance_fault_off_proven"):
    assert result[key] is False,key
assert result["measured_identical_public_fixture_runs"]==8
assert result["measured_frames_repeated_identical_public_input"] is True
assert result["raw_nv12_bgr_model_features_match_scores_or_identity_logged"] is False
assert result["model_weights_or_raw_public_photo_repacked_in_repo"] is False
print("E004HG_BOUNDED_TIMING_SAMPLE_NEGATIVES=PASS COUNT=6")
print("E004HG_RESULT_NO_AUTH_LIVENESS_REPLAY_FRESHNESS_OR_NATIVE_LED=PASS")
