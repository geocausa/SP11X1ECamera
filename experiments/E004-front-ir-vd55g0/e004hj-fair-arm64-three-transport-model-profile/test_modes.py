#!/usr/bin/env python3
"""E004hj: reject malformed six-run CPU comparison and false biometric claims."""
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hj_modes",HERE/"benchmark_three.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
failures=0
for bad in ([],[1]*5,[1]*7,[-1]*6,[1]*5+[1.0],[True]*6):
    try:m.summary(bad)
    except AssertionError:failures+=1
    else:raise AssertionError("E004HJ_INVALID_TIMING_LIST_ACCEPTED")
assert failures==6
assert m.summary([1_000_000,2_000_000,3_000_000,
                  4_000_000,5_000_000,6_000_000])=={
    "samples":6,"min_ms":1.0,"median_ms":3.5,
    "p95_nearest_rank_ms":6.0,"max_ms":6.0}
r=json.loads((HERE/"evidence/RESULT.json").read_text())
assert r["experiment"]=="E004hj"
assert r["total_measured_original_yunet_sface_public_feature_extractions"]==144
assert r["repeated_same_public_visible_light_frame_is_not_a_fresh_camera_stream"] is True
for field in ("real_sp11_illuminated_nir_or_dark_room_recognition_proven",
              "biometric_accuracy_replay_resistance_liveness_enrollment_login_proven",
              "autonomous_host_or_pmic_fault_off_proven",
              "actual_optical_irradiance_or_emitter_current_proven",
              "native_ir_emitter_or_pam_modified",
              "windows_kd_camera_pmic_led_or_golden_modified",
              "raw_image_nv12_bgr_face_feature_match_score_or_identity_saved"):
    assert r[field] is False,field
print("E004HJ_THREE_TRANSPORT_CPU_SAMPLE_NEGATIVES=PASS COUNT="+str(failures))
print("E004HJ_SAME_PUBLIC_FRAME_IS_NOT_LIVE_NIR_STREAM_OR_BIOMETRIC_AUTH=PASS")
