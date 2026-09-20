#!/usr/bin/env python3
"""E004ht: reject fabricated timer requests, write controls and Golden returns."""
from pathlib import Path
import copy,importlib.util,json,zipfile
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004ht_verify",D/"verify_result.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
r=json.loads((v.D/"RESULT.json").read_text())
with zipfile.ZipFile(v.Z) as z:raw=z.read("ORIGINAL-SP7-EARLY-COMMON-SPMI-CONTROLLER-KD.log")
v.log(raw);v.scope(r)
bad_meta={
 "positive_actual_controller_operation_w0":0,
 "positive_actual_controller_register_w4":"0xee3e",
 "positive_actual_controller_byte_count_w6":1,
 "timer_write_marker_count_in_observed_original_log":1,
 "first_original_idle_timer_0x93_writer_identified":True,
 "positive_validates_actual_timer_write_predicate":True,
 "spmi_controller_return_or_physical_silicon_completion_observed":True,
 "real_optical_current_irradiance_pulse_or_autonomous_cutoff_proven":True,
 "native_linux_ir_emitter_pam_or_login_modified":True,
 "camera_preview_or_manually_requested_pmic_led_register_write":True,
 "filtered_write_breakpoint_still_enabled_resolved_at_final_manual_pause":False,
 "debugger_software_code_breakpoints_used_and_disarmed":False,
 "debugger_module_load_exception_filter_explicitly_disabled_before_exit":True,
 "windows_normal_reboot_into_golden":False,
 "golden_return_boot_id":"invented",
 "golden_efi_bootnext_empty":False,
 "original_sp7_kd_archive_sha256":"invented",
}
for key,value in bad_meta.items():
    bad=copy.deepcopy(r);bad[key]=value
    try:v.scope(bad)
    except AssertionError:pass
    else:raise AssertionError("E004HT_ACCEPTED_FALSE_METADATA_"+key)
bad_raw=[
    raw+b"altered",
    raw.replace(b"w0=00000001",b"w0=00000000"),
    raw.replace(b"w4=00000100",b"w4=0000ee3e"),
    raw.replace(b"E004HT_ACTIVE_TIMER_BREAKPOINT_CHECK_DONE",
                b"E004HT_TIMER_FILTER_WAS_DISABLED"),
    raw.replace(b"bc *; bl; .logclose; g",b"no_breakpoint_cleanup"),
]
for i,bad in enumerate(bad_raw):
    try:v.log(bad)
    except AssertionError:pass
    else:raise AssertionError("E004HT_ACCEPTED_ALTERED_SP7_ORIGINAL_"+str(i))
print("E004HT_FALSE_TIMER_IR_SCOPE_GOLDEN_NEGATIVES=PASS COUNT="+str(len(bad_meta)))
print("E004HT_ORIGINAL_SP7_LOG_MUTATION_NEGATIVES=PASS COUNT="+str(len(bad_raw)))
