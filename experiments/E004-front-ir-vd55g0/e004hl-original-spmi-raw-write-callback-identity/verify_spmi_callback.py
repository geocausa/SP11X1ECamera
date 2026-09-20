#!/usr/bin/env python3
"""E004hl: original qcspmi8380.sys +0x30 interface callback identity.

Static original ARM64 SPMI provider table instruction sequence, cross-checking
original PMIC consumer. Not proof of live successful interface installation,
first 0x93 timer write, physical SPMI completion, emitter or independent cutoff.
"""
from pathlib import Path
from hashlib import sha256
import json
import pefile
import capstone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
BASE=0x140000000
SPMI_HASH="b6a5868ec2450e713b9a5ada7b4e1a4a77c77427fedf0806fe3eb6541099523c"
PMIC_HASH="756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
PROVIDER_CALLBACK=0x1660

def need(ok,why):
    if not ok:raise AssertionError("E004HL_FAIL_CLOSED "+why)

def original(name,digest):
    matches=list(ARCH.glob(name+".inf_*/"+name+".sys"))
    need(len(matches)==1,"ambiguous original OEM image "+name)
    raw=matches[0].read_bytes()
    need(sha256(raw).hexdigest()==digest,"original OEM image hash changed "+name)
    pe=pefile.PE(data=raw)
    need(pe.FILE_HEADER.Machine==0xaa64 and pe.OPTIONAL_HEADER.ImageBase==BASE,
         "wrong original OEM Windows ARM64 image")
    return pe

def instr(pe,rva):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    found=list(cs.disasm(pe.get_data(rva,4),BASE+rva))
    need(len(found)==1,"missing original instruction "+hex(rva))
    return found[0].mnemonic,found[0].op_str

def expect(pe,rva,mn,args):
    need(instr(pe,rva)==(mn,args),"original interface callback instr changed "+hex(rva))

def audit(spmi,pmic):
    # The output struct x9=sp+0x110 is the original provider 0x70-byte
    # interface data block. +0x30 is SP+0x140; original x9=+0x1660 is
    # written to SP+0x140, with neighboring +0x38=+0x1920.
    # Descriptor x2=SP+0x70 points at x9 (interface data) and GUID.
    for rva,mn,args in (
        (0x3e38,"ldr","w8, #0x1400042c4"),
        (0x3e44,"str","w8, [sp, #0x110]"),
        (0x3e48,"adrp","x8, #0x140002000"),
        (0x3e4c,"add","x9, x8, #0x820"),
        (0x3e50,"adrp","x8, #0x140002000"),
        (0x3e54,"add","x8, x8, #0x930"),
        (0x3e60,"stp","x9, x8, [sp, #0x120]"),
        (0x3e64,"adrp","x8, #0x140001000"),
        (0x3e68,"add","x10, x8, #0x3a0"),
        (0x3e70,"adrp","x8, #0x140001000"),
        (0x3e74,"add","x9, x8, #0x660"),
        (0x3e78,"stp","xzr, x10, [sp, #0x130]"),
        (0x3e80,"adrp","x8, #0x140001000"),
        (0x3e84,"add","x8, x8, #0x920"),
        (0x3e88,"stp","x9, x8, [sp, #0x140]"),
        (0x3e98,"add","x8, x8, #0xe10"),
        (0x3e9c,"stp","x9, x8, [sp, #0x150]"),
        (0x3ec4,"stp","x9, x8, [sp, #0x170]"),
        (0x3ef0,"mov","x8, #0x30"),
        (0x3ef4,"str","w8, [sp, #0x70]"),
        (0x3efc,"add","x8, x8, #0x1d8"),
        (0x3f00,"add","x9, sp, #0x110"),
        (0x3f10,"stp","x9, x8, [sp, #0x78]"),
        (0x3f24,"ldr","x8, [x8, #0x720]"),
        (0x3f38,"blr","x15"),
        # OEM provider +0x1660 entry consumes context, opaque bus payload
        # and count in exactly the register sequence supplied by PMIC.
        (0x1660,"pacibsp",""),
        (0x1684,"mov","w26, w1"),
        (0x1688,"mov","w21, w2"),
        (0x168c,"mov","x27, x3"),
        (0x1690,"mov","w25, w4"),
        (0x1698,"cbz","x0, #0x1400016d4"),
        (0x177c,"ubfx","w23, w21, #0x10, #4"),
        (0x1780,"ubfx","w19, w21, #8, #8"),
        (0x1784,"and","w20, w21, #0xff"),
        (0x1788,"ubfx","w21, w21, #0x14, #4"),
    ):
        expect(spmi,rva,mn,args)
    for rva,mn,args in (
        (0x393c,"add","x3, x8, #0x10"),
        (0x3948,"add","x2, x8, #0x58"),
        (0x3958,"ldr","x8, [x9, #0x588]"),
        (0x395c,"mov","w4, #0x70"),
        (0x3974,"blr","x15"),
        (0x23ec4,"add","x25, x8, #0x10"),
        (0x23f1c,"ldr","x0, [x25, #0x20]"),
        (0x23f20,"mov","x3, x26"),
        (0x23f24,"ldr","x8, [x25, #0x30]"),
        (0x23f28,"mov","w1, #0"),
        (0x23f2c,"mov","x15, x8"),
        (0x23f3c,"blr","x15"),
    ):
        expect(pmic,rva,mn,args)
    need(spmi.get_data(0xa1d8,16)==pmic.get_data(0x37058,16),
         "original provider/consumer interface GUID changed")
    # Original provider packs sp+0x130 two zero/callback pointers:
    # when the PMIC dereferences x0 from interface +0x20 it may be
    # assigned/adjusted by WDF. The raw provider +0x1660 null-context
    # branch and error handling prevent treating static table as a
    # successful actual register operation.
    return {
        "original_spmi_interface_guid_rva":"0xa1d8",
        "original_pmic_matching_interface_guid_rva":"0x37058",
        "provider_original_interface_buffer_stack_offset":"0x110",
        "provider_original_interface_buffer_size_bytes":112,
        "provider_write_callback_stack_offset":"0x140",
        "provider_write_callback_offset_within_interface":"0x30",
        "provider_original_callback_rva":"0x1660",
        "provider_original_neighbor_callback_rva":"0x1920",
        "provider_callback_argument_capture_rvas":["0x1684","0x1688","0x168c","0x1690"],
        "provider_opaque_packed_selector_decode_rvas":["0x177c","0x1780","0x1784","0x1788"],
        "pmic_consumer_raw_write_indirect_slot_offset":"0x30",
        "pmic_raw_callback_invoked_on_actual_windows_timer_during_this_stage":False,
        "pmic_interface_live_callback_and_context_identity_observed":False,
        "spmi_controller_actual_physical_bus_write_completed":False,
        "pmic_timer_byte_0x93_first_writer_identified":False,
        "physical_emitter_output_or_autonomous_fault_off_proven":False,
    }

def prior():
    p=ROOT/"experiments/E004-front-ir-vd55g0/e004hk-original-pmic-spmi-interface-selector-audit/evidence/RESULT.json"
    d=json.loads(p.read_text())
    need(d["status"]=="PASS_ORIGINAL_OEM_PMIC_SPMI_SHARED_GUID_RAW_WRITE_SELECTOR_AND_INDIRECT_TRANSPORT_OFFLINE" and
         d["original_pmic_spmi_interface_and_selector"]["original_timer_0x93_first_writer_identified"] is False,
         "previous original raw SPMI interface proof changed")
    return sha256(p.read_bytes()).hexdigest()

def main():
    result={
        "experiment":"E004hl",
        "status":"PASS_ORIGINAL_SPMI_PROVIDER_PLUS_30_CALLBACK_1660_PMIC_INDIRECT_SLOT_IDENTITY_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"84a55cf072a3dde194124ed13bcb8f3deb8cbd98",
        "original_oem_image_sha256":{"qcspmi8380":SPMI_HASH,"qcpmic8380":PMIC_HASH},
        "prior_e004hk_result_sha256":prior(),
        "original_provider_consumer_slot":audit(original("qcspmi8380",SPMI_HASH),
                                                 original("qcpmic8380",PMIC_HASH)),
        "fresh_windows_kd_camera_spmi_pmic_led_or_login_action":False,
        "golden_modified":False,
        "native_ir_emitter_authorized":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "test_sha256":sha256((HERE/"test_callback.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HL_ORIGINAL_SPMI_PROVIDER_WDF_INTERFACE_PLUS30_CALLBACK_1660=PASS")
    print("E004HL_ORIGINAL_PMIC_RAW_PLUS30_CONSUMER_EQUALS_PROVIDER_STATIC_SLOT=PASS")
    print("E004HL_NO_ACTUAL_93_FIRST_WRITER_OR_HARDWARE_OUTPUT_NATIVE_IR=OFF")
if __name__=="__main__":main()
