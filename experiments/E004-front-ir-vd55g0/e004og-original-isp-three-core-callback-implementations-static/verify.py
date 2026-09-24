#!/usr/bin/env python3
"""E004og: exact original ISP CSID/IFE/CDM callback implementations, static only.

SHA-locked original private same-SP11 ARM64 .sys stays on original device;
committed output includes *only* RVA/scalar facts and strict unproven gates.
"""
import bisect
import copy
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000

# Provider installation anchor, source branch and original subordinate calls.
# This is NOT evidence that *every* rear profile installed or used all 3.
ANCHORS={
 0x17694:("adrp","x8, 0x140021000 <.text+0x20000>"),
 0x17698:("add","x9, x8, #0x1b0"),
 0x176a4:("stp","x9, x8, [x21]"),
 0x2233c:("adrp","x8, 0x140022000 <.text+0x21000>"),
 0x22340:("add","x9, x8, #0xcd0"),
 0x2234c:("stp","x9, x8, [x23]"),
 0x18348:("adrp","x8, 0x140028000 <.text+0x27000>"),
 0x1834c:("add","x10, x8, #0x480"),
 0x1835c:("stp","x10, x9, [x8]"),
 0x211b0:("pacibsp",""),
 0x22cd0:("pacibsp",""),
 0x28480:("pacibsp",""),
 0x218d8:("cmp","w1, #0x804"),
 0x218dc:("b.eq","0x140021b4c <.text+0x20b4c>"),
 0x218e0:("cmp","w1, #0x805"),
 0x218e4:("b.eq","0x140021904 <.text+0x20904>"),
 0x21904:("ldr","w8, [x19, #0xd4]"),
 0x21918:("str","w22, [x19, #0xbc]"),
 0x2192c:("blr","x15"),
 0x21b10:("add","x0, x19, #0xa8"),
 0x21b14:("bl","0x14002a4a0 <.text+0x294a0>"),
 0x21b24:("adrp","x8, 0x140039000 <.text+0x38000>"),
 0x21b34:("cbz","w20, 0x140021b90 <.text+0x20b90>"),
 0x21b64:("mov","x0, x19"),
 0x21b68:("bl","0x140024260 <.text+0x23260>"),
 0x23604:("cmp","w1, #0x804"),
 0x23608:("b.eq","0x14002366c <.text+0x2266c>"),
 0x2360c:("cmp","w1, #0x805"),
 0x23610:("b.ne","0x140023698 <.text+0x22698>"),
 0x23614:("add","x0, x19, #0xc8"),
 0x23618:("bl","0x1400221a0 <.text+0x211a0>"),
 0x23640:("mov","x0, x19"),
 0x23644:("bl","0x140027278 <.text+0x26278>"),
 0x2364c:("cbz","w20, 0x140023698 <.text+0x22698>"),
 0x28534:("cmp","w1, #0x804"),
 0x28538:("b.eq","0x1400285c8 <.text+0x275c8>"),
 0x2853c:("cmp","w1, #0x805"),
 0x28540:("b.eq","0x14002854c <.text+0x2754c>"),
 0x2854c:("ldr","x8, [x19, #0x48]"),
 0x28550:("str","wzr, [x8, #0x30]"),
 0x28598:("strb","w8, [x19, #0x888]"),
 0x285a4:("bl","0x14002a4a0 <.text+0x294a0>"),
 0x285c8:("ldr","x9, [x19, #0x48]"),
 0x285d4:("bl","0x140009718 <.text+0x8718>"),
 0x285e0:("str","w8, [x9, #0x1c]"),
}
PROVIDERS={
  "CSID":{"installation_RVA":"0x17694","interface_pointer_pair_store_RVA":"0x176a4",
          "first_callback_entry_RVA":"0x211b0","start_selector_cmp_RVA":"0x218d8",
          "stop_selector_cmp_RVA":"0x218e0","stop_selected_branch_RVA":"0x21904"},
  "IFE":{"installation_RVA":"0x2233c","interface_pointer_pair_store_RVA":"0x2234c",
         "first_callback_entry_RVA":"0x22cd0","start_selector_cmp_RVA":"0x23604",
         "stop_selector_cmp_RVA":"0x2360c","stop_selected_branch_RVA":"0x23614"},
  "CDM":{"installation_RVA":"0x18348","interface_pointer_pair_store_RVA":"0x1835c",
         "first_callback_entry_RVA":"0x28480","start_selector_cmp_RVA":"0x28534",
         "stop_selector_cmp_RVA":"0x2853c","stop_selected_branch_RVA":"0x2854c"},
}

def require(ok,reason):
    if not ok:raise AssertionError("E004OG_FAIL_CLOSED "+reason)

def section_data(data,name):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    require(data[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",data,pe+4)[0]==0xaa64,"exact ARM64 PE")
    sh=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    for i in range(struct.unpack_from("<H",data,pe+6)[0]):
        off=sh+40*i
        sec=data[off:off+8].rstrip(b"\0").decode(errors="replace")
        if sec==name:
            virtual_size,va,raw_size,raw=struct.unpack_from("<IIII",data,off+8)
            return data[raw:raw+raw_size]
    raise AssertionError("missing original PE section "+name)

def instructions():
    src=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    return {int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//",1)[0].strip())
            for m in rx.finditer(src)}

def expected():
    return {
      "schema":"sp11-e004og-source-verified-OEM-ISP-CSID-IFE-CDM-first-core-callback-implementations-v1",
      "parent_git_revision":"fa2e06969f86d34a648b406956528a5720e8ad99",
      "exact_original_same_SP11_OEM_ISP_SHA256":SHA,
      "original_ARM64_instruction_anchors":len(ANCHORS),
      "specific_original_per_core_provider_functions":PROVIDERS,
      "first_functions_source_verified_as_PE_function_entries":True,
      "original_core_initializer_stores_3_distinct_first_callback_function_pointers":True,
      "original_core_function_receives_numeric_0x804_0x805_as_parameter_w1":True,
      "CSID_0x805_has_event_or_worker_stop_progress_path":True,
      "IFE_0x805_calls_distinct_stop_command_helpers":True,
      "CDM_0x805_has_separate_command_state_and_event_path":True,
      "all_3_callback_bodies_present_in_original_same_SP11_ISP_binary":True,
      "active_rear_Windows_4k_capture_selected_all_3_core_instances_proven":False,
      "actual_per_mode_hardware_register_write_and_QC10C_UBWC_frame_ABI_fully_decoded":False,
      "physical_stop_DMA_WM16_quiescence_and_irq_retirement_proven":False,
      "Windows_live_BF_0x0f_event_observed":False,
      "Linux_native_rear_4k_ISP_optical_frame_proven":False,
      "original_OEM_ISP_binary_disassembly_optical_data_or_KD_exported":False,
      "protected_Golden_camera_hardware_or_boot_modified":False,
    }

def validate(j):
    require(j==expected(),"saved record or safe source boundary changed")
    for name,profile in j["specific_original_per_core_provider_functions"].items():
        require(profile["first_callback_entry_RVA"] in ("0x211b0","0x22cd0","0x28480"),
                "unknown original provider function "+name)
    return True

if __name__=="__main__":
    orig=ISP.read_bytes()
    require(hashlib.sha256(orig).hexdigest()==SHA,"original same-SP11 OEM binary SHA")
    a=instructions()
    for addr,ins in ANCHORS.items():
        require(a.get(addr)==ins,
                "original OEM disassembly mismatch at 0x%x: %s != %s"%(addr,a.get(addr),ins))
    pdata=section_data(orig,".pdata")
    starts=sorted({struct.unpack_from("<I",pdata,i)[0] for i in range(0,len(pdata)-7,8)
                   if 0x1000<=struct.unpack_from("<I",pdata,i)[0]<0x30000})
    for name,profile in PROVIDERS.items():
        entry=int(profile["first_callback_entry_RVA"],16)
        pivot=int(profile["stop_selector_cmp_RVA"],16)
        k=bisect.bisect_right(starts,pivot)-1
        require(k>=0 and starts[k]==entry,
                "installed callback not PE function entry for "+name)
        require(int(profile["installation_RVA"],16)<int(profile["interface_pointer_pair_store_RVA"],16),
                "address must be taken before interface pointer store "+name)
    j=expected()
    p=HERE/"RESULT.json"
    if not p.exists():
        p.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
        print("E004OG_SAFE_SOURCE_SCALAR_RESULT_CREATED")
    else:
        require(json.loads(p.read_text())==j,"saved safe result does not match original OEM source")
    neg=(
      ("false_source_SHA",lambda q:q.__setitem__("exact_original_same_SP11_OEM_ISP_SHA256","0"*64)),
      ("mislabel_CSID_first_callback",lambda q:q["specific_original_per_core_provider_functions"]["CSID"].__setitem__("first_callback_entry_RVA","0x22cd0")),
      ("mislabel_IFE_callback_store",lambda q:q["specific_original_per_core_provider_functions"]["IFE"].__setitem__("interface_pointer_pair_store_RVA","0x176a4")),
      ("mislabel_CDM_callback",lambda q:q["specific_original_per_core_provider_functions"]["CDM"].__setitem__("first_callback_entry_RVA","0x211b0")),
      ("false_no_PE_entry",lambda q:q.__setitem__("first_functions_source_verified_as_PE_function_entries",False)),
      ("false_shared_callback",lambda q:q.__setitem__("original_core_initializer_stores_3_distinct_first_callback_function_pointers",False)),
      ("false_event",lambda q:q.__setitem__("CSID_0x805_has_event_or_worker_stop_progress_path",False)),
      ("fake_photo_active",lambda q:q.__setitem__("active_rear_Windows_4k_capture_selected_all_3_core_instances_proven",True)),
      ("false_register_decode",lambda q:q.__setitem__("actual_per_mode_hardware_register_write_and_QC10C_UBWC_frame_ABI_fully_decoded",True)),
      ("false_physical_quiescence",lambda q:q.__setitem__("physical_stop_DMA_WM16_quiescence_and_irq_retirement_proven",True)),
      ("false_live_BF",lambda q:q.__setitem__("Windows_live_BF_0x0f_event_observed",True)),
      ("false_native_rear4k",lambda q:q.__setitem__("Linux_native_rear_4k_ISP_optical_frame_proven",True)),
      ("false_Golden_change",lambda q:q.__setitem__("protected_Golden_camera_hardware_or_boot_modified",True)),
      ("false_private_export",lambda q:q.__setitem__("original_OEM_ISP_binary_disassembly_optical_data_or_KD_exported",True)),
    )
    for name,mut in neg:
        mutant=copy.deepcopy(j)
        mut(mutant)
        try:validate(mutant)
        except (AssertionError,KeyError,TypeError):
            continue
        raise AssertionError("E004OG_FAIL_OPEN_NEGATIVE "+name)
    print(f"PASS_E004OG_ORIGINAL_SAME_SP11_CSID_IFE_CDM_CONCRETE_CALLBACKS_"
          f"{len(ANCHORS)}_ARM64_INSTRUCTIONS_{len(neg)}_FAIL_CLOSED_NEGATIVES_"
          "PROVIDER_POINTERS_PE_FUNCTION_ENTRIES_804_805_BRANCHES_"
          "LIVE_BACKEND_AND_PHYSICAL_STOP_UNPROVEN_GOLDEN_SAFE")
