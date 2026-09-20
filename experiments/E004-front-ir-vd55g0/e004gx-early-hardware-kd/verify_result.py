#!/usr/bin/env python3
"""Verify E004gx original SP7 hardware KD trace and narrowly bounded claims."""
from hashlib import sha256
from pathlib import Path
import json
import re
import zipfile

HERE=Path(__file__).resolve().parent
ZIP=HERE/"evidence/ORIGINAL-SP7-HARDWARE-KD-20260920.zip"
RESULT=HERE/"evidence/RESULT.json"
PREPARED=HERE/"evidence/PREPARED.json"
RAW_SHA="ba6161d368be4d946e35c82064be2e16f0e87b50ea660e222c685ec1bb620de4"
ZIP_SHA="fc92bc33eda1de05a1378fcc9892804d588ab518a2aad467720476037059eadb"
ACTUAL=re.compile(rb"(?m)^E004GX_HW_RAW_HELPER_REQ w2=([0-9a-f]+) w3=([0-9a-f]+) w4=([0-9a-f]+)\s*$")

def require(ok,reason):
    if not ok:raise AssertionError("E004GX_EVIDENCE_FAIL_CLOSED "+reason)

def span(raw,start,end):
    start_match=re.search(rb"(?m)^"+start+rb"\s*$",raw)
    require(start_match is not None,"missing standalone KD marker "+start.decode())
    end_match=re.search(rb"(?m)^"+end+rb"\s*$",raw[start_match.end():])
    require(end_match is not None,"missing subsequent KD marker "+end.decode())
    return raw[start_match.end():start_match.end()+end_match.start()]

def validate(raw,result,prepared):
    require(len(raw)==13931 and sha256(raw).hexdigest()==RAW_SHA,
            "original SP7 log hash and size")
    require(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",raw) is None,"KDNET key leaked")
    for mark in (b"Connected to Windows 10 26100 ARM 64-bit",
                 b"E004GX_FIRST_BOOT_PAUSE",
                 b"E004GX_MODULE_ADDRESS_READY",
                 b"E004GX_HARDWARE_BREAKPOINT_ARMED_AT_PMIC_LOAD",
                 b"E004GX_MANUAL_HW_FIRST_REAL_TRAP",
                 b"E004GX_HW_RAW_HELPER_BREAKPOINT_REARMED",
                 b"E004GX_FINAL_HARDWARE_BP_WINDOW",
                 b"E004GX_ALL_HW_BP_CLEARED",
                 b"Closing open log file"):
        require(mark in raw,"KD event missing "+mark.decode())
    initial=span(raw,b"E004GX_FIRST_BOOT_PAUSE",b"E004GX_FIRST_PAUSE_CHECK_DONE")
    require(b"System Uptime: 0 days 0:00:10.934" in initial and
            b"qcpmic8380   (deferred)" not in initial,"first KD pause timing/load")
    loaded=span(raw,b"E004GX_SECOND_LOAD_PAUSE_CHECK",b"E004GX_MODULE_ADDRESS_READY")
    require(b"System Uptime: 0 days 0:00:11.756" in loaded and
            b"fffff802`8a000000 fffff802`8a059000   qcpmic8380" in loaded,
            "original PMIC live load time/base")
    armed=span(raw,b"E004GX_MODULE_ADDRESS_READY",
               b"E004GX_HARDWARE_BREAKPOINT_ARMED_AT_PMIC_LOAD")
    require(b"ba e1 qcpmic8380+0x23968" in armed and
            b"0 e fffff802`8a023968 e 4" in armed and
            b"qcpmic8380+0x23968:" in armed,
            "actual live original ARM64 helper and hardware execution watch")
    control=span(raw,b"E004GX_MANUAL_HW_FIRST_REAL_TRAP",
                 b"E004GX_FIRST_TRAP_INSPECTION_DONE")
    for fact in (b"System Uptime: 0 days 0:00:17.847",
                 b"w2=00004716",b"w3=000000ff",b"w4=000000ff",
                 b"qcpmic8380+0x2bd60"):
        require(fact in control,"actual HW exception positive control "+fact.decode())
    require(b"Syntax error in" in raw and
            b"E004GX_HW_RAW_HELPER_BREAKPOINT_REARMED" in raw,
            "initial command parser error must be acknowledged and corrected")
    matches=ACTUAL.findall(raw)
    require(len(matches)==104,"104 actual HW logged generic request entries")
    require(matches[0]==(b"4716",b"ff",b"ff"),
            "original first non-emitter generic entry")
    require(len(set(m[0] for m in matches))==36,
            "original non-timer register distribution changed")
    require(all(not (0xee3e<=int(a,16)<=0xee41) for a,_,_ in matches),
            "actual timer address was observed: cannot claim zero")
    final=span(raw,b"E004GX_FINAL_HARDWARE_BP_WINDOW",b"E004GX_ALL_HW_BP_CLEARED")
    require(b"System Uptime: 0 days 0:00:22.176" in final and
            b"0 e fffff802`8a023968 e 4" in final and
            b"bc *; bl" in raw and
            b"Closing open log file" in raw,
            "watcher active at end and properly disarmed/logged")
    require(prepared["experiment"]=="E004gx" and
            prepared["status"]=="PREPARED_DISTINCT_HARDWARE_EXECUTE_EARLY_KD_NOT_EXECUTED" and
            prepared["new_windows_boot_consumed"] is False and
            prepared["native_linux_emitter_authorized"] is False,
            "preboot authorization/evidence changed")
    require(result["experiment"]=="E004gx" and
            result["status"]=="PASS_FRESH_EARLY_OEM_PMIC_HARDWARE_EXECUTE_POSITIVE_CONTROL_GOLDEN_RETURN" and
            result["baseline_commit"]=="fa6c1ef73fd3e7156598c578671c1e17e1450f91" and
            result["original_sp7_kd_raw_sha256"]==RAW_SHA and
            result["original_sp7_kd_zip_sha256"]==ZIP_SHA and
            result["original_sp7_kd_raw_bytes"]==len(raw) and
            result["fresh_windows_boots_consumed"]==1 and
            result["raw_hardware_execute_helper_entry_records_logged"]==len(matches) and
            result["hardware_logged_ee3e_through_ee41_entry_requests"]==0 and
            result["golden_return_boot_id"]=="ad449a21-86c0-4194-b8a5-e297d750226a",
            "original bounded result/boot identity drift")
    for field in ("positive_control_has_proven_hardware_exec_bp_works_for_this_helper_during_this_session",
                  "selected_helper_no_timer_address_calls_in_logged_104_entries",
                  "kd_breakpoints_explicitly_cleared_log_closed_and_kd_stopped",
                  "normal_windows_reboot_to_golden_linux",
                  "efi_bootorder_unchanged","uefi_bootnext_and_grub_next_entry_empty",
                  "golden_camera_nodes_modules_processes_idle",
                  "no_linux_ir_emitter_pmic_register_or_login_changes"):
        require(result[field] is True,"supported evidence/cleanup changed "+field)
    for field in ("complete_windows_boot_or_other_cores_writer_absence_proven",
                  "pmic_reset_default_or_earliest_timer_register_writer_identified",
                  "hardware_optical_current_irradiance_pulse_or_autonomous_cutoff_proven"):
        require(result[field] is False,"unsupported all-writer/physical claim "+field)

def main():
    require(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,
            "original ZIP raw bytes drift")
    with zipfile.ZipFile(ZIP) as z:
        require(z.namelist()==["ORIGINAL-SP7-HARDWARE-KD.log"],"original trace ZIP members changed")
        original=z.read("ORIGINAL-SP7-HARDWARE-KD.log")
    validate(original,json.loads(RESULT.read_text()),json.loads(PREPARED.read_text()))
    print("E004GX_ORIGINAL_SP7_HARDWARE_BP_POSITIVE_CONTROL=PASS ACTUAL_HELPER_ENTRY_RECORDS=104")
    print("E004GX_SELECTED_HELPER_TIMER_REGISTER_REQUESTS_IN_LOGGED_CALLS=0")
    print("E004GX_FIRST_TIMER_WRITER=UNKNOWN GOLDEN_RETURN=PASS NATIVE_EMITTER=OFF")

if __name__=="__main__":
    main()
