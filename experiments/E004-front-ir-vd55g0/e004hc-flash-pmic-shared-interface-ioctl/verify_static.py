#!/usr/bin/env python3
"""Verify an ORIGINAL flash->PMIC shared Windows device interface + IOCTL path.

Offline original OEM ARM64 PE only. Does not transmit an IOCTL, read a PMIC,
activate the flash, or equate a software IOCTL with a physical LED pulse.
"""
from pathlib import Path
from hashlib import sha256
import json
import struct
import uuid
import pefile
import capstone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCHIVE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
BASE=0x140000000
OEM={
 "qcpmic8380":"756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
 "qccamflash8380":"6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b",
}
GUID="20952871-af3d-4a8a-9e47-cb346507b95b"
FLASH_GUID_RVA=0xd858
PMIC_GUID_RVA=0x36fb8
CODE=0x802f0fc8
FLASH_CODE_RVA=0x4dc8
PMIC_CODE_RVA=0x7c10

def need(ok,why):
    if not ok:raise AssertionError("E004HC_FAIL_CLOSED "+why)

def original(name):
    matches=list(ARCHIVE.glob(name+".inf_*/"+name+".sys"))
    need(len(matches)==1,"OEM driver archive ambiguous "+name)
    data=matches[0].read_bytes()
    need(sha256(data).hexdigest()==OEM[name],"original OEM PE SHA changed "+name)
    pe=pefile.PE(data=data)
    need(pe.FILE_HEADER.Machine==0xaa64 and
         pe.OPTIONAL_HEADER.ImageBase==BASE,"wrong original Windows ARM64 image "+name)
    return pe

def instruction(pe,rva):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    decoded=list(cs.disasm(pe.get_data(rva,4),BASE+rva))
    need(len(decoded)==1 and decoded[0].address==BASE+rva,
         "original instruction absent "+hex(rva))
    return decoded[0].mnemonic,decoded[0].op_str

def expect(pe,rva,mn,operands):
    need(instruction(pe,rva)==(mn,operands),
         "original ARM64 instruction changed "+hex(rva))

def iat(pe,rva):
    names={entry.address-BASE:(entry.name or b"").decode(errors="replace")
           for group in pe.DIRECTORY_ENTRY_IMPORT for entry in group.imports}
    return names.get(rva)

def direct_calls(pe,target):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    cs.skipdata=True
    sites=[]
    for sec in pe.sections:
        if not sec.Characteristics&0x20000000:
            continue
        for ins in cs.disasm(sec.get_data(),BASE+sec.VirtualAddress):
            if (ins.mnemonic=="bl" and ins.op_str.startswith("#") and
                int(ins.op_str[1:],16)==BASE+target):
                sites.append(ins.address-BASE)
    return sorted(sites)

def audit(flash,pmic):
    common=uuid.UUID(GUID).bytes_le
    need(flash.get_data(FLASH_GUID_RVA,16)==common and
         pmic.get_data(PMIC_GUID_RVA,16)==common,
         "exact original flash/PMIC GUID not identical")
    need(iat(flash,0xc118)=="IoGetDeviceInterfaces" and
         iat(flash,0xc110)=="IoGetDeviceObjectPointer" and
         iat(flash,0xc1a0)=="IoBuildDeviceIoControlRequest" and
         iat(flash,0xc1a8)=="IofCallDriver",
         "flash Windows original Io* import identity changed")
    # GUID: PMIC passes it through its WDF function-pointer entry.
    for rva,mn,operands in (
        (0x2574,"adrp","x8, #0x140036000"),
        (0x2578,"add","x2, x8, #0xfb8"),
        (0x2588,"ldr","x8, [x9, #0x268]"),
        (0x259c,"blr","x15"),
    ):
        expect(pmic,rva,mn,operands)
    # Flash enumerates EXACT SAME GUID and obtains a device object pointer.
    for rva,mn,operands in (
        (0x49fc,"adrp","x8, #0x14000d000"),
        (0x4a00,"add","x0, x8, #0x858"),
        (0x4a18,"ldr","x8, [x8, #0x118]"),
        (0x4a20,"blr","x8"),
        (0x4a38,"ldr","x8, [x8, #0x58]"),
        (0x4a48,"adrp","x8, #0x14002a000"),
        (0x4a4c,"add","x3, x8, #0x7d0"),
        (0x4a50,"adrp","x8, #0x14002a000"),
        (0x4a54,"add","x2, x8, #0x7c0"),
        (0x4a5c,"ldr","x8, [x8, #0x110]"),
        (0x4a68,"blr","x8"),
    ):
        expect(flash,rva,mn,operands)
    # Original flash camera-command wrapper sends its 4-byte input packet
    # via IoBuildDeviceIoControlRequest and IofCallDriver on this interface.
    for rva,mn,operands in (
        (0x4da0,"add","x1, sp, #0x10"),
        (0x4da4,"ldr","w0, #0x140004dc8"),
        (0x4da8,"bl","#0x140004ac0"),
        (0x4ae0,"adrp","x19, #0x14002a000"),
        (0x4ae4,"ldr","x8, [x19, #0x7d0]"),
        (0x4b20,"ldr","x1, [x19, #0x7d0]"),
        (0x4b2c,"ldr","x8, [x8, #0x1a0]"),
        (0x4b68,"ldr","x0, [x19, #0x7d0]"),
        (0x4b4c,"blr","x8"),
        (0x4b70,"ldr","x8, [x8, #0x1a8]"),
        (0x4b74,"blr","x8"),
    ):
        expect(flash,rva,mn,operands)
    need(struct.unpack("<I",flash.get_data(FLASH_CODE_RVA,4))[0]==CODE and
         struct.unpack("<I",pmic.get_data(PMIC_CODE_RVA,4))[0]==CODE,
         "the original flash/PMIC IOCTL codes differ")
    # Original PMIC dispatch compares exactly this code and takes a
    # branch with 4-byte input-size check and an indirect target at +0x90.
    for rva,mn,operands in (
        (0x71e0,"ldr","w8, #0x140007c10"),
        (0x71e4,"cmp","w1, w8"),
        (0x71e8,"b.eq","#0x140007378"),
        (0x7378,"cmp","x23, #4"),
        (0x737c,"b.eq","#0x140007394"),
        (0x7394,"bl","#0x140006e00"),
        (0x73a4,"ldr","x8, [x8, #0x90]"),
        (0x73c0,"mov","x0, x24"),
        (0x73d4,"blr","x15"),
    ):
        expect(pmic,rva,mn,operands)
    need(0x4da8 in direct_calls(flash,0x4ac0),
         "camera flash original command no longer calls IOCTL send wrapper")
    need(direct_calls(pmic,0x32b70)==[],
         "generic PMIC callback gained direct code caller")
    return {
        "shared_original_device_interface_guid":GUID,
        "flash_guid_rva":"0xd858",
        "pmic_guid_rva":"0x36fb8",
        "flash_api":"IoGetDeviceInterfaces then IoGetDeviceObjectPointer",
        "flash_api_import_rvas":["0xc118","0xc110"],
        "flash_command_wrapper_rva":"0x4d58",
        "flash_ioctl_send_helper_rva":"0x4ac0",
        "shared_flash_target_device_object_storage_rva":"0x2a7d0",
        "flash_device_object_pointer_used_by_ioctl_build_and_send":True,
        "flash_ioctl_build_api":"IoBuildDeviceIoControlRequest",
        "flash_ioctl_dispatch_api":"IofCallDriver",
        "shared_original_ioctl_code":hex(CODE),
        "flash_ioctl_literal_rva":"0x4dc8",
        "pmic_ioctl_literal_rva":"0x7c10",
        "pmic_ioctl_dispatch_compare_rva":"0x71e4",
        "pmic_ioctl_match_branch_rva":"0x7378",
        "pmic_input_size_bytes":4,
        "pmic_indirect_ioctl_handler_ptr_offset":"0x90",
        "flash_ioctl_handler_is_generic_0x32b70_callback_proven":False,
        "same_runtime_flash_request_observed_in_this_offline_stage":False,
        "physical_timer_or_led_output_proven":False,
    }

def previous():
    p=ROOT/"experiments/E004-front-ir-vd55g0/e004ha-generic-pmic-callback-registration/evidence/RESULT.json"
    r=json.loads(p.read_text())
    need(r["status"]=="PASS_ORIGINAL_OEM_GENERIC_WRITE_CALLBACK_AND_TWO_DESCRIPTOR_PRODUCERS_OFFLINE" and
         r["generic_write_callback_runtime_entry_hit_observed"] is False,
         "prior generic callback classification changed")
    return sha256(p.read_bytes()).hexdigest()

def main():
    result={
        "experiment":"E004hc",
        "status":"PASS_ORIGINAL_OEM_FLASH_PMIC_SHARED_GUID_IOCTL_DISPATCH_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"858f740f346ececd35b871d6f3c79a1e45aa1fab",
        "original_pe_sha256":OEM,
        "previous_e004ha_result_sha256":previous(),
        "flash_to_pmic_static_original_path":audit(original("qccamflash8380"),original("qcpmic8380")),
        "generic_0x32b70_callback_is_this_ioctl_handler_identified":False,
        "actual_ioctl_request_executed_this_stage":False,
        "original_0x93_timer_register_writer_identified":False,
        "independent_optical_electrical_cutoff_proven":False,
        "new_windows_kd_camera_pmic_or_led_activity":False,
        "native_linux_emitter_authorized":False,
        "golden_modified":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_static.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HC_ORIGINAL_SHARED_PMIF_GUID_AND_IOCTL_802F0FC8_DISPATCH=PASS")
    print("E004HC_FLASH_IOBUILD_REQUEST_TO_PMIC_4BYTE_INDIRECT_HANDLER=PASS")
    print("E004HC_TIMER_FIRST_WRITER=UNKNOWN PHYSICAL_CUTOFF=UNPROVEN GOLDEN=UNCHANGED")

if __name__=="__main__":main()
