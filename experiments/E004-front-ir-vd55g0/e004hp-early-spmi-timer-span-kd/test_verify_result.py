#!/usr/bin/env python3
"""E004hp: fail-closed original SP7 trace and post-reboot outcome mutations."""
from pathlib import Path
import copy
import importlib.util
import json
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hp_v",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
r=json.loads((HERE/"evidence/RESULT.json").read_text())
pre=json.loads((HERE/"evidence/PREPARED.json").read_text())
with zipfile.ZipFile(v.ZIP) as arc:
    original=arc.read("ORIGINAL-SP7-EARLY-SPMI-TIMER-SPAN-KD.log")
v.check_original_log(original)
v.check_result(r,pre)

changes=(
    ("active_persistent_timer_filter_armed_at_driver_load",False),
    ("timer_filter_not_one_shot",False),
    ("independent_early_callback_positive_control_hit",False),
    ("positive_control_auto_action_syntax_error_occurred",False),
    ("positive_control_syntax_error_paused_original_kernel_transaction_then_manually_resumed",False),
    ("positive_control_packed_selector","0x0001ee3e"),
    ("positive_control_payload_bytes",4),
    ("initial_filtered_timer_breakpoint_action_syntax_error_corrected_at_uptime_seconds",31.0),
    ("final_bounded_kernel_uptime_seconds",59.0),
    ("persistent_conditional_timer_breakpoint_still_active_at_final_pause",False),
    ("actual_timer_address_span_callback_hit_markers",1),
    ("actual_first_timer_writer_identified",True),
    ("original_raw_lowlevel_timer_callback_complete_absence_proven",True),
    ("original_pmic_physical_bus_completion_proven",True),
    ("optical_electrical_autonomous_emitter_off_proven",True),
    ("no_camera_preview_manually_issued_flash_spmi_or_pmic_data_writes",False),
    ("all_breakpoints_cleared_original_sp7_log_closed_kd_stopped",False),
    ("golden_return_boot_id","unverified"),
    ("native_linux_ir_emitter_or_pam_modified",True),
    ("new_windows_boots_consumed",0),
)
for key,value in changes:
    altered=copy.deepcopy(r)
    altered[key]=value
    try:v.check_result(altered,pre)
    except AssertionError:pass
    else:raise AssertionError("E004HP_UNREJECTED_RESULT_MUTATION "+key)

for new in (
    original+b"tampered",
    original.replace(b"E004HP_EARLY_NONTIMER_POSITIVE",
                     b"E004HP_EARLY_CONTROL_NOT_HIT"),
    original.replace(b"E004HP_ALL_HOOKS_CLEARED_NO_CAMERA",
                     b"E004HP_ALL_HOOKS_STILL_ARMED"),
    original.replace(b"0 e fffff803"+v.TICK+b"59181660",
                     b"0 e fffff803"+v.TICK+b"59181664"),
    original.replace(b"E004HP_FINAL_BOUNDED_WINDOWS_WINDOW",
                     b"E004HP_FINAL_BOUNDED_WINDOWS_WINDOW_FAKE"),
):
    try:v.check_original_log(new)
    except AssertionError:pass
    else:raise AssertionError("E004HP_ALTERED_ORIGINAL_SP7_LOG_ACCEPTED")

for key,value in (
    ("status","PREPARED_REUSE"),
    ("fresh_windows_boots_consumed",1),
    ("linux_emitter_or_pam_enabled",True),
):
    altered=copy.deepcopy(pre)
    altered[key]=value
    try:v.check_result(r,altered)
    except AssertionError:pass
    else:raise AssertionError("E004HP_ALTERED_PREBOOT_STATE_ACCEPTED "+key)

print("E004HP_FALSE_TIMER_CUTOFF_KD_CLEANUP_AND_GOLDEN_RESULT_NEGATIVES=PASS COUNT="+str(len(changes)))
print("E004HP_ORIGINAL_SP7_LOG_IMMUTABILITY_NEGATIVES=PASS COUNT=5")
print("E004HP_FRESH_PREBOOT_SCOPE_NEGATIVES=PASS COUNT=3")
print("E004HP_CONTROL_ACTION_SYNTAX_ERROR_AND_MANUAL_RECOVERY_NOT_HIDDEN=PASS")
