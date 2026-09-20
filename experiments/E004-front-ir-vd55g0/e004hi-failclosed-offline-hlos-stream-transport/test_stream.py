#!/usr/bin/env python3
"""E004hi: malformed stream construction/provenance scope, offline only."""
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CLIENT=ROOT/"src/sp11-camera-hlos-worker/sp11-offline-stream-client.py"
spec=importlib.util.spec_from_file_location("e004hi_client_negative",CLIENT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
invalid=(0,17,True,-1,1.0,"1",None)
failures=0
for count in invalid:
    try:mod.OfflineStream("/tmp/nonexistent",count)
    except mod.StreamFault:failures+=1
    else:raise AssertionError("E004HI_INVALID_FRAME_COUNT_ACCEPTED")
assert failures==len(invalid)
for max_seconds in (0,False,-1,121,float("nan")):
    try:mod.OfflineStream("/tmp/nonexistent",1,max_seconds=max_seconds)
    except mod.StreamFault:failures+=1
    else:raise AssertionError("E004HI_INVALID_TIME_LIMIT_ACCEPTED")
assert mod.FRAME_LEN==644*604*3//2 and mod.MAX_FRAMES==16
r=json.loads((HERE/"evidence/RESULT.json").read_text())
assert r["provisional_output_committed_before_exact_DONE_and_child_exit_zero"] is False
assert r["late_session_failure_invalidates_all_previous_provisional_frames"] is True
assert r["independent_host_failure_watchdog_proven"] is False
assert r["real_camera_frame_freshness_near_ir_darkness_or_liveness_proven"] is False
assert r["real_user_enrollment_match_or_login_authorized"] is False
assert r["raw_image_nv12_bgr_embedding_match_scores_saved"] is False
assert r["native_linux_emitter_or_pam_modified"] is False
assert r["windows_kd_camera_pmic_led_or_golden_modified"] is False
assert r["actual_optical_current_pulse_autonomous_fault_off_proven"] is False
print("E004HI_OFFLINE_STREAM_CONSTRUCTOR_AND_TIMEOUT_NEGATIVES=PASS COUNT="+str(failures))
print("E004HI_FAILURE_INVALIDATES_PREVIOUS_PROVISIONAL_FRAMES_NO_NATIVE_IR=PASS")
