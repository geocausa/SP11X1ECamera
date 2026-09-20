#!/usr/bin/env python3
"""E004hh: evidence-scope mutations, offline original metadata only."""
from pathlib import Path
import copy,importlib.util,json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hh_result_verify",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
original=json.loads((HERE/"evidence/RESULT.json").read_text())
v.validate(original)
changes=(
    ("original_C_batch_rejects_truncated_or_overlong_input_without_partial_output",False),
    ("original_single_vs_batch_hlos_output_byte_equal",False),
    ("original_C_batch_withholds_all_output_until_all_frames_processed",False),
    ("repeated_fixture_is_not_new_capture_freshness_or_liveness",False),
    ("measured_real_camera_or_dark_nir_frame_rate",True),
    ("real_biometric_authentication_or_enrollment_proven",True),
    ("actual_optical_electrical_fault_off_proven",True),
    ("native_linux_emitter_or_login_modified",True),
    ("windows_kd_camera_pmic_led_or_golden_modified",True),
    ("total_measured_public_frame_model_extractions",8),
    ("benchmark_batch_frames",17),
    ("prior_e004hg_result_sha256","invented-prior-proof"),
)
for key,value in changes:
    bad=copy.deepcopy(original)
    bad[key]=value
    try:v.validate(bad)
    except AssertionError:pass
    else:raise AssertionError("E004HH_SCOPE_MUTATION_ACCEPTED "+key)
bad=copy.deepcopy(original)
bad["timing_ms"]["batch_first_public_feature_ready_ms"]["median_ms"]=-1.0
try:v.validate(bad)
except AssertionError:pass
else:raise AssertionError("E004HH_NEGATIVE_MEDIAN_ACCEPTED")
print("E004HH_EVIDENCE_SCOPE_AND_LATENCY_NEGATIVES=PASS COUNT="+str(len(changes)+1))
print("E004HH_NO_LIVE_IR_CAMERA_BIOMETRIC_OR_PHYSICAL_FAULT_OFF_CLAIMS=PASS")
