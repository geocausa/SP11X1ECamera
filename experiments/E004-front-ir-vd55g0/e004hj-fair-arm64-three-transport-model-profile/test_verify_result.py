#!/usr/bin/env python3
"""E004hj: reject invented performance/biometric conclusions from bounded CPU data."""
from pathlib import Path
import copy
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hj_verify",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
original=json.loads((HERE/"evidence/RESULT.json").read_text())
v.validate(original)
corruptions=(
    ("all_three_modes_c_output_equal_original_single_frame_bytes",False),
    ("each_stream_session_successful_DONE_and_exit0",False),
    ("stream_earlier_output_was_provisional_until_DONE",False),
    ("mode_rotation_measured_rounds",8),
    ("original_identical_public_frame_bytes_per_trial",16),
    ("total_measured_original_yunet_sface_public_feature_extractions",16),
    ("repeated_same_public_visible_light_frame_is_not_a_fresh_camera_stream",False),
    ("real_sp11_illuminated_nir_or_dark_room_recognition_proven",True),
    ("biometric_accuracy_replay_resistance_liveness_enrollment_login_proven",True),
    ("autonomous_host_or_pmic_fault_off_proven",True),
    ("actual_optical_irradiance_or_emitter_current_proven",True),
    ("native_ir_emitter_or_pam_modified",True),
    ("windows_kd_camera_pmic_led_or_golden_modified",True),
    ("raw_image_nv12_bgr_face_feature_match_score_or_identity_saved",True),
)
for name,value in corruptions:
    changed=copy.deepcopy(original)
    changed[name]=value
    try:v.validate(changed)
    except AssertionError:pass
    else:raise AssertionError("E004HJ_UNREJECTED_SCOPE_CORRUPTION "+name)
changed=copy.deepcopy(original)
changed["timing_ms"]["stream"]["first_feature"]["median_ms"]=-1.0
try:v.validate(changed)
except AssertionError:pass
else:raise AssertionError("E004HJ_UNREJECTED_NEGATIVE_STREAM_LATENCY")
changed=copy.deepcopy(original)
changed["timing_ms"]["batch"]["all_eight_features_and_successful_child_exit"]["samples"]=9
try:v.validate(changed)
except AssertionError:pass
else:raise AssertionError("E004HJ_UNREJECTED_INVENTED_BATCH_TRIALS")
print("E004HJ_SAME_SESSION_THREE_MODE_PROVENANCE_NEGATIVES=PASS COUNT="+str(len(corruptions)+2))
print("E004HJ_SIX_PUBLIC_FIXTURE_TRIALS_NOT_BIOMETRIC_OR_PHYSICAL_SAFETY=PASS")
