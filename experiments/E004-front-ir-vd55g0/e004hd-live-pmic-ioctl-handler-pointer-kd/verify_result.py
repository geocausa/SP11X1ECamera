#!/usr/bin/env python3
"""Verify the original SP7 KD live PMIC IOCTL handler-table identity.

Read-only live pointer equality is NOT a record of executing that callback,
a timer-register write, or the independent optical/electrical LED cutoff.
"""
from pathlib import Path
from hashlib import sha256
import json,re,struct,zipfile
import pefile

HERE=Path(__file__).resolve().parent
ZIP=HERE/"evidence/ORIGINAL-SP7-READONLY-PMIC-IOCTL-HANDLER-KD-20260920.zip"
RESULT=HERE/"evidence/RESULT.json"
PREP=HERE/"evidence/PREPARED.json"
RAW_SHA="72d567f1f679d307d59519376e5da56b4f39436aea2f06a254f4506e6afe332a"
ZIP_SHA="aef7253bd5dd1aa0db72e821882f3563fd6d4cf01cc55a00a61bb8d0d775ab22"
PMIC_SHA="756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
PE_ARCHIVE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
BT=bytes([96])

def require(ok,why):
    if not ok:raise AssertionError("E004HD_EVIDENCE_FAIL_CLOSED "+why)

def marker_block(raw,start,end):
    pattern=lambda name:rb"(?m)^"+re.escape(name)+rb"\r?$"
    a=re.search(pattern(start),raw)
    require(a is not None,"missing original KD marker "+start.decode())
    b=re.search(pattern(end),raw[a.end():])
    require(b is not None,"missing later original KD marker "+end.decode())
    return raw[a.end():a.end()+b.start()]

def verify_original_pmic_image():
    paths=list(PE_ARCHIVE.glob("qcpmic8380.inf_*/qcpmic8380.sys"))
    require(len(paths)==1,"original OEM PMIC source ambiguous")
    data=paths[0].read_bytes()
    require(sha256(data).hexdigest()==PMIC_SHA,"original OEM PMIC SHA drift")
    pe=pefile.PE(data=data)
    require(pe.FILE_HEADER.Machine==0xaa64 and
            pe.OPTIONAL_HEADER.ImageBase==0x140000000 and
            struct.unpack("<Q",pe.get_data(0x39500,8))[0]==0x1400285c0,
            "original OEM 0x39470 table slot+0x90 no longer flash handler")
    return PMIC_SHA

def validate(raw,result,prepared):
    require(len(raw)==10284 and sha256(raw).hexdigest()==RAW_SHA,
            "original SP7 KD log byte identity")
    require(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",raw) is None,
            "KDNET secret leaked into archived log")
    for marker in (
        b"Connected to Windows 10 26100 ARM 64-bit",
        b"E004HD_FIRST_PRELOAD_MEMORY_READ_SETUP",
        b"E004HD_SECOND_EARLY_PMIC_LOAD",
        b"E004HD_EARLY_READ_ONLY_HANDLER_POINTER",
        b"E004HD_EARLY_READ_ONLY_CANDIDATE_VTABLE",
        b"E004HD_PASSIVE_WINDOWS_INIT_NO_CAMERA_OR_IOCTL",
        b"E004HD_FINAL_PASSIVE_LIVE_POINTER_READ",
        b"E004HD_LIVE_OBJECT_AND_SLOT_READ_ONLY_PROOF",
        b"E004HD_HANDLER_TARGET_ORIGINAL_CODE_CONFIRMED",
        b"E004HD_BREAKPOINTS_CLEARED",
        b"Closing open log file"):
        require(marker in raw,"KD event missing "+marker.decode())
    first=marker_block(raw,b"E004HD_FIRST_PRELOAD_MEMORY_READ_SETUP",
                       b"E004HD_FIRST_PAUSE_DONE")
    require(b"System Uptime: 0 days 0:00:09.987" in first and
            b"qcpmic8380   (deferred)" not in first,
            "first KD pause was not before original PMIC image load")
    loaded=marker_block(raw,b"E004HD_SECOND_EARLY_PMIC_LOAD",
                        b"E004HD_LIVE_PMIC_BASE_AND_RECEIVER_READY")
    require(b"System Uptime: 0 days 0:00:10.807" in loaded and
            b"fffff803"+BT+b"477a0000 fffff803"+BT+b"477f9000   qcpmic8380" in loaded,
            "original fresh loaded PMIC base changed")
    for opcode in (b"qcpmic8380+0x739c:",b"ldr         x8,[x8,#0x8D8]",
                   b"ldr         x8,[x8,#0x90]"):
        require(opcode in loaded,"live original PMIC indirect dispatch changed")
    early=marker_block(raw,b"E004HD_EARLY_READ_ONLY_HANDLER_POINTER",
                       b"E004HD_EARLY_READ_ONLY_CANDIDATE_VTABLE")
    require(b"fffff803"+BT+b"477db8d8  00000000"+BT+b"00000000" in early,
            "original early live PMIC handler object was not null")
    candidate=marker_block(raw,b"E004HD_EARLY_READ_ONLY_CANDIDATE_VTABLE",
                           b"E004HD_EARLY_KD_POINTER_READ_COMPLETE")
    require(b"fffff803"+BT+b"477d9470  fffff803"+BT+b"477c60b0" in candidate and
            b"fffff803"+BT+b"477d9500  fffff803"+BT+b"477c85c0" in candidate,
            "original candidate table and original +0x90 slot changed")
    final=marker_block(raw,b"E004HD_FINAL_PASSIVE_LIVE_POINTER_READ",
                       b"E004HD_FINAL_POINTER_READ_COMPLETED")
    require(b"System Uptime: 0 days 0:00:26.746" in final and
            b"fffff803"+BT+b"477db8d8  fffff803"+BT+b"477d9470" in final and
            b"fffff803"+BT+b"477d9500  fffff803"+BT+b"477c85c0" in final,
            "original final live handler pointer/slot no longer matches flash table")
    confirmed=marker_block(raw,b"E004HD_LIVE_OBJECT_AND_SLOT_READ_ONLY_PROOF",
                           b"E004HD_HANDLER_TARGET_ORIGINAL_CODE_CONFIRMED")
    require(b"Evaluate expression:" in confirmed and
            b"= fffff803"+BT+b"477d9470" in confirmed and
            b"fffff803"+BT+b"477d9500  fffff803"+BT+b"477c85c0" in confirmed and
            b"qcpmic8380+0x285c0:" in confirmed and
            b"fffff803"+BT+b"477c85c0 d503237f pacibsp" in confirmed,
            "actual verified dereference and live original callback disassembly absent")
    require(b"bc *; bl" in raw and
            b"E004HD_BREAKPOINTS_CLEARED" in raw and
            b"Closing open log file" in raw,
            "KD cleanup and original archive completion missing")
    require(prepared["experiment"]=="E004hd" and
            prepared["status"]=="PREPARED_FRESH_READ_ONLY_ORIGINAL_PMIC_HANDLER_POINTER_KD_NOT_EXECUTED" and
            prepared["parent_commit"]=="ca175860bbdeebe82da7054d779d7554fc8e292d" and
            prepared["new_windows_boot_consumed"] is False and
            prepared["native_ir_enabled"] is False and
            prepared["no_debugger_or_pmic_memory_writes"] is True,
            "fresh original read-only preflight contract changed")
    require(result["experiment"]=="E004hd" and
            result["status"]=="PASS_FRESH_WINDOWS_READ_ONLY_OEM_PMIC_IOCTL_LIVE_HANDLER_TABLE_RESOLVED_GOLDEN_RETURN" and
            result["baseline_commit"]=="3246c060911b9583c052bc6eaa5da31f30f89711" and
            result["fresh_windows_boots_consumed"]==1 and
            result["original_windows_pmic_sha256"]==PMIC_SHA and
            result["original_sp7_kd_raw_bytes"]==10284 and
            result["original_sp7_kd_raw_sha256"]==RAW_SHA and
            result["original_sp7_kd_zip_sha256"]==ZIP_SHA and
            result["golden_return_boot_id"]=="9fe8087b-9476-4ea1-9d26-fda7b59c9828",
            "result scope, original image/log identity or Golden return differs")
    for name in (
        "final_live_slot_was_dereferenced_only_after_nonzero_pointer_verified",
        "final_callback_original_instructions_disassembled_on_live_target",
        "live_pointer_identity_links_original_802f0fc8_dispatch_to_oem_four_channel_callback",
        "no_windows_pmic_register_or_debugger_memory_writes",
        "all_kd_breakpoints_cleared_original_sp7_log_closed_kd_stopped",
        "normal_windows_reboot_to_golden",
        "persistent_efi_bootorder_unchanged",
        "uefi_bootnext_and_grub_next_entry_empty",
        "golden_camera_nodes_modules_processes_idle"):
        require(result[name] is True,"observed live pointer or cleanup changed "+name)
    for name in (
        "previous_windows_or_kd_capture_reused",
        "fresh_windows_camera_ioctl_preview_or_flash_command_executed",
        "four_channel_callback_executed_in_this_read_only_session",
        "original_timer_register_0x93_first_writer_identified",
        "hardware_emission_current_pulse_or_independent_fault_cutoff_proven",
        "native_linux_ir_or_login_modified"):
        require(result[name] is False,"unsupported actual flash/first writer/physical claim "+name)
    require(result["early_live_handler_global_value"]=="0x0" and
            result["final_handler_global_resolved_rva"]=="0x39470" and
            result["final_live_handler_target_oem_pmic_rva"]=="0x285c0" and
            result["final_live_handler_table_slot_offset"]=="0x90",
            "original pointer identity or slot drift")

def main():
    verify_original_pmic_image()
    require(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,"original SP7 ZIP bytes changed")
    with zipfile.ZipFile(ZIP) as z:
        require(z.namelist()==["ORIGINAL-SP7-READONLY-PMIC-IOCTL-HANDLER-KD.log"],
                "unexpected original KD archive members")
        raw=z.read("ORIGINAL-SP7-READONLY-PMIC-IOCTL-HANDLER-KD.log")
    validate(raw,json.loads(RESULT.read_text()),json.loads(PREP.read_text()))
    print("E004HD_ORIGINAL_SP7_LIVE_IOCTL_PMIC_HANDLER_TABLE_IDENTITY=PASS")
    print("E004HD_EARLY_ZERO_FINAL_PMIC_PLUS_39470_SLOT_PLUS_90_TO_PLUS_285C0=PASS")
    print("E004HD_ORIGINAL_FLASH_CALLBACK_NOT_EXECUTED_NO_FIRST_TIMER_WRITER_GOLDEN=PASS")

if __name__=="__main__":main()
