#!/usr/bin/env python3
"""E004hf: isolate original OEM flash alternate timer-arming start callers.

Offline on original SHA-pinned ARM64 drivers only; this excludes an original
FLASH HELPER as a direct writer of 0x93, not earlier/indirect/firmware sources.
"""
from pathlib import Path
from hashlib import sha256
import json
import struct
import pefile
import capstone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
FLASH_HASH="6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b"
PMIC_HASH="756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
BASE=0x140000000
START_RVA=0x48c8
TIMER_RVA=0x4dd0
DIRECT_START_CALLERS=[0x6638,0x6a20]
DIRECT_TIMER_CALLERS=[0x4938,0x5b2c]

def require(ok,why):
    if not ok:raise AssertionError("E004HF_FAIL_CLOSED "+why)

def image(name,digest):
    paths=list(ARCH.glob(name+".inf_*/"+name+".sys"))
    require(len(paths)==1,"original OEM image ambiguous "+name)
    raw=paths[0].read_bytes()
    require(sha256(raw).hexdigest()==digest,"original OEM image hash drift "+name)
    pe=pefile.PE(data=raw)
    require(pe.FILE_HEADER.Machine==0xaa64 and pe.OPTIONAL_HEADER.ImageBase==BASE,
            "wrong original OEM Windows ARM64 image")
    return pe

def instruction(pe,rva):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    matches=list(cs.disasm(pe.get_data(rva,4),BASE+rva))
    require(len(matches)==1,"missing OEM instruction "+hex(rva))
    return matches[0].mnemonic,matches[0].op_str

def expect(pe,rva,mn,operands):
    require(instruction(pe,rva)==(mn,operands),
            "changed OEM instruction "+hex(rva))

def callers(pe,rva):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    cs.skipdata=True
    found=[]
    for sec in pe.sections:
        if not sec.Characteristics&0x20000000:continue
        for ins in cs.disasm(sec.get_data(),BASE+sec.VirtualAddress):
            if (ins.mnemonic=="bl" and ins.op_str.startswith("#") and
                int(ins.op_str[1:],16)==BASE+rva):
                found.append(ins.address-BASE)
    return sorted(found)

def original_route(flash,pmic):
    require(callers(flash,START_RVA)==DIRECT_START_CALLERS,
            "alternate start direct caller set changed")
    require(callers(flash,TIMER_RVA)==DIRECT_TIMER_CALLERS,
            "flash timer helper direct caller set changed")
    # Independent operation start routine: current -> timer -> strobe,
    # with distinct error gates. This is not subtype-0 dispatch itself.
    for rva,mn,args in (
        (0x48c8,"pacibsp",""),
        (0x492c,"bl","#0x140004ce0"),
        (0x4938,"bl","#0x140004dd0"),
        (0x4954,"bl","#0x140004d58"),
        (0x5b2c,"bl","#0x140004dd0"),
        # The general configuration caller reads three arguments from
        # the context after conditional state/usage checks.
        (0x63f8,"pacibsp",""),
        (0x6424,"ccmp","w2, #0xc, #0, ne"),
        (0x6438,"mov","w22, #1"),
        (0x6440,"ldr","w8, [x1, #8]"),
        (0x6444,"str","w8, [x19, #0x74]"),
        (0x6458,"str","w9, [x19, #0x68]"),
        (0x65f4,"ldr","w8, [x19, #0x6c]"),
        (0x65fc,"ldr","w8, [x19, #0x70]"),
        (0x6630,"ldur","x1, [x19, #0x6c]"),
        (0x6634,"ldr","w0, [x19, #0x68]"),
        (0x6638,"bl","#0x1400048c8"),
        # The second caller is behind original device state tests,
        # so don't label it a normal subtype-0 flash request.
        (0x6890,"pacibsp",""),
        (0x69a8,"ldrb","w8, [x19, #0x88]"),
        (0x69ac,"cbz","w8, #0x140006a08"),
        (0x6a08,"ldrb","w8, [x19, #0x81]"),
        (0x6a0c,"cmp","w8, #1"),
        (0x6a10,"b.ne","#0x140006a28"),
        (0x6a14,"ldr","w2, [x19, #0x74]"),
        (0x6a18,"ldur","x1, [x19, #0x6c]"),
        (0x6a1c,"ldr","w0, [x19, #0x68]"),
        (0x6a20,"bl","#0x1400048c8"),
        (0x6a28,"bl","#0x140004828"),
    ):
        expect(flash,rva,mn,args)
    # The actual helper has a FIXED interval argument 0x4f6 twice and
    # selects enabled request 0x101 or disabled request zero. Neither
    # input represents a requested 200-ms timer code of 0x93.
    for rva,mn,args in (
        (0x4de0,"bl","#0x140007bc0"),
        (0x4df0,"uxtb","w19, w0"),
        (0x4e18,"ldr","x8, #0x140004e78"),
        (0x4e20,"cmp","w19, #0"),
        (0x4e24,"str","wzr, [sp, #0xc]"),
        (0x4e28,"stur","x8, [sp, #4]"),
        (0x4e2c,"mov","w8, #0x101"),
        (0x4e30,"csel","w8, w8, wzr, ne"),
        (0x4e3c,"strh","w8, [sp]"),
        (0x4e40,"mov","w2, #0x10"),
        (0x4e48,"ldr","w0, #0x140004e80"),
        (0x4e4c,"bl","#0x140004ac0"),
        # The original PMIC timer callback converts the fixed interval
        # through its own 10-ms encoder to code 0xfe if enabled.
        (0x26ddc,"ldr","w7, [x22, x8, lsl #2]"),
        (0x26de0,"sub","w9, w7, #0xa"),
        (0x26de4,"cmp","w9, #0x4f6"),
        (0x26e38,"orr","w24, w20, w8, lsl #7"),
        (0x26e40,"bl","#0x140023968"),
    ):
        target=pmic if rva>=0x20000 else flash
        expect(target,rva,mn,args)
    require(struct.unpack("<Q",flash.get_data(0x4e78,8))[0]==
            (0x4f6|(0x4f6<<32)),
            "flash helper has non-fixed timer interval bytes")
    require(struct.unpack("<I",flash.get_data(0x4e80,4))[0]==0x802f0fac,
            "flash helper original PMIC timer IOCTL changed")
    require(struct.unpack("<Q",pmic.get_data(0x39498,8))[0]==BASE+0x26d50,
            "original PMIC four-channel timer callback identity changed")
    # Encoder from previous original OEM 10-ms formula:
    # enabled 1270 ms -> 0x80 | floor((1270-10)/10) = 0xfe;
    # disabled -> 0x00. A 0x93 value would encode 200 ms, NOT 1270.
    encoded=0x80|((0x4f6-10)//10)
    require(encoded==0xfe and encoded!=0x93 and 0!=0x93,
            "fixed helper could produce the archived 0x93 timer byte")
    return {
        "original_flash_alternate_start_rva":"0x48c8",
        "original_flash_direct_alternate_start_caller_rvas":
            [hex(x) for x in DIRECT_START_CALLERS],
        "original_flash_direct_timer_helper_caller_rvas":
            [hex(x) for x in DIRECT_TIMER_CALLERS],
        "general_context_setup_entry":"0x63f8",
        "general_context_setup_twelve_byte_input_checked":True,
        "general_context_prestart_checks_both_saved_context_words_zero":True,
        "second_start_caller_checks_context_byte_0x88_zero_and_byte_0x81_one":True,
        "alternate_start_direct_request_sequence":["current","timer","strobe"],
        "normal_subtype_zero_direct_branch_is_not_entire_lifecycle_proven":True,
        "timer_helper_fixed_interval_ms_when_enabled":0x4f6,
        "timer_helper_enabled_request_first_two_bytes":[1,1],
        "timer_helper_disabled_request_first_two_bytes":[0,0],
        "fixed_helper_enabled_encoder_requested_timer_byte":"0xfe",
        "fixed_helper_disabled_requested_timer_byte":"0x00",
        "fixed_helper_directly_requests_idle_0x93":False,
        "other_oem_timer_callback_callers_or_existing_state_excluded":False,
        "earliest_real_oem_or_firmware_0x93_writer_identified":False,
    }

def prior():
    p=ROOT/"experiments/E004-front-ir-vd55g0/e004he-original-subtype0-live-table-timer-route/evidence/RESULT.json"
    r=json.loads(p.read_text())
    require(r["status"]=="PASS_ORIGINAL_SUBTYPE0_CROSS_DRIVER_FLASH_TIMER_BRANCH_AND_LIVE_HANDLER_RECONCILIATION_OFFLINE" and
            r["cross_driver_original_arm64_route"]["normal_subtype_zero_contains_direct_timer_helper_call"] is False and
            r["original_timer_0x93_first_writer_identified"] is False,
            "previous original live-table subtype-0 status has drifted")
    return sha256(p.read_bytes()).hexdigest()

def main():
    result={
        "experiment":"E004hf",
        "status":"PASS_OEM_ALTERNATE_FLASH_START_CALLER_CONDITIONS_AND_FIXED_TIMER_REQUEST_EXCLUSION_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"721b7ca456badff50f52f400744d9b998c3c7700",
        "original_pe_sha256":{"qccamflash8380":FLASH_HASH,"qcpmic8380":PMIC_HASH},
        "prior_e004he_result_sha256":prior(),
        "original_alternate_start_route":original_route(image("qccamflash8380",FLASH_HASH),image("qcpmic8380",PMIC_HASH)),
        "fixed_helper_is_complete_oem_or_firmware_timer_writer_search":False,
        "first_0x93_timer_writer_identified":False,
        "new_windows_kd_camera_pmic_led_or_login_activity":False,
        "golden_modified":False,
        "native_ir_emitter_authorized":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_alternate.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HF_ORIGINAL_FLASH_ALTERNATE_START_TWO_DIRECT_CALLERS=PASS")
    print("E004HF_FIXED_TIMER_HELPER_CAN_REQUEST_FE_OR_00_NOT_93=PASS")
    print("E004HF_FIRST_93_WRITER=UNKNOWN GOLDEN_UNCHANGED IR_OFF")

if __name__=="__main__":main()
