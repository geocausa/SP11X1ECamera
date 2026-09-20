#!/usr/bin/env python3
"""E004gy: audit original SP7 hardware raw-write KD transcript, bounded claims."""
from hashlib import sha256
from pathlib import Path
import json
import re
import zipfile

HERE=Path(__file__).resolve().parent
ZIP=HERE/"evidence/ORIGINAL-SP7-RAW-HARDWARE-KD-20260920.zip"
RESULT=HERE/"evidence/RESULT.json"
PREP=HERE/"evidence/PREPARED.json"
RAW_SHA="0b072371f455a8aaa253582fcba3a8af2d85ffd58e9b1c920a5da103f6cf945b"
ZIP_SHA="db55534620b0ac6c5a265a0b8817b031ec0ab4366898fcdf58129f68456f5630"
ENTRIES=re.compile(rb"(?m)^E004GY_HW_RAW_ENTRY start=([0-9a-f]+) len=([0-9a-f]+) caller=([0-9a-f]+)\s*$")

def need(ok,why):
    if not ok:raise AssertionError("E004GY_EVIDENCE_FAIL_CLOSED "+why)

def validate(raw,result,prep):
    need(len(raw)==12263 and sha256(raw).hexdigest()==RAW_SHA,
         "original SP7 raw KD transcript identity")
    need(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",raw) is None,
         "KDNET credential in archived transcript")
    for marker in (b"Connected to Windows 10 26100 ARM 64-bit",
                   b"E004GY_FIRST_EARLY_BOOT_PAUSE",
                   b"E004GY_FRESH_PMIC_LOAD_CHECK",
                   b"E004GY_RAW_HARDWARE_BP_ARMED_AT_DRIVER_LOAD",
                   b"E004GY_FIRST_RAW_HW_BREAK",
                   b"E004GY_MANUAL_FIRST_RAW_HW_CONTROL",
                   b"E004GY_HW_RAW_AUTO_LOG_ARMED",
                   b"E004GY_FINAL_BOUNDED_RAW_WRITE_INSPECTION",
                   b"E004GY_ALL_HW_BREAKPOINTS_CLEARED",
                   b"Closing open log file"):
        need(marker in raw,"original KD event marker missing "+marker.decode())
    need(b"System Uptime: 0 days 0:00:10.935" in raw and
         b"System Uptime: 0 days 0:00:11.756" in raw and
         b"fffff802`20520000 fffff802`20579000   qcpmic8380" in raw,
         "actual pre-load and original PMIC load sequence")
    need(b"qcpmic8380+0x23dc8:" in raw and
         b"ba e1 qcpmic8380+0x23dc8" in raw and
         b"0 e fffff802`20543dc8 e 4" in raw,
         "live ARM64 raw-write helper and hardware execute breakpoint absent")
    need(b"System Uptime: 0 days 0:00:17.902" in raw and
         b"E004GY_FIRST_RAW_HW_BREAK" in raw and
         b"w2=00004716" in raw and b"w4=00000001" in raw and
         b"Bad register error" in raw and b"E004GY_MANUAL_FIRST_RAW_HW_CONTROL" in raw and
         b"lr=fffff80220543a08" in raw and
         b"qcpmic8380+0x23a08" in raw,
         "genuine first nonemitter positive control or manual register-alias correction")
    matches=ENTRIES.findall(raw)
    need(len(matches)==26,"original corrected hardware raw-write entry count")
    need(matches[0]==(b"4716",b"1",b"fffff80220543a08"),
         "first corrected hardware raw entry")
    need({int(n,16) for _,n,_ in matches}=={1},
         "original raw-write byte lengths changed")
    need({c for _,_,c in matches}=={b"fffff80220543a08"},
         "original observed raw-write caller distribution changed")
    need(all(not (int(n,16)>0 and int(a,16)<=0xee41 and
                  int(a,16)+int(n,16)>0xee3e) for a,n,_ in matches),
         "actual original raw write overlaps the timer register range")
    need(b"System Uptime: 0 days 0:00:42.472" in raw and
         b"E004GY_FINAL_ACTIVE_HW_OBSERVER_CONFIRMED" in raw and
         b"bc *; bl" in raw and b"E004GY_ALL_HW_BREAKPOINTS_CLEARED" in raw,
         "original bounded final pause or KD hardware cleanup missing")
    need(prep["experiment"]=="E004gy" and
         prep["status"]=="PREPARED_NEW_RAW_PMIC_WRITE_HARDWARE_KD_NOT_EXECUTED" and
         prep["parent_commit"]=="5918dd3096a2e1afbef4da39e6f5730090ea2d93" and
         prep["new_windows_boot_consumed"] is False and
         prep["native_emitter_authorized"] is False,
         "distinct preboot contract changed")
    need(result["experiment"]=="E004gy" and
         result["status"]=="PASS_FRESH_RAW_PMIC_HARDWARE_EXECUTE_BOUNDED_NO_TIMER_OVERLAP_GOLDEN_RETURN" and
         result["baseline_commit"]=="e348fa720a0c94d266d77106541834a720aed0a3" and
         result["new_windows_boots_consumed"]==1 and
         result["corrected_hardware_raw_helper_entry_records_logged"]==26 and
         result["raw_write_entry_spans_overlapping_ee3e_to_ee41"]==0 and
         result["original_sp7_kd_raw_bytes"]==12263 and
         result["original_sp7_kd_raw_sha256"]==RAW_SHA and
         result["original_sp7_kd_zip_sha256"]==ZIP_SHA and
         result["golden_return_boot_id"]=="836f28b9-850a-486a-9742-7152ebbe23e2",
         "original scoped result, log identity or Golden boot changed")
    for key in ("all_kd_breakpoints_cleared_log_closed_debugger_stopped",
                "normal_windows_reboot_and_golden_return_pass",
                "efi_bootorder_unchanged",
                "uefi_bootnext_and_grub_next_entry_empty",
                "golden_camera_nodes_modules_processes_idle",
                "no_native_linux_ir_emitter_pmic_register_or_login_changes"):
        need(result[key] is True,"original cleanup or hardware no-go changed "+key)
    for key in ("raw_write_alternate_three_direct_callers_observed_in_this_window",
                "all_windows_boot_writers_and_firmware_excluded",
                "first_idle_timer_0x93_origin_identified",
                "autonomous_hardware_fault_cutoff_or_optical_output_proven"):
        need(result[key] is False,"fabricated bypass coverage/timer or optical proof "+key)

def main():
    need(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,
         "original SP7 evidence ZIP changed")
    with zipfile.ZipFile(ZIP) as z:
        need(z.namelist()==["ORIGINAL-SP7-RAW-HARDWARE-KD.log"],
             "unapproved original KD archive members")
        original=z.read("ORIGINAL-SP7-RAW-HARDWARE-KD.log")
    validate(original,json.loads(RESULT.read_text()),json.loads(PREP.read_text()))
    print("E004GY_ORIGINAL_SP7_RAW_HW_KD_POSITIVE_CONTROL=PASS ENTRIES=26")
    print("E004GY_LOGGED_RAW_WRITES_TIMER_SPAN_OVERLAPS=0 OTHER_THREE_CALLERS=UNOBSERVED")
    print("E004GY_GOLDEN_RETURN=PASS FIRST_TIMER_WRITER=UNKNOWN NATIVE_IR=OFF")

if __name__=="__main__":main()
