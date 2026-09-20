#!/usr/bin/env python3
"""Verify original SP7 E004hb KD log without inferring unobserved callback calls."""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile

HERE=Path(__file__).resolve().parent
ZIP=HERE/"evidence/ORIGINAL-SP7-GENERIC-KD-20260920.zip"
RESULT=HERE/"evidence/RESULT.json"
PREP=HERE/"evidence/PREPARED.json"
RAW_SHA="9a92d9ff07fd4d9876385edb05a8e9978f15774fdba24e941d3898b3fc645b9d"
ZIP_SHA="d98e9658cc41af8a39618c5dd427f3fc30d86c1eeb553fa6a45f8f0e6e17c0e8"
BT=bytes([96])

def require(ok,why):
    if not ok:raise AssertionError("E004HB_FAIL_CLOSED "+why)

def between(raw,start,end):
    needle=lambda x:rb"(?m)^"+re.escape(x)+rb"\r?$"
    a=re.search(needle(start),raw)
    require(a is not None,"missing original marker "+start.decode())
    b=re.search(needle(end),raw[a.end():])
    require(b is not None,"missing next original marker "+end.decode())
    return raw[a.end():a.end()+b.start()]

def validate(raw,result,prep):
    require(len(raw)==10463 and sha256(raw).hexdigest()==RAW_SHA,
            "original SP7 raw log bytes")
    require(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",raw) is None,
            "KD secret present")
    for marker in (b"Connected to Windows 10 26100 ARM 64-bit",
                   b"E004HB_FIRST_PRELOAD_CHECK",
                   b"E004HB_SECOND_EARLY_PAUSE",
                   b"E004HB_LIVE_CODE_CHECK_DONE",
                   b"E004HB_THREE_HARDWARE_HOOKS_ARMED",
                   b"Too many data breakpoints for processor 0",
                   b"E004HB_HW_SLOT_LIMIT_RECOVERY",
                   b"E004HB_TWO_HW_HOOKS_ARMED",
                   b"E004HB_BOUNDED_TWO_SLOT_HARDWARE_SESSION_RUNNING",
                   b"E004HB_FINAL_BOUNDED_WINDOW",
                   b"E004HB_ALL_HW_BREAKPOINTS_CLEARED",
                   b"Closing open log file"):
        require(marker in raw,"original KD event missing "+marker.decode())
    first=between(raw,b"E004HB_FIRST_PRELOAD_CHECK",b"E004HB_FIRST_PAUSE_DONE")
    require(b"System Uptime: 0 days 0:00:10.969" in first and
            b"qcpmic8380   (deferred)" not in first,
            "original first predriver pause")
    second=between(raw,b"E004HB_SECOND_EARLY_PAUSE",b"E004HB_PMIC_LIVE_PRE_ARM_CHECK")
    require(b"System Uptime: 0 days 0:00:11.791" in second and
            b"fffff803"+BT+b"a6220000 fffff803"+BT+b"a6279000   qcpmic8380" in second,
            "live OEM PMIC load")
    for name in (b"qcpmic8380+0x2f918:",b"qcpmic8380+0x2fdd0:",b"qcpmic8380+0x32b70:"):
        require(name in raw,"live original code not disassembled "+name.decode())
    failed=between(raw,b"E004HB_THREE_HARDWARE_HOOKS_ARMED",
                   b"E004HB_HW_SLOT_LIMIT_RECOVERY")
    require(b"Too many data breakpoints for processor 0" in failed and
            b"bp2 at fffff803"+BT+b"a6252b70 failed" in failed,
            "three-HW-breakpoint CPU limit not documented")
    require(b"E004HB_TWO_HW_HOOKS_ARMED" in raw and
            b"E004HB_BOUNDED_TWO_SLOT_HARDWARE_SESSION_RUNNING" in raw,
            "corrected two-breakpoint continuation missing")
    for pattern in (rb"(?m)^E004HB_GENERIC_WRITER_ENTER reg=",
                    rb"(?m)^E004HB_GENERAL_DESCRIPTOR_HIT\r?$",
                    rb"(?m)^E004HB_4A_DESCRIPTOR_HIT\r?$"):
        require(re.search(pattern,raw) is None,
                "real callback hit occurred; result needs revision")
    final=between(raw,b"E004HB_FINAL_BOUNDED_WINDOW",
                  b"E004HB_FINAL_HW_INSPECTION_DONE")
    require(b"System Uptime: 0 days 0:00:34.451" in final and
            b" 0 e fffff803"+BT+b"a6252b70 e 4" in final and
            b" 1 e fffff803"+BT+b"a624f918 e 4" in final and
            b"a624fdd0" not in final,
            "final two-HW-watch state changed")
    require(b"bc *; bl" in raw and b"E004HB_ALL_HW_BREAKPOINTS_CLEARED" in raw and
            b"Closing open log file" in raw,
            "KD hook/log teardown not recorded")
    require(prep["experiment"]=="E004hb" and
            prep["status"]=="PREPARED_NEW_EARLY_GENERIC_CALLBACK_HARDWARE_KD_NOT_EXECUTED" and
            prep["parent_commit"]=="2d469a1e09b10c15ed8592b90797bc45ec64ff36" and
            prep["new_windows_boot_consumed"] is False and
            prep["native_linux_ir_enabled"] is False,
            "original fresh-identity preparation drift")
    require(result["experiment"]=="E004hb" and
            result["status"]=="PASS_BOUNDED_EARLY_GENERIC_HARDWARE_KD_NO_RECORDED_HITS_INCONCLUSIVE_GOLDEN_RETURN" and
            result["baseline_commit"]=="0812f3c92cc065dbdd81ff6eaac9908d0bf95fbb" and
            result["fresh_windows_boots_consumed"]==1 and
            result["original_sp7_kd_raw_bytes"]==10463 and
            result["original_sp7_kd_raw_sha256"]==RAW_SHA and
            result["original_sp7_kd_zip_sha256"]==ZIP_SHA and
            result["golden_return_boot_id"]=="91e918f6-a800-4a6a-9511-78cbc275a07c",
            "original result, log or Golden identity drift")
    for key in ("third_hardware_breakpoint_programming_failed",
                "recovered_after_failed_three_breakpoint_go",
                "two_hardware_breakpoints_active_after_rearm",
                "final_two_hardware_breakpoints_confirmed_active",
                "all_kd_breakpoints_cleared_original_log_closed_kd_stopped",
                "normal_windows_reboot_to_golden",
                "efi_bootorder_unchanged","bootnext_and_grub_next_entry_empty",
                "golden_camera_nodes_modules_and_processes_idle",
                "no_windows_camera_preview_or_fault_injection",
                "no_native_linux_ir_emitter_pmic_register_or_login_changes"):
        require(result[key] is True,"original state/teardown drift "+key)
    for key in ("three_hardware_breakpoints_simultaneously_installed_in_cpu",
                "type_0x4a_descriptor_monitored_during_bounded_boot",
                "hardware_callback_positive_control_obtained_this_session",
                "no_generic_callback_executed_anywhere_proven",
                "physical_led_current_irradiance_pulse_or_autonomous_fault_off_proven"):
        require(result[key] is False,"unsupported all-caller or physical claim "+key)
    require(result["actual_hw_observer_rvas_during_boot"]==["0x32b70","0x2f918"] and
            result["generic_writer_entry_hit_markers"]==0 and
            result["general_descriptor_entry_hit_markers"]==0 and
            result["effective_available_hardware_execute_slots_in_this_session"]==2,
            "observed two-slot coverage changed")

def main():
    require(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,"original ZIP bytes changed")
    with zipfile.ZipFile(ZIP) as z:
        require(z.namelist()==["ORIGINAL-SP7-GENERIC-KD.log"],"unexpected archive members")
        original=z.read("ORIGINAL-SP7-GENERIC-KD.log")
    validate(original,json.loads(RESULT.read_text()),json.loads(PREP.read_text()))
    print("E004HB_ORIGINAL_SP7_TWO_HW_KD_AND_THREE_SLOT_FAILURE=PASS")
    print("E004HB_NO_CALLBACK_MARKER=INCONCLUSIVE WITHOUT_POSITIVE_CONTROL")
    print("E004HB_GOLDEN_RETURN=PASS NATIVE_IR=OFF TIMER_WRITER=UNKNOWN")

if __name__=="__main__":main()
