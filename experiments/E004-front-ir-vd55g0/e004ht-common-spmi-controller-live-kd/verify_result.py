#!/usr/bin/env python3
"""Check original E004ht SP7 KD controller read-positive and timer nonhit."""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile
D=Path(__file__).resolve().parent/"evidence"
Z=D/"ORIGINAL-SP7-EARLY-COMMON-SPMI-CONTROLLER-KD-20260920.zip"
RAW="a439d6073f22f27c707b631d8fd95c2fb21db4225230ccd272816f3412fdb434"
ZIP_SHA="c8e75a196d4eefa4d3fdadb0cf2b66bcea8fa88a4a3dc3aea7a9201c9a2abbe2"
def must(value,reason):
    if not value:raise AssertionError("E004HT_FAIL_CLOSED "+reason)
def scope(r):
    must(r["status"]=="PASS_FRESH_EARLY_WINDOWS_COMMON_SPMI_CONTROLLER_READ_POSITIVE_PERSISTENT_FILTERED_WRITE_TIMER_NONHIT_GOLDEN_RETURN","status")
    expected={"experiment":"E004ht","prepared_checkpoint":"d77226ed44c2fdaafe7b80524e9d518fbceec1ce",
      "fresh_windows_boots_consumed":1,"original_spmi_live_base":"fffff8037b2a0000",
      "original_pmic_live_base":"fffff8037b240000","controller_original_rva":"0x64d8",
      "persistent_filter_armed_at_live_address":"fffff8037b2a64d8",
      "separate_one_shot_positive_hit_kernel_uptime_seconds":12.313,
      "positive_actual_controller_operation_w0":1,"positive_actual_controller_bus_w2":0,
      "positive_actual_controller_sid_w3":0,"positive_actual_controller_register_w4":"0x0100",
      "positive_actual_controller_byte_count_w6":6,"bounded_window_final_kernel_uptime_seconds":92.962,
      "timer_write_marker_count_in_observed_original_log":0,
      "golden_return_boot_id":"b151079f-6d5d-48fa-937a-2b1eff6d992b",
      "original_sp7_kd_raw_bytes":9782,"original_sp7_kd_raw_sha256":RAW,
      "original_sp7_kd_archive_sha256":ZIP_SHA}
    for key,value in expected.items():must(r[key]==value,key)
    for key in ("persistent_filter_arm_at_driver_load","persistent_filter_w0_write_zero",
       "positive_is_controller_software_read_not_write","positive_proves_shared_controller_entry_invoked_in_original_boot",
       "filtered_write_breakpoint_still_enabled_resolved_at_final_manual_pause",
       "debugger_software_code_breakpoints_used_and_disarmed","original_sp7_log_closed_and_kd_stopped",
       "windows_normal_reboot_into_golden","golden_efi_bootorder_unchanged",
       "golden_efi_bootnext_empty","golden_camera_nodes_modules_processes_idle"):
        must(r[key] is True,"true_"+key)
    for key in ("positive_validates_actual_timer_write_predicate","first_original_idle_timer_0x93_writer_identified",
       "spmi_controller_return_or_physical_silicon_completion_observed",
       "real_optical_current_irradiance_pulse_or_autonomous_cutoff_proven",
       "camera_preview_or_manually_requested_pmic_led_register_write",
       "debugger_module_load_exception_filter_explicitly_disabled_before_exit",
       "native_linux_ir_emitter_pam_or_login_modified"):
        must(r[key] is False,"false_"+key)
    must(r["persistent_filter_allowed_byte_count_min_max"]==[1,256],"length_range")
    must(r["persistent_filter_address_low16_overlap_range"]==["0xee3e","0xee41"],"addr_range")
def log(raw):
    must(len(raw)==9782 and sha256(raw).hexdigest()==RAW,"original_sp7_bytes")
    must(not re.search(rb"(?i)key=[a-z0-9.]{8,}",raw),"secret")
    first=raw.find(b"E004HT_FIRST_PRELOAD\r\n")
    load=raw.find(b"E004HT_LOAD_REASON\r\n")
    arm=raw.find(b"E004HT_ORIGINAL_CONTROLLER_LOAD_INSTRUCTIONS\r\n")
    control=raw.find(b"\nE004HT_TWO_CONTROLLER_OBSERVERS_ARMED_BEFORE_NORMAL_INIT\r\n")
    end=raw.find(b"E004HT_COMMON_CONTROLLER_BOUNDED_WINDOW_END\r\n")
    closed=raw.find(b"Closing open log file")
    must(0<first<load<arm<control<end<closed,"order")
    for key in (b"System Uptime: 0 days 0:00:10.967",
       b"System Uptime: 0 days 0:00:11.788",b"System Uptime: 0 days 0:00:12.313",
       b"System Uptime: 0 days 0:01:32.962",
       b"Last event: Load module qcspmi8380.sys at fffff803\x607b2a0000",
       b"fffff803\x607b2a64d8 d503237f pacibsp",
       b"fffff803\x607b2a64dc a9bb53f3 stp",
       b" 0 e fffff803\x607b2a64d8",b" 1 e fffff803\x607b2a64dc",
       b"(@w0 == 0) && (@w6 >= 1) && (@w6 <= 256)",
       b"((@w4 & 0xffff) <= 0xee41)",
       b"(((@w4 & 0xffff) + @w6) > 0xee3e)",
       b"w0=00000001",b"w1=00000000",b"w2=00000000",b"w3=00000000",
       b"w4=00000100",b"w6=00000006",b"bc *; bl; .logclose; g"):
        must(key in raw,"original_marker_"+str(key[:26]))
    window=raw[control:end]
    must(b"E004HT_REAL_CONTROLLER_FIRST_UNFILTERED_POSITIVE" in window,
         "missing_unfiltered_actual_controller_entry")
    must(b"E004HT_REAL_CONTROLLER_TIMER_WRITE_SPAN" not in window,
         "actual_write_timer_marker_present")
    endblock=raw[end:closed]
    must(b" 0 e fffff803\x607b2a64d8" in endblock and
         b" 1 e fffff803\x607b2a64dc" not in endblock,
         "persistent_filtered_breakpoint_not_active_at_end")
def run():
    must(sha256(Z.read_bytes()).hexdigest()==ZIP_SHA,"zip_identity")
    with zipfile.ZipFile(Z) as a:
        must(a.namelist()==["ORIGINAL-SP7-EARLY-COMMON-SPMI-CONTROLLER-KD.log"],"archive_member")
        raw=a.read(a.namelist()[0])
    log(raw)
    scope(json.loads((D/"RESULT.json").read_text()))
    p=json.loads((D/"PREPARED.json").read_text())
    must(p["status"]=="PREPARED_NEW_COMMON_SPMI_CONTROLLER_KD_NOT_EXECUTED" and
         p["preboot_golden_boot_id"]=="a668186f-df85-4238-9983-f7b28455ec84" and
         p["new_windows_boot_consumed"] is False,"preboot_guard")
    print("E004HT_REAL_EARLY_CONTROLLER_READ_POSITIVE_WRITE_TIMER_NONHIT=PASS")
    print("E004HT_FIRST_0X93_WRITER_UNKNOWN_NEW_GOLDEN_PRESERVED=PASS")
if __name__=="__main__":run()
