#!/usr/bin/env python3
"""E004hn: replay-proof original SP7 KD live SPMI pointer proof; NO TIMER HIT.

Read-only evidence audit. A loaded function pointer cannot establish a callback
invocation, first 0x93 writer, actual bus transaction or physical LED cutoff.
"""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ZIP=HERE/"evidence/ORIGINAL-SP7-READONLY-SPMI-LIVE-INTERFACE-KD-20260920.zip"
RESULT=HERE/"evidence/RESULT.json"
PREP=HERE/"evidence/PREPARED.json"
RAW_SHA="81cf7b9e0655a98902e3f54a1973a1d3a8134077b6a6065a469c96148f059643"
ZIP_SHA="02a616f5719f48f1ecee293707a45cfc4715a548881130839c1c5034bfef6b61"
TICK=bytes([96])
def need(ok,msg):
    if not ok:raise AssertionError("E004HN_EVIDENCE_FAIL_CLOSED "+msg)

def block(raw,start,end):
    def match(name,pos):
        return re.search(rb"(?m)^"+re.escape(name)+rb"\r?$",raw[pos:])
    a=match(start,0)
    need(a is not None,"original KD start marker missing "+start.decode())
    begin=a.end()
    b=match(end,begin)
    need(b is not None,"original KD end marker missing "+end.decode())
    return raw[begin:begin+b.start()]

def previous():
    p=ROOT/"experiments/E004-front-ir-vd55g0/e004hl-original-spmi-raw-write-callback-identity/evidence/RESULT.json"
    r=json.loads(p.read_text())
    need(r["status"]==
         "PASS_ORIGINAL_SPMI_PROVIDER_PLUS_30_CALLBACK_1660_PMIC_INDIRECT_SLOT_IDENTITY_OFFLINE" and
         r["original_provider_consumer_slot"]["pmic_interface_live_callback_and_context_identity_observed"] is False and
         r["native_ir_emitter_authorized"] is False,
         "prior ORIGINAL static callback proof changed")
    return sha256(p.read_bytes()).hexdigest()

def validate(raw,r,prep):
    need(len(raw)==12995 and sha256(raw).hexdigest()==RAW_SHA,
         "SP7 original KD transcript identity/length changed")
    need(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",raw) is None,
         "original KD log contains credential")
    for m in (b"Connected to Windows 10 26100 ARM 64-bit",
              b"E004HN_FIRST_PRELOAD_CHECK",
              b"E004HN_EARLY_PMIC_INTERFACE_READ",
              b"E004HN_EARLY_INTERFACE_COMPLETE",
              b"E004HN_POST_WINDOWS_IDLE_MODULES",
              b"E004HN_POST_IDLE_READ_ONLY_INTERFACE_DONE",
              b"E004HN_ACTUAL_TARGET_DISASSEMBLY",
              b"E004HN_ONE_SHOT_NATURAL_IDLE_NONCAMERA_POSITIVE_ARMED",
              b"E004HN_PASSIVE_IDLE_WINDOW_ENDED_NO_SPMI_ENTRY",
              b"E004HN_ALL_BP_CLEAR_NO_CAMERA",
              b"Closing open log file"):
        need(m in raw,"original KD trace missing "+m.decode())
    initial=block(raw,b"E004HN_FIRST_PRELOAD_CHECK",b"E004HN_FIRST_PAUSE_CHECK_DONE")
    need(b"System Uptime: 0 days 0:00:10.997" in initial and
         b"qcpmic8380   (deferred)" not in initial and
         b"qcspmi8380   (deferred)" not in initial,
         "first kernel debugger pause not before original driver load")
    loaded=block(raw,b"E004HN_STOP_REASON",b"E004HN_EARLY_PMIC_INTERFACE_READ")
    need(b"System Uptime: 0 days 0:00:11.819" in loaded and
         b"fffff803"+TICK+b"3de40000 fffff803"+TICK+b"3de99000   qcpmic8380" in loaded and
         b"Last event: Load module qcpmic8380.sys" in loaded,
         "original PMIC driver load/base unverified")
    early=block(raw,b"E004HN_EARLY_PMIC_INTERFACE_READ",b"E004HN_EARLY_INTERFACE_COMPLETE")
    need(b"qcpmic8380+0x23f1c:" in early and
         b"ldr         x8,[x25,#0x30]" in early and
         b"fffff803"+TICK+b"3de7d040  00000000"+TICK+b"00000000" in early,
         "original PMIC interface callback not zero after initial module load")
    idle=block(raw,b"E004HN_POST_WINDOWS_IDLE_MODULES",b"E004HN_POST_IDLE_READ_ONLY_INTERFACE_DONE")
    need(b"System Uptime: 0 days 0:00:35.654" in idle and
         b"fffff803"+TICK+b"3dea0000 fffff803"+TICK+b"3deb2000   qcspmi8380" in idle and
         b"fffff803"+TICK+b"3de40000 fffff803"+TICK+b"3de99000   qcpmic8380" in idle and
         b"fffff803"+TICK+b"3de7d010  00000000"+TICK+b"00010070" in idle and
         b"fffff803"+TICK+b"3de7d040  fffff803"+TICK+b"3dea1660" in idle,
         "live PMIC+0x3d040 did not point to real SPMI+0x1660")
    target=block(raw,b"E004HN_ACTUAL_TARGET_DISASSEMBLY",
                 b"E004HN_ONE_SHOT_NATURAL_IDLE_NONCAMERA_POSITIVE_ARMED")
    need(b"qcspmi8380+0x1660:" in target and
         b"fffff803"+TICK+b"3dea1660 d503237f pacibsp" in target and
         b"fffff803"+TICK+b"3de7d040  fffff803"+TICK+b"3dea1660" in target and
         b"bp /1 qcspmi8380+0x1660" in raw and
         b"/1 0001 (0001) qcspmi8380+0x1660" in target,
         "actual target disassembly/one-shot idle breakpoint not verified")
    finish=block(raw,b"E004HN_PASSIVE_IDLE_WINDOW_ENDED_NO_SPMI_ENTRY",
                 b"E004HN_ALL_BP_CLEAR_NO_CAMERA")
    need(b"System Uptime: 0 days 0:01:25.089" in finish and
         b"Last event: Break instruction exception - code 80000003" in finish and
         b"/1 0001 (0001) qcspmi8380+0x1660" in finish and
         b"Breakpoint 0 hit" not in raw,
         "no one-shot SPMI hit proved only within bounded idle observation")
    need(b"bc *; sxd ld:qcspmi8380; sxd ld:qcpmic8380; bl" in raw and
         b"E004HN_ALL_BP_CLEAR_NO_CAMERA" in raw and
         b"Closing open log file" in raw,
         "SP7 breakpoint clear and original log closure not established")
    need(prep["status"]==
         "PREPARED_FRESH_READ_ONLY_SPMI_IDENTITY_KD_NOT_YET_EXECUTED" and
         prep["baseline_commit"]=="fd69b89fdb3c4c3e62b8733723f5f317896f8d68" and
         prep["new_windows_boot_consumed"] is False and
         prep["native_ir_or_login_enabled"] is False,
         "fresh E004hn original preboot contract drift")
    need(r["status"]==
         "PASS_FRESH_READ_ONLY_WINDOWS_LIVE_PMIC_SPMI_INTERFACE_CALLBACK_1660_GOLDEN_RETURN_IDLE_NONHIT" and
         r["prepared_checkpoint"]=="1b9525ae82c3fe87ded90b577649b1daeb7facd9" and
         r["fresh_windows_boots_consumed"]==1 and
         r["previous_trace_or_capture_reused"] is False and
         r["pmic_live_base"]=="fffff8033de40000" and
         r["spmi_live_base"]=="fffff8033dea0000" and
         r["pmic_live_interface_callback_slot_rva"]=="0x3d040" and
         r["pmic_live_callback_slot_value"]=="fffff8033dea1660" and
         r["original_spmi_live_callback_resolved_rva"]=="0x1660" and
         r["golden_return_boot_id"]=="de81c0ac-01e1-4fcd-a473-744b5791ffcc" and
         r["original_sp7_log_raw_bytes"]==12995 and
         r["original_sp7_log_raw_sha256"]==RAW_SHA and
         r["original_sp7_log_archive_sha256"]==ZIP_SHA,
         "fresh original Windows callback pointer or Golden restore proof drift")
    for key in ("pmic_interface_early_all_zero",
                "original_loaded_spmi_callback_instructions_disassembled",
                "original_pmic_raw_helper_indirect_slot_load_disassembled",
                "one_shot_non_camera_spmi_callback_breakpoint_armed_after_initialization",
                "breakpoint_entry_event_absent_only_during_bounded_idle_window",
                "no_spmi_positive_control_verified",
                "no_camera_preview_flash_or_pmic_register_write_fault_injection_or_debugger_data_write",
                "temporary_one_shot_software_code_breakpoint_installed_then_cleared",
                "all_kd_breakpoints_cleared_original_log_closed_sp7_kd_stopped",
                "normal_windows_reboot_to_golden",
                "efi_persistent_bootorder_unchanged","efi_bootnext_empty",
                "golden_camera_nodes_modules_processes_idle"):
        need(r[key] is True,"claimed live scope/cleanup changed "+key)
    for key in ("one_shot_natural_idle_spmi_callback_entry_hit_observed",
                "first_writer_of_original_pmic_idle_timer_byte_0x93_identified",
                "actual_bus_sid_or_register_transaction_observed",
                "hardware_register_or_physical_emitter_cutoff_proven",
                "native_linux_ir_or_login_modified"):
        need(r[key] is False,"unsupported actual bus/timer/IR claim "+key)

def main():
    need(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,"archived original SP7 KD ZIP changed")
    with zipfile.ZipFile(ZIP) as z:
        need(z.namelist()==["ORIGINAL-SP7-READONLY-SPMI-LIVE-INTERFACE-KD.log"],
             "original KD log archive members changed")
        raw=z.read(z.namelist()[0])
    validate(raw,json.loads(RESULT.read_text()),json.loads(PREP.read_text()))
    need(previous(),"prior E004hl original OEM source evidence absent")
    print("E004HN_FRESH_ORIGINAL_KD_LIVE_PMIC_SPMI_SLOT_PLUS30_TO_SPMI_PLUS1660=PASS")
    print("E004HN_IDLE_ONESHOT_NO_HIT_NO_93_FIRST_WRITER_NEW_GOLDEN_RETURN=PASS")
    print("E004HN_NO_NATIVE_IR_CAMERA_FLASH_AUTH_OR_PHYSICAL_CUTOFF_PROOF=PASS")

if __name__=="__main__":main()
