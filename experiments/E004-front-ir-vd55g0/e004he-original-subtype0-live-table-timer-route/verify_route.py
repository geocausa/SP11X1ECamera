#!/usr/bin/env python3
"""E004he: original Windows subtype-0 flash commands and PMIC table identity.

Cross-check original pinned ARM64 PEs, previously completed live-pointer KD
and original subtype-0 evidence. No Windows boot, PMIC/LED or camera access.
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
BASE=0x140000000
HASHES={
    "qccamflash8380":"6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b",
    "qcpmic8380":"756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
}
# rva of the FLASH literal, PMIC literal, comparison, handler branch,
# input byte count, actual vtable offset, target original PMIC RVA.
ROUTES={
    "current":(0x802f0fb0,0x4d50,0x7bfc,0x6f8c,0x6fc8,6,0x38,0x270c0),
    "timer":(0x802f0fac,0x4e80,0x7bf8,0x6f80,0x7040,16,0x28,0x26d50),
    "trigger_input":(0x802f0fcc,0x6238,0x7c14,0x71f0,0x7300,4,0x70,0x27f20),
    "trigger_mode":(0x802f0fd0,0x623c,0x7c18,0x71fc,0x7288,20,0x80,0x281e0),
    "strobe":(0x802f0fc8,0x4dc8,0x7c10,0x71e4,0x7378,4,0x90,0x285c0),
}
EXPECTED_FLASH_DIRECT_TIMER_CALLERS=[0x4938,0x5b2c]

def require(ok,msg):
    if not ok:raise AssertionError("E004HE_FAIL_CLOSED "+msg)

def original(name):
    files=list(ARCH.glob(name+".inf_*/"+name+".sys"))
    require(len(files)==1,"ambiguous OEM original PE "+name)
    raw=files[0].read_bytes()
    require(sha256(raw).hexdigest()==HASHES[name],"OEM original hash changed "+name)
    pe=pefile.PE(data=raw)
    require(pe.OPTIONAL_HEADER.ImageBase==BASE and
            pe.FILE_HEADER.Machine==0xaa64,"wrong original OEM ARM64 PE "+name)
    return pe

def decode(pe,rva):
    dis=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    result=list(dis.disasm(pe.get_data(rva,4),BASE+rva))
    require(len(result)==1,"missing original opcode at "+hex(rva))
    return result[0].mnemonic,result[0].op_str

def expect(pe,rva,opcode,operands):
    require(decode(pe,rva)==(opcode,operands),
            "unexpected original ARM64 instruction at "+hex(rva))

def number(pe,rva):
    require(len(pe.get_data(rva,4))==4,"missing literal at "+hex(rva))
    return struct.unpack("<I",pe.get_data(rva,4))[0]

def direct_bl(pe,target):
    dis=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    dis.skipdata=True
    matches=[]
    for sec in pe.sections:
        if not sec.Characteristics&0x20000000:
            continue
        for i in dis.disasm(sec.get_data(),BASE+sec.VirtualAddress):
            if i.mnemonic=="bl" and i.op_str.startswith("#"):
                if int(i.op_str[1:],16)-BASE==target:
                    matches.append(i.address-BASE)
    return sorted(matches)

def verify(flash,pmic):
    for name,(code,fr,pr,cmp_rva,branch,size,slot,target) in ROUTES.items():
        require(number(flash,fr)==code and number(pmic,pr)==code,
                "cross-driver IOCTL constant mismatch for "+name)
        # Bound the original compare to this exact literal and a branch
        # to the specified PMIC handler; no guessed named exports.
        expect(pmic,cmp_rva,"cmp","w1, w8")
        expect(pmic,cmp_rva+4,"b.eq","#"+hex(BASE+branch))
        # The input-size comparison is in the beginning of each branch;
        # find the exact following cmp, rather than accepting any branch.
        branch_code=[decode(pmic,x) for x in range(branch,branch+16,4)]
        expected_sizes={("cmp",register+" #"+rendered)
                        for register in ("x23,", "x27,")
                        for rendered in (hex(size),str(size))}
        require(any(item in expected_sizes for item in branch_code),
                "PMIC input-size check for "+name)
        actual=struct.unpack("<Q",pmic.get_data(0x39470+slot,8))[0]
        require(actual==BASE+target,"original PMIC four-channel table slot changed for "+name)
    # Pin both table branches and their original argument forwarding.
    for rva,mn,args in (
        (0x6f7c,"ldr","w8, #0x140007bf8"),
        (0x6f80,"cmp","w1, w8"),
        (0x6f84,"b.eq","#0x140007040"),
        (0x705c,"bl","#0x140006e00"),
        (0x7068,"ldr","x8, [x8, #0x8d8]"),
        (0x706c,"ldr","x8, [x8, #0x28]"),
        (0x709c,"blr","x15"),
        (0x71e0,"ldr","w8, #0x140007c10"),
        (0x71e4,"cmp","w1, w8"),
        (0x71e8,"b.eq","#0x140007378"),
        (0x7394,"bl","#0x140006e00"),
        (0x73a0,"ldr","x8, [x8, #0x8d8]"),
        (0x73a4,"ldr","x8, [x8, #0x90]"),
        (0x73d4,"blr","x15"),
        (0x4d20,"mov","w2, #6"),
    ):
        target=flash if rva==0x4d20 else pmic
        expect(target,rva,mn,args)
    # Original flash helper/normal-subtype path: 0->0x5b80, while subtype
    # 2 directly calls the timer helper. The subtype-0 direct command
    # sequence has current + three interface requests + strobe, not timer.
    for rva,mn,args in (
        (0x4d28,"ldr","w0, #0x140004d50"),
        (0x4d2c,"bl","#0x140004ac0"),
        (0x4e40,"mov","w2, #0x10"),
        (0x4e48,"ldr","w0, #0x140004e80"),
        (0x4e4c,"bl","#0x140004ac0"),
        (0x4da4,"ldr","w0, #0x140004dc8"),
        (0x4da8,"bl","#0x140004ac0"),
        (0x5ae8,"cmp","w8, #2"),
        (0x5aec,"b.ne","#0x140005b44"),
        (0x5b2c,"bl","#0x140004dd0"),
        (0x5b44,"cmp","w8, #1"),
        (0x5b48,"b.ne","#0x140005b7c"),
        (0x5b7c,"cbnz","w8, #0x140005c88"),
        (0x5bd4,"bl","#0x140004ce0"),
        (0x5c20,"ldr","w0, #0x140006238"),
        (0x5c24,"bl","#0x140004ac0"),
        (0x5c4c,"ldr","w0, #0x14000623c"),
        (0x5c50,"bl","#0x140004ac0"),
        (0x5c58,"mov","w2, #0"),
        (0x5c5c,"mov","w1, #1"),
        (0x5c60,"mov","w0, #1"),
        (0x5c64,"bl","#0x140004d58"),
    ):
        expect(flash,rva,mn,args)
    require(direct_bl(flash,0x4dd0)==EXPECTED_FLASH_DIRECT_TIMER_CALLERS,
            "whole original flash executable direct timer-helper caller set changed")
    dis=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    inside=[i for i in dis.disasm(flash.get_data(0x5b7c,0x5c68-0x5b7c),
                                    BASE+0x5b7c)
            if i.mnemonic=="bl" and i.op_str=="#0x140004dd0"]
    require(not inside,"original subtype-0 direct path unexpectedly calls timer")
    for rva,mn,args in (
        (0x28620,"ldrb","w5, [x20]"),
        (0x28678,"ldrb","w8, [x20, #3]"),
        (0x28680,"mov","w2, #0xee46"),
        (0x28688,"ubfiz","w4, w8, #7, #1"),
        (0x28698,"bl","#0x140023968"),
        (0x2869c,"cbnz","w0, #0x140028804"),
        (0x287bc,"mov","w2, #0xee4e"),
        (0x287c4,"bl","#0x140023968"),
        (0x26e40,"bl","#0x140023968"),
    ):
        expect(pmic,rva,mn,args)
    return {
        "verified_cross_driver_commands":{
            name:{
                "ioctl":hex(code),"flash_literal_rva":hex(fr),
                "pmic_literal_rva":hex(pr),"pmic_dispatch_branch_rva":hex(branch),
                "input_bytes":size,"live_four_channel_table_offset":hex(slot),
                "original_pmic_callback_rva":hex(target),
            }
            for name,(code,fr,pr,cmp_rva,branch,size,slot,target) in ROUTES.items()
        },
        "live_windows_flash_handler_table_rva":"0x39470",
        "normal_subtype_zero_direct_flash_request_sequence":
            ["current","trigger_input","trigger_mode","strobe"],
        "flash_timer_helper_rva":"0x4dd0",
        "whole_flash_original_direct_timer_helper_callers":
            [hex(v) for v in EXPECTED_FLASH_DIRECT_TIMER_CALLERS],
        "normal_subtype_zero_contains_direct_timer_helper_call":False,
        "normal_subtype_zero_may_invoke_indirect_or_prior_timer_writer_excluded":False,
        "normal_subtype_zero_strobe_on_initial_data_bytes":[1,1,0,1],
        "pmic_strobe_callback_requests_module_ee46_then_channels_ee4e":True,
        "pmic_strobe_callback_directly_calls_timer_helper_0x26d50":False,
        "windows_normal_subtype_zero_actual_0x93_timer_source_identified":False,
    }

def prior():
    proof=ROOT/"experiments/E004-front-ir-vd55g0/e004hd-live-pmic-ioctl-handler-pointer-kd/evidence/RESULT.json"
    r=json.loads(proof.read_text())
    require(r["status"]==
            "PASS_FRESH_WINDOWS_READ_ONLY_OEM_PMIC_IOCTL_LIVE_HANDLER_TABLE_RESOLVED_GOLDEN_RETURN" and
            r["final_handler_global_resolved_rva"]=="0x39470" and
            r["final_live_handler_target_oem_pmic_rva"]=="0x285c0" and
            r["four_channel_callback_executed_in_this_read_only_session"] is False and
            r["normal_windows_reboot_to_golden"] is True and
            r["native_linux_ir_or_login_modified"] is False,
            "prior live-pointer original KD evidence no longer validates")
    return sha256(proof.read_bytes()).hexdigest()

def main():
    route=verify(original("qccamflash8380"),original("qcpmic8380"))
    result={
        "experiment":"E004he",
        "status":"PASS_ORIGINAL_SUBTYPE0_CROSS_DRIVER_FLASH_TIMER_BRANCH_AND_LIVE_HANDLER_RECONCILIATION_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"ed70db7d9afff865790b769212a49b6a5d988c9a",
        "original_pe_sha256":HASHES,
        "prior_e004hd_live_kd_result_sha256":prior(),
        "cross_driver_original_arm64_route":route,
        "fresh_windows_session_or_camera_preview_executed":False,
        "original_timer_0x93_first_writer_identified":False,
        "physical_current_irradiance_autonomous_timer_proven":False,
        "native_linux_ir_emitter_authorized":False,
        "golden_modified":False,
        "verifier_source_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_source_sha256":sha256((HERE/"test_route.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HE_ORIGINAL_CROSS_DRIVER_5_OPERATION_LIVE_TABLE_ROUTE=PASS")
    print("E004HE_SUBTYPE0_CURRENT_TRIGGER_MODE_STROBE_NO_DIRECT_TIMER_CALL=PASS")
    print("E004HE_FIRST_TIMER_WRITER=UNKNOWN NATIVE_IR=OFF GOLDEN_UNCHANGED")

if __name__=="__main__":main()
