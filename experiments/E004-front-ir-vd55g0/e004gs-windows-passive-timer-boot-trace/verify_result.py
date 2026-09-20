#!/usr/bin/env python3
"""E004gs immutable original KD trace + Golden-return evidence verifier, offline."""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
ZIP=HERE/"evidence/ORIGINAL-SP7-KD-20260920.zip"
RESULT=HERE/"evidence/RESULT.json"
EXPECTED_TRACE="2d8f43c76e426b491f894184342f499cc5ad6dd2597295ee3a749555d35fb571"

def require(ok,why):
    if not ok:raise AssertionError("E004GS_EVIDENCE_FAIL_CLOSED "+why)

def validate(log,result):
    require(sha256(log).hexdigest()==EXPECTED_TRACE,"original SP7 KD trace bytes changed")
    require(len(log)==10792,"original trace length mismatch")
    require(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",log) is None,"KD key leaked into trace")
    for exact in (
        b"Connected to Windows 10 26100 ARM 64-bit",
        b"qcpmic8380+0x26d50:",
        b"qcpmic8380+0x26f30:",
        b"qccamflash8380+0x4dd0:",
        b"E004GS_PASSIVE_BREAKPOINTS_READY",
        b"E004GS_PASSIVE_IDLE_END_NO_CAMERA",
        b"E004GS_PASSIVE_ALL_KD_BP_CLEARED",
    ):
        require(exact in log,"original KD marker absent "+exact.decode())
    require(log.count(b"E004GS_PASSIVE_ALL_KD_BP_CLEARED")>=1,
            "breakpoint disarm record missing")
    require(re.search(rb"(?m)^\s*[012] e fffff800",log) is not None,
            "live one-shot timer breakpoints not armed")
    for tag in (b"E004GS_TIMER4_ENTER",b"E004GS_TIMER1_ENTER",b"E004GS_FLASH_TIMER_ENTER"):
        # The breakpoint command text appears in the source/list listing.
        # Only a marker at the beginning of a line is an actual callback hit.
        require(re.search(rb"(?m)^"+tag+rb"\s*$",log) is None,
                "a passive callback did hit "+tag.decode())
    require(result["experiment"]=="E004gs" and
            result["status"]=="PASS_FRESH_PASSIVE_WINDOWS_KD_BOOT_AND_RETURN_TO_GOLDEN",
            "experiment/result drift")
    require(result["prior_consumed_e004gb_repeated"] is False and
            result["windows_new_boot_count"]==1 and
            result["one_shot_timer_breakpoints_armed"]==3 and
            result["passive_idle_timer_breakpoint_hits"]==
               {"timer4":0,"timer1":0,"flash_timer_helper":0},
            "bounded passive observation drift")
    for tag in ("breakpoints_armed_only_after_windows_boot",
                "no_oem_camera_preview_intentionally_started",
                "kd_breakpoints_all_cleared","sp7_kd_closed",
                "golden_kernel_unchanged","uefi_bootorder_unchanged",
                "golden_saved_entry_unchanged","camera_nodes_processes_modules_idle"):
        require(result[tag] is True,tag+" proof drift")
    for tag in ("first_windows_boot_init_timer_requests_excluded",
                "any_windows_background_hello_emission_physically_proven_absent",
                "linux_native_emitter_activated",
                "physical_led_current_irradiance_or_autonomous_fault_off_proven"):
        require(result[tag] is False,tag+" invalid scope claim")
    require(result["original_windows_trace_sha256"]==EXPECTED_TRACE and
            result["original_windows_trace_bytes"]==len(log) and
            result["linux_golden_return_boot_id"]==
               "bbb9ef1b-f1e5-4024-a636-44b5cc67c5a6",
            "postboot or original trace identity drift")

def main():
    result=json.loads(RESULT.read_text())
    require(sha256(ZIP.read_bytes()).hexdigest()==result["archived_trace_sha256"],
            "original archive byte drift")
    with zipfile.ZipFile(ZIP) as package:
        require(package.namelist()==["ORIGINAL-SP7-KD.log"],"archive members changed")
        raw=package.read("ORIGINAL-SP7-KD.log")
    validate(raw,result)
    print("E004GS_ARCHIVED_ORIGINAL_SP7_KD_AND_PASSIVE_ZERO_HIT=PASS")
    print("E004GS_GOLDEN_RETURN_EVIDENCE=PASS ORIGINAL_TIMER_INIT_DURING_EARLY_BOOT=NOT_EXCLUDED")
    print("NATIVE_IR=OFF CAMERA_PREVIEW_INTENTIONALLY_STARTED=NO E004GB_REPEAT=NO")

if __name__=="__main__":main()
