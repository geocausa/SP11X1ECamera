#!/usr/bin/env python3
"""E004hv: pinned original UEFI PmicDxe indirect computed-register write path.

Original firmware HAS a computed-address, caller-value two-register writer
despite absence of four-channel flash timer literal in E004hu. The final
address, runtime periph metadata, routine invocation and incoming value remain
UNOBSERVED; this cannot establish the origin of idle timer byte 0x93.
No firmware/ESP/kernel/PMIC/SPMI write, camera or emitter activity.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import struct

import capstone
import pefile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HU=ROOT/"experiments/E004-front-ir-vd55g0/e004hu-installed-version-uefi-pmic-spmi-timer-literal-audit"
SPEC=importlib.util.spec_from_file_location("e004hv_original_uefi_parent",HU/"verify_firmware.py")
assert SPEC is not None and SPEC.loader is not None
previous=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(previous)
PE_SHA="402315711a6761441234eac8c0cd3c0ad23cb4fdb7d0a9de3dd94c3ffac38dff"
TARGET=0x222f8
RAW_WRITE=0x12154
SOFTWARE_SPMI_WRITE=0x8cd0
PTR_SITE=0x38d98
# These are exact original ARM64 image RVAs, not an executed decoder trace.
OPCODES=[
    (0x222f8,"stp","x29, x30, [sp, #-0x20]!"),
    (0x22304,"str","w0, [x29, #0x1c]"),
    (0x22308,"mov","w2, #0x26"),
    (0x2230c,"strh","w1, [x29, #0x18]"),
    (0x22310,"add","x4, x29, #0x1c"),
    (0x22314,"mov","w0, wzr"),
    (0x22318,"mov","w1, #0xe"),
    (0x2231c,"mov","w3, #4"),
    (0x22320,"bl","#0x12154"),
    (0x22328,"add","x4, x29, #0x18"),
    (0x2232c,"mov","w0, wzr"),
    (0x22330,"mov","w1, #0xe"),
    (0x22334,"mov","w2, #0x3e"),
    (0x22338,"mov","w3, #2"),
    (0x2233c,"bl","#0x12154"),
    (0x22340,"orr","w9, w0, w19"),
    (0x2234c,"cmp","w9, #0"),
    (0x12154,"stp","x29, x30, [sp, #-0x40]!"),
    (0x12168,"mov","x19, x4"),
    (0x1216c,"mov","w20, w3"),
    (0x12170,"mov","w22, w2"),
    (0x12174,"mov","w23, w1"),
    (0x12178,"mov","w21, w0"),
    (0x12184,"mov","w0, w21"),
    (0x12188,"bl","#0x12a98"),
    (0x12194,"cbz","x19, #0x121ac"),
    (0x121d0,"and","w23, w23, #0xff"),
    (0x121e4,"ldr","x8, [x21, #0x18]"),
    (0x121ec,"add","w9, w20, w22, uxtb"),
    (0x121f0,"ldr","w8, [x8, w23, uxtw #2]"),
    (0x12204,"and","w22, w22, #0xff"),
    (0x12214,"ldr","x0, [x21, #0x28]"),
    (0x1221c,"ldp","x11, x8, [x21]"),
    (0x12220,"mov","w2, w20"),
    (0x12224,"mov","x3, x19"),
    (0x12228,"ldrh","w9, [x21, #0x20]"),
    (0x1222c,"ldrh","w10, [x8]"),
    (0x12230,"ldrh","w8, [x8, #2]"),
    (0x12234,"add","w9, w9, w22"),
    (0x12238,"ldr","w0, [x11]"),
    (0x1223c,"madd","w9, w23, w10, w9"),
    (0x12240,"add","w1, w8, w9"),
    (0x12244,"bl","#0x8cd0"),
    (0x1224c,"mov","w19, w0"),
    (0x8cd0,"mov","w8, w1"),
    (0x8cd4,"mov","x4, x3"),
    (0x8cd8,"mov","w1, w0"),
    (0x8cdc,"mov","w3, w2"),
    (0x8ce0,"mov","w0, wzr"),
    (0x8ce4,"mov","w2, w8"),
    (0x8ce8,"b","#0x8cec"),
    (0x8d34,"bl","#0x1caf8"),
]
def require(ok,why):
    if not ok:raise AssertionError("E004HV_FAIL_CLOSED "+why)

def original_image():
    matches=[p for p in previous.DUMP.rglob("body.bin")
             if "PE32 image section" in p.parent.name and
             p.parent.parent.name.endswith(" PmicDxe")]
    require(len(matches)==1,"original UEFI PMIC PE missing or ambiguous")
    data=matches[0].read_bytes()
    require(sha256(data).hexdigest()==PE_SHA,
            "original version-matched UEFI PmicDxe image changed")
    pe=pefile.PE(data=data)
    require(pe.OPTIONAL_HEADER.ImageBase==0 and
            pe.FILE_HEADER.Machine==0xaa64,
            "wrong original UEFI ARM64 image")
    return pe

def instr(pe,rva):
    dis=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    items=list(dis.disasm(pe.get_data(rva,4),rva))
    require(len(items)==1 and items[0].address==rva,
            "missing original ARM64 instruction "+hex(rva))
    return items[0].mnemonic,items[0].op_str

def direct_bl_sites(pe,rva):
    dis=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    dis.skipdata=True
    sites=[]
    for sec in pe.sections:
        if not sec.Characteristics & 0x20000000:continue
        for i in dis.disasm(sec.get_data(),sec.VirtualAddress):
            if i.mnemonic=="bl" and i.op_str.startswith("#"):
                if int(i.op_str[1:],16)==rva:sites.append(i.address)
    return sorted(sites)

def analyze(pe):
    for rva,mn,ops in OPCODES:
        require(instr(pe,rva)==(mn,ops),
                "changed original PmicDxe code at "+hex(rva))
    require(struct.unpack("<Q",pe.get_data(PTR_SITE,8))[0]==TARGET,
            "original PmicDxe indirect service pointer changed")
    targets=[]
    needle=struct.pack("<Q",TARGET)
    for sec in pe.sections:
        data=sec.get_data()
        offset=0
        while (ix:=data.find(needle,offset))>=0:
            targets.append(sec.VirtualAddress+ix)
            offset=ix+1
    require(targets==[PTR_SITE],
            "original indirect firmware function table binding changed")
    no_direct=direct_bl_sites(pe,TARGET)
    require(not no_direct,
            "new original direct call to computed-peripheral firmware writer")
    calls=direct_bl_sites(pe,RAW_WRITE)
    require(len(calls)==47 and 0x22320 in calls and 0x2233c in calls,
            "original generic firmware write helper caller inventory drift")
    assert instr(pe,0x22334)==("mov","w2, #0x3e")
    return {
        "original_firmware_protocol_function_pointer_table_rva":hex(PTR_SITE),
        "original_indirect_function_pointer_target_rva":hex(TARGET),
        "original_direct_bl_to_indirect_function_count":0,
        "original_generic_write_helper_rva":hex(RAW_WRITE),
        "original_generic_write_direct_bl_count":len(calls),
        "original_uefi_pmic_index_input_for_both_calls":0,
        "original_peripheral_index_for_both_calls":"0x0e",
        "first_register_relative_offset":"0x26",
        "first_original_input_word_size_bytes":4,
        "second_register_relative_offset":"0x3e",
        "second_original_input_word_size_bytes":2,
        "second_original_value_source":"lower_16_bits_of_caller_w1",
        "runtime_address_base_source_rva":"0x12228",
        "runtime_peripheral_stride_source_rva":"0x1222c",
        "runtime_additional_offset_source_rva":"0x12230",
        "runtime_peripheral_base_composition_rvas":["0x12234","0x1223c","0x12240"],
        "original_uefi_spmi_software_write_wrapper_rva":hex(SOFTWARE_SPMI_WRITE),
        "second_write_register_address_equals_ee3e_proven":False,
        "original_function_called_on_this_sp11_pre_os_boot_proven":False,
        "original_caller_supplied_two_bytes_equal_0x93_or_0x9393_proven":False,
        "silicon_completion_or_physical_emitter_cutoff_proven":False,
        "original_timer_idle_byte_0x93_first_writer_identified":False,
    }

def prior():
    p=HU/"evidence/RESULT.json";r=json.loads(p.read_text())
    require(r["status"]==
            "PASS_CURRENT_VERSION_MATCHED_ARCHIVED_SP11_UEFI_PMIC_SPMI_EXPLICIT_TIMER_LITERAL_AUDIT_OFFLINE" and
            r["original_uefi_firmware_bounded_audit"]["original_first_0x93_timer_writer_identified"] is False and
            r["original_uefi_firmware_bounded_audit"]["archived_capsule_bytes_equals_running_firmware_bytes_verified"] is False,
            "original UEFI capsule provenance/missing first writer changed")
    return sha256(p.read_bytes()).hexdigest()

def main():
    r={
       "experiment":"E004hv",
       "status":"PASS_ORIGINAL_CURRENT_VERSION_UEFI_PMIC_INDIRECT_COMPUTED_PERIPHERAL_WRITE_2BYTE_OFFSET_3E_OFFLINE",
       "date":"2026-09-20",
       "baseline_commit":"0921178bc87ebbe6383ff2210f9b7a001b117df0",
       "original_uefi_pmic_image_sha256":PE_SHA,
       "prior_original_e004hu_result_sha256":prior(),
       "original_uefi_pmic_indirect_computed_writer":analyze(original_image()),
       "no_windows_kd_camera_pmic_spmi_led_firmware_or_login_activity":True,
       "golden_modified":False,
       "native_ir_emitter_authorized":False,
       "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
       "negative_test_sha256":sha256((HERE/"test_indirect.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(r,indent=2)+"\n")
    print("E004HV_ORIGINAL_UEFI_INDIRECT_PMIC_WRITE_SERVICE_FUNC_222F8_PUBLISHED=PASS")
    print("E004HV_TWO_COMPUTED_PERIPHERAL_WRITES_OFFSETS_26_3E_ORIGINAL_INPUT_BYTES=PASS")
    print("E004HV_NO_PROVEN_ACTUAL_EE3E_OR_93_FIRST_WRITER_OR_HARDWARE_CUTOFF")
if __name__=="__main__":main()
