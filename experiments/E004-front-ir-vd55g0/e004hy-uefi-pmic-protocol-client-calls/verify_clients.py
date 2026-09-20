#!/usr/bin/env python3
"""E004hy: real static UEFI protocol-lookup/callsite audit, no hardware access.

A compiled client callsite does NOT establish an invocation on this SP11,
and a negative scan of one instruction form does not exclude indirect calls.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import re
import pefile
import capstone

HERE=Path(__file__).resolve().parent
HW=HERE.parent/"e004hw-uefi-pmic-protocol-owner-static"
HX=HERE.parent/"e004hx-uefi-pmic-runtime-descriptor-provenance"
S=importlib.util.spec_from_file_location("e004hw_source",HW/"verify_protocol.py")
assert S and S.loader
hw=importlib.util.module_from_spec(S)
S.loader.exec_module(hw)
# Original image SHA/RVA and exact original selected instruction identities.
CLIENTS={
 "78 QcomChargerDxeWp":{
  "sha":"067796b86f7473584a12e22493d50ed95b7b67c2b29c4352586240bccf8bf481",
  "guid_rva":0x2d260,
  "code":{
   0x2864:("adrp","x0, #0x2d000"),
   0x286c:("add","x0, x0, #0x260"),
   0x287c:("ldr","x8, [x8, #0x140]"),
   0x2880:("blr","x8"),
   0x2894:("ldr","x8, [x8, #0x180]"),
   0x289c:("blr","x8"),
   0x11284:("add","x0, x0, #0x260"),
   0x11294:("ldr","x8, [x8, #0x140]"),
   0x11298:("blr","x8"),
   0x112b0:("ldr","x8, [x8, #0x270]"),
  }
 },
 "80 ChargerExDxe":{
  "sha":"6e3e9d6c12db312457a7eae95e639d31e4c8023bff962810166b0645ee997509",
  "guid_rva":0x70a0,
  "code":{
   0x2574:("adrp","x0, #0x7000"),
   0x257c:("add","x0, x0, #0xa0"),
   0x258c:("ldr","x8, [x8, #0x140]"),
   0x2590:("blr","x8"),
   0x25a4:("ldr","x8, [x8, #0x180]"),
   0x25ac:("blr","x8"),
  }
 },
 "53 PlatformEntMgtPolicyDxe":{
  "sha":"fc6ca458e5c44e12b3420ce8eaf13863300a7250e0f213940eb9d17acf4b649d",
  "guid_rva":0x12140,
  "code":{
   0x7d64:("adrp","x0, #0x12000"),
   0x7d6c:("add","x0, x0, #0x140"),
   0x7d7c:("ldr","x8, [x8, #0x140]"),
   0x7d80:("blr","x8"),
   0x7d9c:("ldr","x8, [x8, #0x180]"),
   0x7da8:("blr","x8"),
  }
 },
 "88 BdsDxe":{
  "sha":"83a73d1dfadca35a9ddc07380c0907ac8e5329d5263ce30e1aaf167fc8e982ee",
  "guid_rva":0x8b780,
  "code":{
   0x36818:("adrp","x0, #0x8b000"),
   0x36820:("add","x0, x0, #0x780"),
   0x36830:("ldr","x8, [x8, #0x140]"),
   0x36834:("blr","x8"),
   0x36850:("ldr","x8, [x8, #0x180]"),
   0x3685c:("blr","x8"),
  }
 },
 "97 DisplayDxe":{
  "sha":"8d1f8e750a72b4e04cc71bdb9350e333b488dc42db156415c6ca0f1d634cbf40",
  "guid_rva":0x6e360,
  "code":{
   0x4d014:("adrp","x0, #0x6e000"),
   0x4d01c:("add","x0, x0, #0x360"),
   0x4d02c:("ldr","x8, [x8, #0x140]"),
   0x4d030:("blr","x8"),
   0x4d04c:("ldr","x8, [x8, #0x180]"),
   0x4d058:("blr","x8"),
  }
 },
 "108 UsbPwrCtrlDxe":{
  "sha":"6afb1921b08a13876cf015e700607236a180f8249c71a65db0ccc8f696e5e806",
  "guid_rva":0x80e0,
  "code":{
   0x4e80:("adrp","x0, #0x8000"),
   0x4e88:("add","x0, x0, #0xe0"),
   0x4e98:("ldr","x8, [x8, #0x140]"),
   0x4e9c:("blr","x8"),
   0x4ec4:("ldr","x2, [x8, #0x80]"),
   0x4ec8:("br","x2"),
  }
 }
}
def require(ok,reason):
    if not ok:raise AssertionError("E004HY_FAIL_CLOSED "+reason)

def check_client_image(pe,name):
    spec=CLIENTS[name]
    require(pe.FILE_HEADER.Machine==0xaa64 and pe.OPTIONAL_HEADER.ImageBase==0,
            "wrong original client image type "+name)
    guid_rva=spec["guid_rva"]
    require(pe.get_data(guid_rva,16)==hw.GUID_INTERFACE,
            "original client GUID site changed "+name)
    for addr,expect in spec["code"].items():
        require(hw.hv.instr(pe,addr)==expect,
                "original client instruction changed "+name+" "+hex(addr))

def original_image_path(name):
    hits=[p for p in hw.hv.previous.DUMP.rglob("body.bin")
          if "PE32 image section" in p.parent.name and p.parent.parent.name==name]
    require(len(hits)==1,"original client image missing/ambiguous "+name)
    return hits[0]

def original_client(name):
    raw=original_image_path(name).read_bytes()
    require(sha256(raw).hexdigest()==CLIENTS[name]["sha"],
            "original client archive SHA drift "+name)
    return pefile.PE(data=raw)

def scan_direct_0x240_ldr(pe):
    # Narrow negative: only direct LDR Xn,[Xm,#0x240] in original executable
    # 4-byte-aligned code. No claim about register-computed or other forms.
    dis=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    count=0
    pattern=re.compile(r"x(?:[12]?\d|30), \[x(?:[12]?\d|30), #0x240\]$")
    for sec in pe.sections:
        if not (sec.Characteristics & 0x20000000):continue
        raw=sec.get_data()
        for i in range(0,len(raw)-3,4):
            one=list(dis.disasm(raw[i:i+4],sec.VirtualAddress+i))
            if one and one[0].mnemonic=="ldr" and pattern.fullmatch(one[0].op_str):
                count+=1
    return count

def main():
    prior=HX/"evidence/RESULT.json"
    old=json.loads(prior.read_text())
    require(old["status"]==
        "PASS_ORIGINAL_UEFI_PMIC_RUNTIME_DESCRIPTOR_LAZY_INIT_AND_FALLBACK_ADDRESS_BOUND_OFFLINE",
        "previous original firmware runtime provenance missing")
    summary={}
    for name in CLIENTS:
        pe=original_client(name)
        check_client_image(pe,name)
        summary[name]={
            "original_pe_sha256":CLIENTS[name]["sha"],
            "exact_original_guid_rva":hex(CLIENTS[name]["guid_rva"]),
            "original_guid_uefi_boot_services_lookup_offset":"0x140",
            "positive_compiled_protocol_callsite_offsets":
                ["0x180","0x270"] if name=="78 QcomChargerDxeWp" else
                ["0x80"] if name=="108 UsbPwrCtrlDxe" else ["0x180"],
            "direct_literal_ldr_method_offset_0x240_in_this_original_image":
                scan_direct_0x240_ldr(pe),
            "actual_original_guid_lookup_or_method_invocation_on_this_sp11_boot_proven":False,
        }
        require(summary[name]["direct_literal_ldr_method_offset_0x240_in_this_original_image"]==0,
                "direct original client 0x240 load found: inspect instead of claim")
    result={
        "experiment":"E004hy",
        "status":"PASS_ORIGINAL_UEFI_PMIC_CLIENT_POSITIVE_METHOD_CALLS_AND_BOUNDED_240_NO_LITERAL_LDR_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"8443104e2630331285dbe26254cf8eabf2e373dc",
        "prior_e004hx_result_sha256":sha256(prior.read_bytes()).hexdigest(),
        "original_guid": "ae6ae96e-483f-42ae-9cc1-9fac1b584728",
        "original_protocol_client_selected_evidence":summary,
        "no_claim_about_other_indirect_call_forms_to_slot_0x240":True,
        "no_claim_of_actual_pmic_timer_write_or_0x93_first_writer":True,
        "original_firmware_boot_reboot_kd_camera_spmi_pmic_emitter_login_activity":False,
        "native_ir_emitter_authorized":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_clients.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HY_6_ORIGINAL_CLIENTS_GENUINE_UEFI_PROTOCOL_ACQUISITION_AND_ALTERNATE_METHOD_CALLS_PASS")
    print("E004HY_DIRECT_LITERAL_LDR_METHOD_SLOT_0x240_IN_SIX_CLIENTS_ZERO_ONLY_BOUNDED_NEGATIVE")
    print("E004HY_PRE_OS_TIMER_0x93_WRITER_UNKNOWN_NATIVE_IR_OFF")
if __name__=="__main__":main()
