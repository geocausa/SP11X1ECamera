#!/usr/bin/env python3
"""E004hh: bounded CPU sample integrity and no-auth/IR claims, offline only."""
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hh_bench",HERE/"benchmark_batch.py")
b=importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
bad=([1]*3,[1]*5,[],[-1]*4,[1]*3+[1.0],[True]*4)
failures=0
for values in bad:
    try:b.timer_summary(values)
    except AssertionError:failures+=1
    else:raise AssertionError("E004HH_INVALID_CPU_TRIAL_COUNT_ACCEPTED")
assert failures==len(bad)
assert b.timer_summary([1_000_000,2_000_000,3_000_000,4_000_000])=={
    "samples":4,"min_ms":1.0,"median_ms":2.5,
    "p95_nearest_rank_ms":4.0,"max_ms":4.0}
r=json.loads((HERE/"evidence/RESULT.json").read_text())
assert r["experiment"]=="E004hh"
assert r["original_C_batch_rejects_truncated_or_overlong_input_without_partial_output"] is True
assert r["original_C_batch_withholds_all_output_until_all_frames_processed"] is True
assert r["repeated_fixture_is_not_new_capture_freshness_or_liveness"] is True
assert r["measured_real_camera_or_dark_nir_frame_rate"] is False
assert r["real_biometric_authentication_or_enrollment_proven"] is False
assert r["actual_optical_electrical_fault_off_proven"] is False
assert r["raw_nv12_bgr_public_crop_embedding_or_scores_persisted"] is False
assert r["native_linux_emitter_or_login_modified"] is False
assert r["windows_kd_camera_pmic_led_or_golden_modified"] is False
print("E004HH_BOUNDED_CPU_SAMPLE_NEGATIVES=PASS COUNT="+str(failures))
print("E004HH_NO_LIVENESS_NEW_CAPTURE_AUTH_OR_NATIVE_IR_CLAIM=PASS")
