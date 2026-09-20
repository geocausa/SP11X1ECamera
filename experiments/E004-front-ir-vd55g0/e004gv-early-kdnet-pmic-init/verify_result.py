#!/usr/bin/env python3
"""E004gv: verify original early KD boot and that timer-origin conclusion is INCONCLUSIVE."""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile

HERE=Path(__file__).resolve().parent
RAW_HASH="4c85099f3f02bb0b17c4fc5e15a22061ca1f84b14ca5dbd73f9e9e38c8af8e92"
ZIP=HERE/"evidence/ORIGINAL-SP7-EARLY-KD-20260920.zip"
RESULT=HERE/"evidence/RESULT.json"
PREP=HERE/"evidence/PREPARED.json"

def need(ok,why):
    if not ok:raise AssertionError("E004GV_EVIDENCE_FAIL_CLOSED "+why)

def validate(original,result):
    need(len(original)==12536 and sha256(original).hexdigest()==RAW_HASH,
         "original SP7 KD trace identity")
    need(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",original) is None,
         "KDNET credential in original archive")
    for marker in (
        b"Connected to Windows 10 26100 ARM 64-bit",
        b"E004GV_FIRST_BREAK_NO_CAMERA",
        b"System Uptime: 0 days 0:00:10.839",
        b"E004GV_FIRST_BREAK_MODULE_CHECK_DONE",
        b"E004GV_PRELOAD_CHECK_AFTER_INITIAL_GO",
        b"System Uptime: 0 days 0:00:11.659",
        b"fffff800`11fc0000 fffff800`12019000   qcpmic8380",
        b"E004GV_GENERIC_TIMER_WATCH_ARMED_PRE_DRIVER_START",
        b"E004GV_EARLY_BOOT_TIMER_WRITE_WATCH_RUNNING",
        b"E004GV_END_EARLY_BOOT_OBSERVATION_NO_CAMERA",
        b"E004GV_ALL_KD_BREAKPOINTS_CLEARED",
        b"Closing open log file",
    ):
        need(marker in original,"original early-boot/KD rollback marker "+marker.decode())
    first=original.split(b"E004GV_FIRST_BREAK_NO_CAMERA",1)[1].split(
        b"E004GV_FIRST_BREAK_MODULE_CHECK_DONE",1)[0]
    need(b"qcpmic8380   (deferred)" not in first,
         "PMIC had actually loaded at first initial break")
    second=original.split(b"E004GV_PRELOAD_CHECK_AFTER_INITIAL_GO",1)[1].split(
        b"E004GV_BEFORE_HELPER_CONDITION_ARM",1)[0]
    need(b"qcpmic8380   (deferred)" in second,
         "PMIC second-break transition not observed")
    need(b'(@w2 >= 0xee3e && @w2 <= 0xee41)' in original and
         b" 0 e fffff800`11fe3968" in original,
         "original conditional generic PMIC watcher missing")
    need(re.search(rb"(?m)^E004GV_FIRST_TIMER_MASKED_WRITE\s*$",original) is None,
         "unexpected callback marker - adjust evidence instead of forcing no-hit")
    for key,val in (
        ("experiment","E004gv"),
        ("status","PASS_FRESH_EARLY_KD_PRELOAD_GOLDEN_RETURN_TIMER_WRITER_UNRESOLVED"),
        ("new_windows_boots_consumed",1),
        ("new_oem_camera_sessions",0),
        ("initial_windows_kernel_uptime_seconds",10.839),
        ("second_windows_kernel_uptime_seconds",11.659),
        ("original_masked_write_helper_rva","0x23968"),
        ("one_shot_condition","@w2 >= 0xee3e && @w2 <= 0xee41"),
        ("golden_return_boot_id","0f0b092e-538a-4391-a518-d7eab653f400"),
        ("original_kd_log_sha256",RAW_HASH),
        ("original_kd_log_bytes",12536),
    ):
        need(result[key]==val,"result datum mutated "+key)
    for key in ("pmic_loaded_at_initial_break",
                "first_pmic_driver_entry_intercepted",
                "first_pmic_register_writer_observed",
                "original_kd_log_contains_timer_write_hit_marker",
                "breakpoint_still_listed_at_end",
                "absence_of_timer_writes_during_early_boot_proven",
                "native_ir_emitter_activated",
                "physical_current_irradiance_pulse_fault_off_proven"):
        need(result[key] is False,"unsupported timer/physical claim "+key)
    for key in ("pmic_loaded_at_second_break",
                "one_shot_bp_armed_after_pmic_listed",
                "one_shot_watcher_could_have_been_consumed_by_nonmatching_call",
                "kd_breakpoints_all_cleared_and_log_closed",
                "no_pmic_register_changes_fault_injection_or_camera_preview",
                "golden_kernel_unchanged","golden_saved_entry_unchanged",
                "efi_bootorder_unchanged","bootnext_empty",
                "camera_nodes_modules_and_processes_idle"):
        need(result[key] is True,"missing scope/cleanup "+key)

def main():
    result=json.loads(RESULT.read_text())
    prep=json.loads(PREP.read_text())
    need(prep["state"]=="PREPARED_NOT_EXECUTED" and
         prep["new_windows_boot_consumed"] is False and
         prep["baseline_commit"]=="dcb6e667c260bd52ec24063b27f717b78f85841e" and
         result["baseline_commit"]=="af164ab7dd66f3b5e7839553ad2066293da593ba",
         "preflight evidence drift")
    need(sha256(ZIP.read_bytes()).hexdigest()==result["original_kd_zip_sha256"],
         "original archive changed")
    with zipfile.ZipFile(ZIP) as z:
        need(z.namelist()==["ORIGINAL-SP7-EARLY-KD.log"],"unexpected original log members")
        raw=z.read("ORIGINAL-SP7-EARLY-KD.log")
    validate(raw,result)
    print("E004GV_ORIGINAL_EARLY_KD_PRELOAD_AND_GOLDEN_RETURN=PASS")
    print("E004GV_FIRST_TIMER_WRITER=UNRESOLVED ONE_SHOT_CONDITIONAL_NO_HIT=NOT_PROOF_OF_ABSENCE")

if __name__=="__main__":main()
