#!/usr/bin/env python3
"""Pinned original Windows PMIC indirect timer callback-table audit, OFFLINE.

Maps code/data only. Does not establish which callback the OEM IR preview
actually exercises, physical electrical cutoff, pulse duration or eye safety.
"""
from pathlib import Path
from hashlib import sha256
import json
import struct
import pefile
import capstone

HERE=Path(__file__).resolve().parent
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
NAME="qcpmic8380.sys"
EXPECTED_HASH="756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
IMAGE_BASE=0x140000000
TABLE_RVA=0x39470
TIMER_BULK_RVA=0x26d50
TIMER_SINGLE_RVA=0x26f30
MODULE_RVA=0x285c0

def need(ok,why):
    if not ok: raise AssertionError("E004GP_FAIL_CLOSED "+why)

def check(data):
    need(sha256(data).hexdigest()==EXPECTED_HASH,"original Windows PMIC image SHA256 changed")
    pe=pefile.PE(data=data)
    need(pe.OPTIONAL_HEADER.ImageBase==IMAGE_BASE,"Windows PMIC preferred image base changed")
    need(pe.FILE_HEADER.Machine==0xaa64,"not an ARM64 PE")
    def pointer(rva):
        value=struct.unpack("<Q",pe.get_data(rva,8))[0]
        need(IMAGE_BASE<=value<IMAGE_BASE+pe.OPTIONAL_HEADER.SizeOfImage,
             "pointer outside original PMIC image")
        return value-IMAGE_BASE
    need(pointer(TABLE_RVA)==0x260b0,"dispatch-table first callback changed")
    need(pointer(TABLE_RVA+5*8)==TIMER_BULK_RVA,
         "4-channel timer callback table slot 5 changed")
    need(pointer(TABLE_RVA+6*8)==TIMER_SINGLE_RVA,
         "single-channel timer callback table slot 6 changed")
    need(pointer(TABLE_RVA+18*8)==MODULE_RVA,
         "four-channel module enable callback table slot 18 changed")
    md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    def instruction(rva):
        instructions=list(md.disasm(pe.get_data(rva,4),IMAGE_BASE+rva))
        need(len(instructions)==1,"missing AArch64 instruction")
        return instructions[0].mnemonic,instructions[0].op_str
    # The exported PMIC object path 0x210f0 loads this callback table into
    # an output structure. This is a static assignment, not a live call trace.
    for rva,mnemonic,argument in (
        (0x210f0,"adrp","0x140039000"),
        (0x210f4,"add","#0x470"),
        (0x210f8,"stp","xzr, x8"),
        (0x210fc,"mov","w8, #0x203"),
        (0x21100,"sturh","[x20, #0x19]"),
    ):
        op,args=instruction(rva)
        need(op==mnemonic and argument in args,
             f"PMIC output table initialization code changed at {rva:#x}: {op} {args}")
    # Do not confuse existence of a register-timer callback with knowledge
    # of actual runtime dispatch, controller edge behavior or fault latching.
    return {
        "pmic_callbacks_table_rva":"0x39470",
        "timer_bulk_callback_slot":5,
        "timer_bulk_callback_rva":"0x26d50",
        "timer_single_channel_callback_slot":6,
        "timer_single_channel_callback_rva":"0x26f30",
        "four_channel_module_callback_slot":18,
        "four_channel_module_callback_rva":"0x285c0",
        "table_pointer_assigned_to_output_structure_at_rva":"0x210f8",
        "table_output_variant_software_tag":"0x0203",
        "normal_oem_ir_preview_uses_bulk_or_single_timer_callback_proven":False,
        "timer_hardware_independently_cuts_off_stuck_strobe_proven":False,
        "actual_optical_current_and_irradiance_measured":False,
        "native_ir_emitter_authorized":False,
    }

def main():
    paths=list(ARCH.glob("*/"+NAME))
    need(len(paths)==1,"ambiguous original Windows PMIC image")
    data=paths[0].read_bytes()
    result=check(data)
    result.update({
        "experiment":"E004gp",
        "status":"PASS_PINNED_OEM_PMIC_INDIRECT_TIMER_CALLBACK_TABLE_OFFLINE",
        "original_pmic_sha256":EXPECTED_HASH,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_table.py").read_bytes()).hexdigest(),
        "ghidra_original_pmicsys_decompile_completed":True,
        "new_windows_kd_camera_pmic_or_emitter_activity":False,
        "golden_modified":False,
    })
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GP_ORIGINAL_PMIC_ARM64_DISPATCH_TABLE=PASS BULK_TIMER_SLOT=5 SINGLE_TIMER_SLOT=6")
    print("E004GP_OBJECT_TABLE_ASSIGNMENT=0x210f8 MODULE_CALLBACK_SLOT=18")
    print("RUNTIME_TIMER_SELECTED=UNKNOWN PHYSICAL_LED_OFF=UNPROVEN EMITTER=OFF")

if __name__=="__main__":main()
