#!/usr/bin/env python3
"""E004gz: address-range proof for three OTHER direct raw-write call sites.

Only original SHA-pinned Windows ARM64 PMIC PE and existing immutable E004gy
evidence. No camera, hardware access or claims about unobserved firmware.
"""
from pathlib import Path
from hashlib import sha256
import json
import struct
import pefile
import capstone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCHIVE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
PMIC_SHA="756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
IMAGE_BASE=0x140000000
TIMER_START=0xee3e
TIMER_END=0xee41
EXPECTED_DIRECT_RAW_CALLS=[0x23a04,0x2fc54,0x303b4,0x32c2c]
GENERIC_WRAPPER_RVA=0x32b70

def require(condition,reason):
    if not condition:raise AssertionError("E004GZ_FAIL_CLOSED "+reason)

def original_image():
    paths=list(ARCHIVE.glob("qcpmic8380.inf_*/qcpmic8380.sys"))
    require(len(paths)==1,"original OEM PMIC archive ambiguous")
    raw=paths[0].read_bytes()
    require(sha256(raw).hexdigest()==PMIC_SHA,"original Windows PMIC PE hash changed")
    pe=pefile.PE(data=raw)
    require(pe.FILE_HEADER.Machine==0xaa64 and
            pe.OPTIONAL_HEADER.ImageBase==IMAGE_BASE,"wrong ARM64 Windows image")
    return pe

def opcode(pe,rva):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    ins=list(cs.disasm(pe.get_data(rva,4),IMAGE_BASE+rva))
    require(len(ins)==1 and ins[0].address==IMAGE_BASE+rva,
            "missing original instruction "+hex(rva))
    return ins[0].mnemonic,ins[0].op_str

def assert_instruction(pe,rva,name,args):
    mn,operands=opcode(pe,rva)
    require((mn,operands)==(name,args),
            "changed original ARM64 instruction at "+hex(rva))
    return True

def direct_calls(pe,target):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    cs.skipdata=True
    callers=[]
    for sec in pe.sections:
        if not (sec.Characteristics&0x20000000):
            continue
        for ins in cs.disasm(sec.get_data(),IMAGE_BASE+sec.VirtualAddress):
            if (ins.mnemonic=="bl" and ins.op_str.startswith("#") and
                int(ins.op_str[1:],16)==IMAGE_BASE+target):
                callers.append(ins.address-IMAGE_BASE)
    return sorted(callers)

def address_proof(pe):
    require(direct_calls(pe,0x23dc8)==EXPECTED_DIRECT_RAW_CALLS,
            "direct raw-write helper caller set changed")
    require(direct_calls(pe,GENERIC_WRAPPER_RVA)==[],
            "generic raw-write wrapper gained direct BL caller")

    for rva,mn,args in (
        (0x2fc18,"ldrb","w4, [x20, #0x10]"),
        (0x2fc2c,"ldrb","w8, [x20, #4]"),
        (0x2fc30,"mov","w9, #0xfd00"),
        (0x2fc3c,"orr","w2, w8, w9"),
        (0x2fc54,"bl","#0x140023dc8"),
        (0x30298,"mov","w23, w2"),
        (0x30394,"mov","w8, #0x49"),
        (0x3039c,"orr","w2, w23, w8"),
        (0x303a4,"mov","w4, #2"),
        (0x303b4,"bl","#0x140023dc8"),
        (0x32b90,"uxth","w25, w1"),
        (0x32b94,"uxtb","w20, w2"),
        (0x32c20,"mov","w4, w20"),
        (0x32c24,"mov","w2, w25"),
        (0x32c28,"mov","x3, x23"),
        (0x32c2c,"bl","#0x140023dc8"),
    ):
        assert_instruction(pe,rva,mn,args)

    # A <=255-byte fdxx write always starts beyond the timer address range;
    # this does not assume a single-byte write.
    fdxx_min=min(0xfd00|byte for byte in range(256))
    fdxx_max_last=max((0xfd00|byte)+size-1
                      for byte in range(256) for size in range(1,256))
    require(fdxx_min==0xfd00 and fdxx_max_last==0xfefd and
            fdxx_min>TIMER_END,"FDxx candidate might overlap timer")

    # A 2-byte write into any timer byte must start at one of these
    # five addresses. None contains all the 0x49 bits that the original
    # OR instruction forces on the start address.
    starts=list(range(TIMER_START-1,TIMER_END+1))
    require(starts==[0xee3d,0xee3e,0xee3f,0xee40,0xee41] and
            all((start&0x49)!=0x49 for start in starts),
            "0x49-OR 2-byte candidate might overlap timer")

    # Generic function in actual .data callback table, separate from
    # Guard CF and unwind metadata xrefs.
    table_rva=0x3a510
    require(struct.unpack("<Q",pe.get_data(table_rva,8))[0]==
            IMAGE_BASE+GENERIC_WRAPPER_RVA and
            struct.unpack("<Q",pe.get_data(0x3a508,8))[0]==
            IMAGE_BASE+0x329e0,"original runtime generic IO callback table changed")
    require(struct.unpack("<I",pe.get_data(0x36694,4))[0]==
            GENERIC_WRAPPER_RVA and
            struct.unpack("<I",pe.get_data(0x3fee8,4))[0]==
            GENERIC_WRAPPER_RVA,"original Guard CF/.pdata metadata changed")
    return {
        "raw_write_helper_rva":"0x23dc8",
        "original_direct_raw_write_callsite_rvas":
            [hex(x) for x in EXPECTED_DIRECT_RAW_CALLS],
        "masked_write_callsite":"0x23a04",
        "excluded_as_direct_timer_writer":{
            "0x2fc54":"start 0xfd00 | u8, length u8<=255, start strictly above timer range",
            "0x303b4":"start input_or_0x49, length exactly 2; no overlap-eligible start contains all 0x49 bits",
        },
        "generic_capable_raw_write_callsite":"0x32c2c",
        "generic_wrapper_entry_rva":"0x32b70",
        "generic_wrapper_argument_address":"u16 of w1",
        "generic_wrapper_argument_length":"u8 of w2",
        "generic_wrapper_actual_data_callback_table_rva":"0x3a510",
        "generic_wrapper_direct_bl_callers":[],
        "generic_wrapper_dispatch_or_firmware_writer_identified":False,
        "actual_electrical_timer_register_write_observed":False,
    }

def prior():
    path=ROOT/"experiments/E004-front-ir-vd55g0/e004gy-early-raw-pmic-write-hardware-kd/evidence/RESULT.json"
    d=json.loads(path.read_text())
    require(d["experiment"]=="E004gy" and
            d["corrected_hardware_raw_helper_entry_records_logged"]==26 and
            d["raw_write_entry_spans_overlapping_ee3e_to_ee41"]==0 and
            d["raw_write_alternate_three_direct_callers_observed_in_this_window"] is False,
            "prior real SP7 KD result differs from original baseline")
    return sha256(path.read_bytes()).hexdigest()

def main():
    pe=original_image()
    summary=address_proof(pe)
    result={
        "experiment":"E004gz",
        "status":"PASS_ORIGINAL_ARM64_PMIC_THREE_BYPASS_ADDRESS_RANGE_AUDIT",
        "date":"2026-09-20",
        "baseline_commit":"60d4a05df31700ea2e2022c21c174e6be8b7b496",
        "original_pmic_sha256":PMIC_SHA,
        "prior_e004gy_result_sha256":prior(),
        "static_address_proof":summary,
        "two_direct_callers_impossible_to_overlap_four_timer_registers":True,
        "generic_16bit_address_u8_length_bypass_caller_remains_possible":True,
        "actual_generic_bypass_caller_runtime_hit_observed":False,
        "preos_firmware_or_original_timer_writer_identified":False,
        "native_linux_ir_emitter_authorized":False,
        "new_windows_kd_camera_or_pmic_activity":False,
        "golden_modified":False,
        "test_source_sha256":sha256((HERE/"test_static.py").read_bytes()).hexdigest(),
        "verifier_source_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GZ_ORIGINAL_PMICSYS_DIRECT_BYPASS_PROOF=PASS FDxx_AND_OR49_EXCLUDE_TIMER=YES")
    print("E004GZ_GENERIC_BYPASS_RVA=0x32c2c DISPATCH_DATA_TABLE_RVA=0x3a510")
    print("E004GZ_FIRST_TIMER_WRITER=UNKNOWN NATIVE_IR=OFF GOLDEN=UNCHANGED")

if __name__=="__main__":main()
