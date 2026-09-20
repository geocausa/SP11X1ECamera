#!/usr/bin/env python3
"""E004hp: original SP7 KD early SPMI overlapping-timer-span audit.

A real early separate +0x1664 non-timer positive control, a persistent
+0x1660 timer span filter and ZERO matching markers in one BOUNDED window.
The first writer, physical PMIC transfer and autonomous emitter cutoff are
NOT established; the original positive-action syntax error must be retained.
"""
from pathlib import Path
from hashlib import sha256
import json
import re
import zipfile

HERE=Path(__file__).resolve().parent
ZIP=HERE/"evidence/ORIGINAL-SP7-EARLY-SPMI-TIMER-SPAN-KD-20260920.zip"
RAW_SHA="74d5d5b73cc29a96e6fcc7be73dd4b3f02ffe68144bfd6a9e3d5827ae1405472"
ZIP_SHA="a3ec537cd31f8d03f8c764828321584e5feac68482a96533f3d934965a8a8942"
TICK=bytes([96])
FILTER=b"((@w4 > 0) && (@w4 <= 256) && ((@w2 & 0xffff) <= 0xee41) && (((@w2 & 0xffff) + @w4) > 0xee3e))"

def need(ok,msg):
    if not ok:raise AssertionError("E004HP_FAIL_CLOSED "+msg)

def marker(raw,name):
    matches=list(re.finditer(rb"(?m)^"+re.escape(name)+rb"\r?$",raw))
    need(len(matches)==1,"original SP7 marker missing/repeated "+name.decode())
    return matches[0]

def span(raw,start,end):
    first=marker(raw,start).end()
    last=marker(raw,end).start()
    need(first<last,"original SP7 KD marker order changed "+start.decode())
    return raw[first:last]

def check_original_log(raw):
    need(len(raw)==12707 and sha256(raw).hexdigest()==RAW_SHA,
         "original SP7 raw KD log length/hash changed")
    need(re.search(rb"(?i)key=[a-z0-9.]{8,}",raw) is None,
         "KDNET key appeared in original KD archive")
    first=span(raw,b"E004HP_FIRST_PRELOAD_CHECK",
               b"E004HP_SPMI_LOAD_WATCH_ARMED")
    need(b"System Uptime: 0 days 0:00:10.950" in first and
         b"qcspmi8380   (deferred)" not in first and
         b"qcpmic8380   (deferred)" not in first,
         "first KD pause did not precede original PMIC/SPMI module load")
    loaded=span(raw,b"E004HP_SPMI_LOAD_STOP_REASON",
                b"E004HP_MODULE_LOAD_CONFIRMED")
    need(b"System Uptime: 0 days 0:00:11.771" in loaded and
         b"Last event: Load module qcspmi8380.sys at fffff803"+TICK+b"59180000" in loaded and
         b"fffff803"+TICK+b"59180000 fffff803"+TICK+b"59192000   qcspmi8380" in loaded and
         b"fffff803"+TICK+b"59120000 fffff803"+TICK+b"59179000   qcpmic8380" in loaded,
         "early real original driver load/module bases missing")
    first_arm=span(raw,b"E004HP_ORIGINAL_SPMI_TWO_INSTRUCTION_SITES",
                   b"E004HP_PERSISTENT_TIMER_FILTER_ARMED")
    need(b"qcspmi8380+0x1660:" in first_arm and
         b"fffff803"+TICK+b"59181660 d503237f pacibsp" in first_arm and
         b"fffff803"+TICK+b"59181664 a9bb53f3 stp" in first_arm and
         FILTER in first_arm.replace(b"\x08\r\n",b"") and
         b"0 e fffff803"+TICK+b"59181660" in first_arm and
         b"qcspmi8380+0x1660 (Condition:" in first_arm,
         "persistent overlapping-timer filter not active after first module load")
    both=span(raw,b"E004HP_PERSISTENT_TIMER_FILTER_ARMED",
              b"E004HP_EARLY_TWO_INDEPENDENT_HOOKS_ACTIVE")
    need(b"bp /1 qcspmi8380+0x1664" in both and
         b"0 e fffff803"+TICK+b"59181660" in both and
         b"1 e fffff803"+TICK+b"59181664" in both and
         b"/1 0001 (0001) qcspmi8380+0x1664" in both,
         "separate unfiltered original SPMI instruction-site positive control missing")
    control=span(raw,b"E004HP_EARLY_NONTIMER_POSITIVE",
                 b"E004HP_CONTROL_ACTION_SYNTAX_FAIL_MANUAL_RESUME")
    need(b"System Uptime: 0 days 0:00:16.819" in control and
         b"Syntax error in '.echo E004HP_EARLY_NONTIMER_POSITIVE; .time; r x2 x4 lr; gc'" in control and
         b"qcspmi8380+0x1664:" in control and
         b"x2=0000000000019246" in control and
         b"x4=0000000000000001" in control and
         b"lr=2b9d780359143bec" in control and
         b"r x2; r x4; r lr; bl; .echo E004HP_CONTROL_ACTION_SYNTAX_FAIL_MANUAL_RESUME; g" in control and
         b"0 e fffff803"+TICK+b"59181660" in control,
         "positive control actual hit, syntax error, manual recovery and surviving filter not verified")
    fix=span(raw,b"E004HP_FIX_PERSISTENT_ACTION_SYNTAX",
             b"E004HP_CORRECTED_PERSISTENT_TIMER_ACTION_ARMED")
    need(b"System Uptime: 0 days 0:00:30.921" in fix and
         b"bc 0; bp /w" in raw and
         b"r x1; r x2; r x4; r lr; gc" in fix and
         b"0 e fffff803"+TICK+b"59181660" in fix and
         FILTER in fix.replace(b"\x08\r\n",b""),
         "corrected persistent filtered breakpoint not rearmed")
    final=span(raw,b"E004HP_FINAL_BOUNDED_WINDOWS_WINDOW",
               b"E004HP_ALL_HOOKS_CLEARED_NO_CAMERA")
    need(b"System Uptime: 0 days 0:00:58.415" in final and
         b"Last event: Break instruction exception - code 80000003" in final and
         b"0 e fffff803"+TICK+b"59181660" in final and
         b"qcspmi8380+0x1660 (Condition:" in final and
         FILTER in final.replace(b"\x08\r\n",b"") and
         b"r x1; r x2; r x4; r lr; gc" in final and
         b"bc *; sxd ld:qcspmi8380; bl" in raw,
         "active conditional filter at end or debugger cleanup missing")
    need(len(re.findall(rb"(?m)^E004HP_TIMER_SPAN_REQUEST\r?$",raw))==0,
         "observed real timer-span request cannot be reported as a no-hit")
    need(b"Closing open log file" in raw and
         b"E004HP_ALL_HOOKS_CLEARED_NO_CAMERA" in raw,
         "original SP7 KD log close or breakpoint clear missing")

def check_result(r,prepared):
    need(prepared["experiment"]=="E004hp" and
         prepared["status"]==
         "PREPARED_ONE_TIME_FRESH_WINDOWS_EARLY_SPMI_SPAN_FILTER_NOT_YET_EXECUTED" and
         prepared["baseline_commit"]=="fb5bcfbd5815513018367a6a8bee7b81310a716b" and
         prepared["golden_preboot_id"]=="842c0fe1-499b-4eff-88ba-bc5392edddcd" and
         prepared["fresh_windows_boots_consumed"]==0 and
         prepared["timer_filtered_breakpoint_persistent_not_one_shot"] is True and
         prepared["linux_emitter_or_pam_enabled"] is False,
         "fresh original E004hp preboot identity/safety changed")
    need(r["experiment"]=="E004hp" and
         r["status"]==
         "PASS_FRESH_EARLY_SPMI_TIMER_SPAN_WATCH_WITH_NONTIMER_CALLBACK_CONTROL_NO_MATCH_GOLDEN_RETURN" and
         r["prepared_checkpoint"]=="3f51840f46384e3fc09b1a1ef4db6f195a8b0c64" and
         r["new_windows_boots_consumed"]==1 and
         r["previous_experiment_trace_reused"] is False and
         r["first_kd_pause_uptime_seconds"]==10.950 and
         r["spmi_driver_load_uptime_seconds"]==11.771 and
         r["original_spmi_live_base"]=="fffff80359180000" and
         r["original_pmic_live_base"]=="fffff80359120000" and
         r["original_filtered_spmi_entry_rva"]=="0x1660" and
         r["original_independent_callback_control_rva"]=="0x1664" and
         r["positive_control_hit_uptime_seconds"]==16.819 and
         r["positive_control_packed_selector"]=="0x00019246" and
         r["positive_control_payload_bytes"]==1 and
         r["positive_control_original_return_lr_masked_hex"]=="2b9d780359143bec" and
         r["initial_filtered_timer_breakpoint_action_syntax_error_corrected_at_uptime_seconds"]==30.921 and
         r["final_bounded_kernel_uptime_seconds"]==58.415 and
         r["actual_timer_address_span_callback_hit_markers"]==0,
         "original fresh Windows bounded timeline/callback evidence changed")
    for key in (
        "active_persistent_timer_filter_armed_at_driver_load",
        "timer_filter_not_one_shot",
        "timer_filter_matches_low16_address_span_ee3e_to_ee41_count_1_to_256",
        "independent_early_callback_positive_control_hit",
        "positive_control_register_and_byte_count_read_after_auto_action_syntax_error",
        "positive_control_auto_action_syntax_error_occurred",
        "positive_control_syntax_error_paused_original_kernel_transaction_then_manually_resumed",
        "corrected_filter_condition_identical_to_original_installed_condition",
        "persistent_conditional_timer_breakpoint_still_active_at_final_pause",
        "no_camera_preview_manually_issued_flash_spmi_or_pmic_data_writes",
        "temporary_code_breakpoints_arm_and_clear_only",
        "all_breakpoints_cleared_original_sp7_log_closed_kd_stopped",
        "normal_windows_reboot_to_golden","efi_saved_bootorder_unchanged",
        "efi_bootnext_and_grub_next_entry_empty",
        "golden_camera_devices_modules_processes_idle",
    ):need(r[key] is True,"observed debugger/Golden/timer filter scope changed "+key)
    for key in (
        "actual_first_timer_writer_identified",
        "original_raw_lowlevel_timer_callback_complete_absence_proven",
        "original_pmic_physical_bus_completion_proven",
        "optical_electrical_autonomous_emitter_off_proven",
        "native_linux_ir_emitter_or_pam_modified",
    ):need(r[key] is False,"unsupported first-writer/hardware/native-IR claim "+key)
    need(r["golden_return_boot_id"]=="e32d34ba-a422-44cb-a60b-4ff28b583bab" and
         r["golden_kernel"]=="7.1.5-sp11-render-parity-v4+" and
         r["golden_saved_grub"]=="sp11-audio-fullio-v19c" and
         r["original_sp7_kd_raw_bytes"]==12707 and
         r["original_sp7_kd_raw_sha256"]==RAW_SHA and
         r["original_sp7_kd_zip_sha256"]==ZIP_SHA,
         "original SP7 log or independently verified Golden return changed")

def verify():
    need(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,
         "original byte-exact SP7 KD ZIP hash changed")
    with zipfile.ZipFile(ZIP) as archive:
        need(archive.namelist()==["ORIGINAL-SP7-EARLY-SPMI-TIMER-SPAN-KD.log"],
             "unexpected original SP7 KD archive members")
        raw=archive.read(archive.namelist()[0])
    check_original_log(raw)
    check_result(json.loads((HERE/"evidence/RESULT.json").read_text()),
                 json.loads((HERE/"evidence/PREPARED.json").read_text()))
    print("E004HP_REAL_EARLY_SPMI_INDEPENDENT_NONTIMER_ONE_SHOT_POSITIVE=PASS")
    print("E004HP_PERSISTENT_ORIGINAL_SPMI_TIMER_SPAN_NO_OBSERVED_MATCH_TO_58_415S=PASS")
    print("E004HP_ACTION_SYNTAX_ERROR_MANUAL_RECOVERY_AND_NEW_GOLDEN_RETURN_VERIFIED=PASS")
    print("E004HP_NO_FIRST_0X93_WRITER_NO_PHYSICAL_EMITTER_CUTOFF_NATIVE_IR_OFF")

if __name__=="__main__":verify()
