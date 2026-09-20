#!/usr/bin/env python3
"""E004gw: pin original SP7 KD transcript and scoped, persistent-breakpoint result.

Only original Windows software-helper entry requests could have been observed;
this does not verify PMIC silicon state, pre-first-pause firmware or optical safety.
"""
from pathlib import Path
from hashlib import sha256
import json
import re
import zipfile

HERE=Path(__file__).resolve().parent
ZIP=HERE/"evidence/ORIGINAL-SP7-PRELOAD-KD-20260920.zip"
PREP=HERE/"evidence/PREPARED.json"
RESULT=HERE/"evidence/RESULT.json"
RAW_SHA="1c6d5a603f00c0b5d53f316abcb686a6d9b3b7f30a9542d30b17f997fb3c25a2"
ZIP_SHA="4292b7150cd0c90459463d1f443a42ec872609736683fb970be48589f038da0b"
STANDALONE=lambda name:rb"(?m)^"+name+rb"\s*$"
ACTIVE=rb"(?m)^\s*0 e fffff803`037e3968\s+0001 \(0001\) qcpmic8380\+0x23968 \(Condition: \(@w2 >= 0xee3e && @w2 <= 0xee41\)\)"

def require(cond,why):
    if not cond:raise AssertionError("E004GW_ORIGINAL_EVIDENCE_FAIL_CLOSED "+why)

def block(raw,name,nextname=None):
    match=re.search(STANDALONE(name.encode()),raw)
    require(match is not None,"missing actual standalone KD marker "+name)
    tail=raw[match.end():]
    if nextname:
        end=re.search(STANDALONE(nextname.encode()),tail)
        require(end is not None,"missing next standalone KD marker "+nextname)
        return tail[:end.start()]
    return tail

def validate(raw,meta,prep):
    require(len(raw)==14502 and sha256(raw).hexdigest()==RAW_SHA,
            "original SP7 KD transcript changed")
    require(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",raw) is None,
            "KDNET credential unexpectedly present")
    for token in (
        b"Connected to Windows 10 26100 ARM 64-bit",
        b"E004GW_FIRST_PRELOAD_PAUSE",
        b"E004GW_DEFERRED_PERSISTENT_WATCH_ARMED_PRE_PMIC_LOAD",
        b"E004GW_SECOND_EARLY_KD_VERIFY",
        b"E004GW_RESOLVED_PERSISTENT_TIMER_WATCH_ACTIVE_BEFORE_RESUME",
        b"E004GW_FINAL_PERSISTENT_WATCH_INSPECTION_NO_CAMERA",
        b"E004GW_FINAL_INSPECTION_DONE",
        b"E004GW_ALL_KD_BP_DISARMED",
        b"Closing open log file",
    ):
        require(token in raw,"original KD marker missing "+token.decode())
    first=block(raw,"E004GW_FIRST_PRELOAD_PAUSE",
                "E004GW_INITIAL_MODULE_AND_BREAKPOINT_CHECK")
    require(b"System Uptime: 0 days 0:00:10.948" in first and
            b"qcpmic8380   (deferred)" not in first,
            "first KD break must precede PMIC module listing")
    pending=block(raw,"E004GW_INITIAL_MODULE_AND_BREAKPOINT_CHECK",
                  "E004GW_DEFERRED_PERSISTENT_WATCH_ARMED_PRE_PMIC_LOAD")
    require(b"bu /w" in pending and b"/1 /w" not in pending and
            b"0 eu" in pending and b"qcpmic8380+0x23968" in pending and
            b"@w2 >= 0xee3e && @w2 <= 0xee41" in pending,
            "preload symbolic pending watch was not persistent or properly filtered")
    second=block(raw,"E004GW_SECOND_EARLY_KD_VERIFY",
                 "E004GW_MUST_REPAIR_SYMBOLIC_PENDING_HOOK")
    require(b"System Uptime: 0 days 0:00:11.770" in second and
            b"fffff803`037c0000 fffff803`03819000   qcpmic8380" in second and
            re.search(ACTIVE,second) is not None,
            "original helper breakpoint did not resolve at second pause")
    final=block(raw,"E004GW_FINAL_PERSISTENT_WATCH_INSPECTION_NO_CAMERA",
                "E004GW_FINAL_INSPECTION_DONE")
    require(b"System Uptime: 0 days 0:00:50.272" in final and
            re.search(ACTIVE,final) is not None,
            "persistent filtered breakpoint was not active at final pause")
    require(re.search(STANDALONE(b"E004GW_REAL_TIMER_MASKED_CALL"),raw) is None,
            "genuine matching timer-register caller occurred: result must be revised")
    cleanup=block(raw,"E004GW_FINAL_INSPECTION_DONE",
                  "E004GW_ALL_KD_BP_DISARMED")
    require(b"bc *; bl" in raw and
            re.search(rb"(?m)^\s*0 e fffff803`037e3968",cleanup) is None,
            "original breakpoint cleanup not evidenced")
    require(prep["experiment"]=="E004gw" and
            prep["status"]=="PREPARED_NEW_EARLY_PERSISTENT_SYMBOLIC_TIMER_WATCH_NOT_EXECUTED" and
            prep["baseline_commit"]=="8b2fcff0bc4446c68a78acc4e392f8dba696a393" and
            prep["new_windows_boot_consumed"] is False and
            prep["persistent_breakpoint_required_for_valid_no_hit_conclusion"] is True and
            prep["native_ir_emitter_authorized"] is False,
            "original preboot experiment contract changed")
    require(meta["experiment"]=="E004gw" and
            meta["status"]=="PASS_FRESH_PRELOAD_PERSISTENT_MASKED_TIMER_WATCH_NO_MATCH_GOLDEN_RETURN" and
            meta["baseline_commit"]=="59651262968f908e53ddcaed1fae2c041ce21198" and
            meta["new_windows_boots_consumed"]==1 and
            meta["new_oem_camera_preview_sessions"]==0 and
            meta["original_kd_log_sha256"]==RAW_SHA and
            meta["original_kd_log_bytes"]==len(raw) and
            meta["original_zip_sha256"]==ZIP_SHA,
            "completed stage or original trace identity changed")
    for k in (
        "deferred_persistent_bp_armed_at_initial_preload_pause",
        "breakpoint_resolved_active_at_second_pause",
        "breakpoint_still_resolved_active_at_final_pause",
        "bounded_post_resolution_selected_helper_no_matching_requests_observed",
        "kd_bp_cleared_log_closed_and_debugger_stopped",
        "no_camera_pmic_write_or_fault_injection",
        "saved_fullio_v19c_unchanged","efi_bootorder_unchanged",
        "bootnext_and_grub_next_entry_empty",
        "golden_camera_nodes_modules_processes_idle",
    ):
        require(meta[k] is True,"missing original scoped/rollback evidence "+k)
    for k in (
        "pmic_module_loaded_at_first_pause","breakpoint_one_shot_option_used",
        "deferred_hook_resolved_before_first_pmic_driver_entry_proven",
        "pre_first_kd_pause_timer_writes_excluded",
        "all_pmic_timer_writers_or_uefi_firmware_excluded",
        "actual_first_timer_register_writer_identified",
        "windows_timer_register_value_during_this_boot_measured",
        "physical_led_current_irradiance_pulse_or_fault_cutoff_proven",
        "native_linux_ir_emitter_enabled",
    ):
        require(meta[k] is False,"unverified broad or hardware claim "+k)
    require(meta["first_kd_break_windows_kernel_uptime_s"]==10.948 and
            meta["second_break_windows_kernel_uptime_s"]==11.770 and
            meta["windows_kernel_uptime_final_pause_s"]==50.272 and
            meta["original_log_actual_matching_timer_request_markers"]==0 and
            meta["golden_return_boot_id"]=="e305fe1c-0bd9-407d-bf8c-e56a19354b7e",
            "time window, hit count or Golden boot id changed")

def main():
    require(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,
            "original ZIP file changed")
    with zipfile.ZipFile(ZIP) as z:
        require(z.namelist()==["ORIGINAL-SP7-PRELOAD-KD.log"],
                "original archive unexpectedly contains extra members")
        original=z.read("ORIGINAL-SP7-PRELOAD-KD.log")
    validate(original,json.loads(RESULT.read_text()),json.loads(PREP.read_text()))
    print("E004GW_ORIGINAL_PRELOAD_PERSISTENT_TIMER_WATCH=PASS")
    print("E004GW_SELECTED_HELPER_EE3E_TO_EE41_NO_MATCH_BOUNDED=PASS FIRST_TIMER_WRITER=UNKNOWN")
    print("E004GW_GOLDEN_RETURN=PASS NATIVE_IR=OFF PHYSICAL_SHUTDOWN=UNVERIFIED")

if __name__=="__main__":main()
