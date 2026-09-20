#!/usr/bin/env python3
"""E004hr: in-memory negatives forbid turning a bounded alternate no-hit into success."""
from pathlib import Path
import importlib.util,copy,json,zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hr_original",HERE/"verify_result.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
r=json.loads((HERE/"evidence/RESULT.json").read_text())
prep=json.loads((HERE/"evidence/PREPARED.json").read_text())
with zipfile.ZipFile(v.ZIP) as arc:
    raw=arc.read("ORIGINAL-SP7-EARLY-ALTERNATE-SPMI-MASKED-KD.log")
v.verify_log(raw)
v.verify_result(r,prep)
v.static_original()
changes={
    "direct_write_positive_control_hit":False,
    "alt_masked_positive_control_hit":True,
    "alt_masked_timer_address_filtered_hit":True,
    "persistent_alt_masked_timer_breakpoint_active_at_final_manual_pause":False,
    "one_shot_alt_masked_control_still_armed_at_final_manual_pause":False,
    "timer_filter_compares_w2_low16_single_register_ee3e_through_ee41":False,
    "alternate_masked_w4_is_mask_not_byte_count":False,
    "alternate_masked_path_full_bus_sid_or_legacy_real_address_observed":True,
    "alternate_masked_path_comprehensive_absence_proven":True,
    "first_original_idle_timer_byte_0x93_writer_identified":True,
    "physical_silicon_write_current_pulse_autonomous_fault_off_proven":True,
    "all_debugger_breakpoints_load_events_cleared_log_closed_kd_stopped":False,
    "no_windows_camera_preview_manual_pmic_spmi_flash_command_or_debugger_data_write":False,
    "windows_normally_rebooted_to_golden":False,
    "golden_return_boot_id":"fabricated-golden",
    "native_ir_emitter_or_login_modified":True,
    "original_sp7_kd_raw_sha256":"invented-original",
    "direct_positive_control_selector":"0x0001ee3e",
    "fresh_windows_boots_consumed":0,
}
for key,value in changes.items():
    altered=copy.deepcopy(r);altered[key]=value
    try:v.verify_result(altered,prep)
    except AssertionError:pass
    else:raise AssertionError("E004HR_UNREJECTED_FALSE_RESULT "+key)
bad_log=[
    raw+b"modified",
    raw.replace(b"E004HR_DIRECT_WRITE_CONTROL",b"E004HR_DIRECT_CONTROL_NOT_HIT"),
    raw.replace(b"E004HR_FINAL_BOUNDED_ALTERNATE_OBSERVER_CHECK",b"E004HR_EARLY_STOP_MISSING"),
    raw.replace(b"Closing open log file ",b"KD_LOG_NOT_CLOSED "),
]
for item in bad_log:
    try:v.verify_log(item)
    except AssertionError:pass
    else:raise AssertionError("E004HR_ALTERED_ORIGINAL_SP7_LOG_ACCEPTED")
print("E004HR_EVIDENCE_FALSE_POSITIVE_GOLDEN_IR_SCOPE_NEGATIVES=PASS COUNT="+str(len(changes)+len(bad_log)))
print("E004HR_ALT_MASKED_ENTRY_NOT_OBSERVED_FIRST_0X93_WRITER_UNKNOWN=PASS")
