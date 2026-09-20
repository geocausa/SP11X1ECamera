#!/usr/bin/env python3
"""E004ho: original SP7 KD early-SMPI non-timer positive-control evidence.

One natural software callback on the PMIC masked one-byte write path is proven.
No first 0x93 writer, physical bus completion or autonomous emitter off proven.
"""
from pathlib import Path
from hashlib import sha256
import json
import re
import zipfile
import capstone
import pefile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
ZIP=HERE/"evidence/ORIGINAL-SP7-EARLY-SPMI-CALLBACK-KD-20260920.zip"
RAW_SHA="fdf6a5118cecce073046cfc8382141d2e9b4d4cf2a0aec74a612683fc2af2e39"
ZIP_SHA="b77473cbf7072ca4cafe0b3b48ee574d1f7c0dd4c8ef2aefabc9a6c3fd7bd8e3"
BASE=0x140000000
TICK=bytes([96])
HASHES={
 "qcpmic8380":"756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
 "qcspmi8380":"b6a5868ec2450e713b9a5ada7b4e1a4a77c77427fedf0806fe3eb6541099523c",
}

def need(ok,msg):
    if not ok:raise AssertionError("E004HO_FAIL_CLOSED "+msg)

def original(name):
    paths=list(ARCH.glob(name+".inf_*/"+name+".sys"))
    need(len(paths)==1,"ambiguous original OEM PE "+name)
    raw=paths[0].read_bytes()
    need(sha256(raw).hexdigest()==HASHES[name],"original OEM PE hash drift "+name)
    pe=pefile.PE(data=raw)
    need(pe.FILE_HEADER.Machine==0xaa64 and pe.OPTIONAL_HEADER.ImageBase==BASE,
         "wrong original ARM64 OEM PE "+name)
    return pe

def expect(pe,rva,mn,ops):
    dis=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    ins=list(dis.disasm(pe.get_data(rva,4),BASE+rva))
    need(len(ins)==1 and (ins[0].mnemonic,ins[0].op_str)==(mn,ops),
         "original ARM64 instruction mismatch "+hex(rva))

def original_code_check(pmic,spmi):
    for rva,mn,ops in (
        (0x23ba8,"ldrb","w8, [sp, #0x18]"),
        (0x23bac,"mov","w4, #1"),
        (0x23bb0,"mov","x3, x21"),
        (0x23bb4,"mov","w2, w27"),
        (0x23bb8,"mov","w1, #0"),
        (0x23bbc,"bic","w9, w8, w23"),
        (0x23bc0,"ldrb","w8, [sp, #0x10]"),
        (0x23bc4,"and","w8, w8, w23"),
        (0x23bc8,"orr","w8, w9, w8"),
        (0x23bcc,"strb","w8, [x21]"),
        (0x23bd0,"ldr","x0, [x26, #0x20]"),
        (0x23bd4,"ldr","x8, [x26, #0x30]"),
        (0x23bd8,"mov","x15, x8"),
        (0x23be8,"blr","x15"),
        (0x23bec,"cbz","w0, #0x140023c20"),
    ):expect(pmic,rva,mn,ops)
    for rva,mn,ops in (
        (0x1660,"pacibsp",""),
        (0x1684,"mov","w26, w1"),
        (0x1688,"mov","w21, w2"),
        (0x168c,"mov","x27, x3"),
        (0x1690,"mov","w25, w4"),
    ):expect(spmi,rva,mn,ops)

def marker(raw,name):
    matches=list(re.finditer(rb"(?m)^"+re.escape(name)+rb"\r?$",raw))
    need(len(matches)==1,"KD marker absent or duplicated "+name.decode())
    return matches[0]

def section(raw,start,end):
    a=marker(raw,start).end()
    b=marker(raw,end).start()
    need(a<b,"original KD markers out of order "+start.decode())
    return raw[a:b]

def check_log(raw):
    need(len(raw)==12007 and sha256(raw).hexdigest()==RAW_SHA,
         "original SP7 KD transcript checksum/length drift")
    need(re.search(rb"(?i)key=[a-z0-9.]{8,}",raw) is None,
         "original SP7 transcript contains a KDNET key")
    first=section(raw,b"E004HO_FIRST_PRELOAD_CHECK",b"E004HO_SPMI_LOAD_WATCH_ARMED")
    need(b"System Uptime: 0 days 0:00:10.987" in first and
         b"qcspmi8380   (deferred)" not in first and
         b"qcpmic8380   (deferred)" not in first,
         "earliest pause occurred after original driver load")
    loaded=section(raw,b"E004HO_SPMI_LOAD_OR_STOP_REASON",
                   b"E004HO_LOAD_STOP_CHECK_DONE")
    need(b"System Uptime: 0 days 0:00:11.809" in loaded and
         b"Last event: Load module qcspmi8380.sys at fffff803"+TICK+b"5eba0000" in loaded and
         b"fffff803"+TICK+b"5eba0000 fffff803"+TICK+b"5ebb2000   qcspmi8380" in loaded and
         b"fffff803"+TICK+b"5eb40000 fffff803"+TICK+b"5eb99000   qcpmic8380" in loaded,
         "original SPMI module load and current PMIC/SPMI bases missing")
    armed=section(raw,b"E004HO_EARLY_SPMI_ORIGINAL_ENTRY",
                  b"E004HO_EARLY_ONE_SHOT_ARMED_BEFORE_SPMI_DEVICE_INIT")
    need(b"qcspmi8380+0x1660:" in armed and
         b"fffff803"+TICK+b"5eba1660 d503237f pacibsp" in armed and
         b"/1 0001 (0001) qcspmi8380+0x1660" in armed and
         b"bp /1 qcspmi8380+0x1660" in raw and
         b"r x2; r x4; r lr; gc" in raw,
         "original SPMI module-load one-shot was not armed before device init")
    hit=section(raw,b"E004HO_EARLY_SPMI_CALLBACK_HIT",
                b"E004HO_FIRST_NATURAL_CALLBACK_CLASSIFICATION_DONE")
    need(b"System Uptime: 0 days 0:00:16.243" in hit and
         b"x2=0000000000019246" in hit and
         b"x4=0000000000000001" in hit and
         b"lr=fffff8035eb63bec" in hit,
         "natural early callback hit selector/length/original PMIC return absent")
    caller=section(raw,b"E004HO_FIRST_CALLBACK_CALLER_DISASSEMBLY",
                   b"E004HO_FIRST_NATURAL_CALLBACK_CLASSIFICATION_DONE")
    need(b"qcpmic8380+0x23bd0:" in caller and
         b"fffff803"+TICK+b"5eb63be8 d63f01e0 blr         x15" in caller and
         b"fffff803"+TICK+b"5eb63bec 340001a0 cbz         w0" in caller,
         "live PMIC original raw-function callsite not correlated to hit LR")
    operation=section(raw,b"E004HO_ORIGINAL_CALL_TYPE_AT_FIRST_HIT",
                      b"E004HO_ALL_BPS_CLEARED_AFTER_EARLY_POSITIVE")
    for literal in (b"5eb63bac 52800024 mov         w4,#1",
                    b"5eb63bb4 2a1b03e2 mov         w2,w27",
                    b"5eb63bb8 52800001 mov         w1,#0",
                    b"5eb63bcc 390002a8 strb        w8,[x21]",
                    b"5eb63be8 d63f01e0 blr         x15"):
        need(literal in operation,"live original masked one-byte write path missing")
    need(b"bc *; sxd ld:qcspmi8380" in raw and
         b"E004HO_ALL_BPS_CLEARED_AFTER_EARLY_POSITIVE" in raw and
         b"Closing open log file" in raw,
         "SP7 KD breakpoint clear and log close not verified")

def check_result(r,prep):
    need(prep["experiment"]=="E004ho" and
         prep["status"]=="PREPARED_NOT_YET_EXECUTED" and
         prep["baseline_commit"]=="93471abcc978b93685e2fa71b9633b7dee8d1478" and
         prep["golden_preboot_id"]=="de81c0ac-01e1-4fcd-a473-744b5791ffcc" and
         prep["windows_boot_consumed"] is False and
         prep["native_emitter_enabled"] is False,
         "original E004ho prep/Golden scope changed")
    need(r["experiment"]=="E004ho" and
         r["status"]==
         "PASS_FRESH_EARLY_WINDOWS_SPMI_CALLBACK_NATURAL_NON_TIMER_MASKED_WRITE_PATH_HIT_GOLDEN_RETURN" and
         r["prepared_checkpoint"]=="978457b39624485a241315069c7ba1a4cf662167" and
         r["fresh_windows_boots_consumed"]==1 and
         r["previous_kd_session_or_camera_capture_reused"] is False and
         r["first_sp7_kd_pause_kernel_uptime_seconds"]==10.987 and
         r["spmi_original_module_load_kernel_uptime_seconds"]==11.809 and
         r["first_entry_hit_kernel_uptime_seconds"]==16.243 and
         r["spmi_loaded_module_base"]=="fffff8035eba0000" and
         r["pmic_loaded_module_base"]=="fffff8035eb40000" and
         r["original_spmi_entry_callback_rva"]=="0x1660" and
         r["first_entry_packed_selector"]=="0x00019246" and
         r["selector_high_bus_nibble"]==0 and
         r["selector_sid_nibble"]==1 and
         r["selector_low_16_bit_register"]=="0x9246" and
         r["first_entry_payload_byte_count"]==1 and
         r["first_entry_caller_return_address"]=="fffff8035eb63bec" and
         r["first_entry_original_pmic_caller_return_rva"]=="0x23bec",
         "first SPMI early positive-control context changed")
    packed=int(r["first_entry_packed_selector"],16)
    need(((packed>>20)&15)==r["selector_high_bus_nibble"] and
         ((packed>>16)&15)==r["selector_sid_nibble"] and
         (packed&0xffff)==int(r["selector_low_16_bit_register"],16) and
         not any((packed&0xffff)<=t<(packed&0xffff)+r["first_entry_payload_byte_count"]
                 for t in range(0xee3e,0xee42)),
         "observed non-timer selector falsely decoded")
    for key in (
        "one_shot_breakpoint_armed_at_driver_load_before_normal_init",
        "one_shot_natural_callback_entry_observed",
        "source_original_pmic_caller_prepares_one_byte_masked_write",
        "source_original_pmic_caller_supplies_operation_w1_zero",
        "positive_control_observes_spmi_software_callback_on_non_timer_write_path",
        "one_shot_software_code_breakpoint_temporarily_installed_and_cleared",
        "all_debugger_breakpoints_cleared_original_sp7_log_closed_and_kd_stopped",
        "normal_windows_reboot_to_golden","persistent_efi_bootorder_unchanged",
        "uefi_bootnext_and_grub_next_entry_empty",
        "golden_camera_nodes_modules_and_processes_idle",
    ):need(r[key] is True,"observed positive-control/cleanup fact changed "+key)
    for key in (
        "actual_w1_at_spmi_entry_logged",
        "first_entry_x3_payload_buffer_or_value_logged",
        "callback_first_positive_selector_intersects_timer_addresses_0xee3e_0xee41",
        "controller_mmio_command_or_completion_status_observed_at_first_callback",
        "pmic_silicon_write_or_illumination_physically_measured",
        "first_original_pmic_idle_timer_0x93_writer_identified",
        "independent_physical_emitter_current_irradiance_pulse_or_host_fault_cutoff_proven",
        "fresh_windows_camera_preview_flash_request_debugger_data_or_pmic_register_write",
        "native_linux_ir_emitter_or_login_modified",
    ):need(r[key] is False,"unsupported timer/physical/auth claim "+key)
    need(r["golden_return_boot_id"]=="842c0fe1-499b-4eff-88ba-bc5392edddcd" and
         r["golden_kernel"]=="7.1.5-sp11-render-parity-v4+" and
         r["golden_grub_saved_entry"]=="sp11-audio-fullio-v19c" and
         r["original_sp7_kd_raw_bytes"]==12007 and
         r["original_sp7_kd_raw_sha256"]==RAW_SHA and
         r["original_sp7_kd_zip_sha256"]==ZIP_SHA,
         "new Golden return or original SP7 transcript identity changed")

def verify():
    need(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,
         "archived original SP7 KD ZIP changed")
    with zipfile.ZipFile(ZIP) as archive:
        need(archive.namelist()==["ORIGINAL-SP7-EARLY-SPMI-CALLBACK-KD.log"],
             "original SP7 KD archive contains changed members")
        raw=archive.read(archive.namelist()[0])
    check_log(raw)
    check_result(json.loads((HERE/"evidence/RESULT.json").read_text()),
                 json.loads((HERE/"evidence/PREPARED.json").read_text()))
    original_code_check(original("qcpmic8380"),original("qcspmi8380"))
    print("E004HO_FRESH_EARLY_SPMI_1660_NON_TIMER_0X9246_LEN1_MASKED_WRITE_PATH=PASS")
    print("E004HO_NEW_GOLDEN_RETURN_ORIGINAL_SP7_KD_LOG_NO_KEY=PASS")
    print("E004HO_FIRST_TIMER_93_WRITER_UNKNOWN_NATIVE_IR_OFF")

if __name__=="__main__":verify()
