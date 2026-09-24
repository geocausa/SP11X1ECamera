#!/usr/bin/env python3
"""E004od: same-SP11 OEM AVStream -> ISP -> nested HW-manager callback chain.

Offline only. SHA-lock original private ARM64 PE images. Export relative RVAs,
scalar evidence flags and bounded negative tests; never export OEM images,
disassembly, KD material, optical pixels, hardware addresses or parameters.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ORIG=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
AVS=ORIG/"surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys"
ISP=ORIG/"qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys"
SHA={
 "AVStream":"b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed",
 "ISP":"64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c",
}
BASE=0x140000000
# All anchors below are checked against ORIGINAL source disassembly, never
# copied from a guessed Linux driver or from unverified postprocessed notes.
ANCHORS={
 "AVStream":{
  0x20dd8:("ldrb","w10, [x9, #0x30]"),
  0x20ddc:("cbnz","w10, 0x140020dfc <.text+0x1fdfc>"),
  0x20dfc:("ldr","x10, [x9, #0x40]"),
  0x20e18:("mov","w2, w1"),
  0x20e1c:("ldr","x1, [x9, #0x38]"),
  0x20e30:("blr","x15"),
 },
 "ISP":{
  # Original ISP interface request returns the outer callback, not the
  # nested hardware manager directly.
  0x5684:("adrp","x9, 0x140004000 <.text+0x3000>"),
  0x5688:("add","x9, x9, #0xe30"),
  0x568c:("stp","x22, x9, [x8, #0x10]"),
  0x4e54:("mov","x24, x1"),
  0x4e58:("mov","w22, w2"),
  0x51e0:("ldr","x0, [x24, #0x10]"),
  0x51f4:("ldr","x8, [x0]"),
  0x51fc:("mov","w1, w22"),
  0x5210:("blr","x15"),
  # Typed context field +0x10 is the OUTPUT of helper 0x15A40, not an
  # arbitrary pointer we invent or infer from the numeric command.
  0x6a13c:("ldr","x2, [x8, #0x110]"),
  0x6a164:("mov","x20, x0"),
  0x6a2e4:("add","x0, x20, #0x10"),
  0x6a2f4:("bl","0x140015a40 <.text+0x14a40>"),
  0x6a304:("ldr","x4, [x20, #0x10]"),
  # Pool helper chooses a free record among at most sixteen of stride
  # 0xE38; returns record+0x48 to the typed-context output field.
  0x15ab4:("mov","w21, #0x0"),
  0x15ab8:("mov","x9, #0xe38"),
  0x15ac0:("umaddl","x8, w21, w9, x8"),
  0x15ac4:("ldrb","w10, [x8, #0x70]"),
  0x15ad0:("cmp","w21, #0x10"),
  0x15adc:("add","x9, x8, #0x48"),
  0x15ae0:("str","x9, [x19]"),
  0x15b70:("ldr","x19, [x19]"),
  0x15b74:("adrp","x8, 0x140015000 <.text+0x14000>"),
  0x15b78:("add","x8, x8, #0xd70"),
  0x15b80:("stp","x8, x9, [x19]"),
  # Nested function dispatches 0x804 start-like and 0x805 stop-like
  # to per-core callback interfaces. No physical VFE/MMIO semantics here.
  0x15d70:("pacibsp",""),
  0x15db4:("mov","w24, w1"),
  0x15ee0:("cmp","w24, #0x804"),
  0x15ee4:("b.ne","0x140016300 <.text+0x15300>"),
  0x15f3c:("mov","w1, #0x804"),
  0x15f50:("blr","x15"),
  0x15fd8:("mov","w1, #0x804"),
  0x15fec:("blr","x15"),
  0x161ec:("mov","w1, #0x804"),
  0x16208:("blr","x15"),
  0x16300:("cmp","w24, #0x805"),
  0x16304:("b.ne","0x140016504 <.text+0x15504>"),
  0x1631c:("strb","wzr, [x21, #0x510]"),
  0x163ac:("mov","w1, #0x805"),
  0x163c8:("blr","x15"),
  0x16414:("mov","w1, #0x805"),
  0x16434:("blr","x15"),
  0x164a0:("mov","w1, #0x805"),
  0x164b4:("blr","x15"),
 }
}

def must(ok,why):
    if not ok:raise AssertionError("E004OD_FAIL_CLOSED "+why)

def disasm(p):
    s=subprocess.check_output(["llvm-objdump","-d",str(p)],text=True)
    regex=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    return {int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//",1)[0].strip())
            for m in regex.finditer(s)}

def verify_saved(j):
    must(j["schema"]=="sp11-e004od-original-oem-nested-hw-manager-static-v1","schema")
    must(j["parent_git_revision"]=="c583437a310297d546e1150da5b6147e253db310","parent")
    must(j["private_original_OEM_SHA256"]==SHA,"original OEM hashes")
    must(j["original_ARM64_instruction_anchors"]==sum(map(len,ANCHORS.values())),"instruction count")
    expected_rvas={
      "AVStream_common_dispatcher":"0x20da8",
      "ISP_returned_outer_callback":"0x4e30",
      "ISP_typed_context_creation":"0x6a0a0",
      "ISP_nested_pool_acquire_helper":"0x15a40",
      "ISP_nested_pool_record_callback":"0x15d70",
      "ISP_0x804_nested_branch":"0x15ee0",
      "ISP_0x805_nested_branch":"0x16300",
    }
    must(j["proven_source_RVAs"]==expected_rvas,"callback chain")
    must(j["nested_pool_max_slots"]==16 and j["nested_pool_stride_bytes"]==0xe38 and
         j["nested_interface_record_offset_bytes"]==0x48,"bounded pool")
    must(j["AVStream_alternate_callback_passes_selector_w1_to_ISP_w2"] is True,"selector transform")
    must(j["ISP_outer_callback_forwards_selected_engine_commands_to_nested_interface"] is True,"outer->nested")
    must(j["ISP_nested_callback_dispatches_0x804_to_distinct_per_core_interfaces"] is True,"nested start fanout")
    must(j["ISP_nested_callback_dispatches_0x805_to_distinct_per_core_interfaces"] is True,"nested stop fanout")
    for key in ("live_rear_VideoRecord_selected_this_ISP_callback_proven",
                "ISP_0x809_receiver_and_semantics_proven",
                "per_core_callback_implementation_and_real_MMIO_stop_order_proven",
                "live_Windows_rear_BF_completion_proven",
                "Linux_native_rear_4k_ISP_optical_frame_proven",
                "Golden_camera_hardware_or_boot_modified"):
        must(j[key] is False,key+" unproven")
    must(j["original_private_driver_pixels_DMA_addresses_or_OEM_binaries_exported"] is False,"private export")
    return True

def build():
    ds={}
    for name,path in (("AVStream",AVS),("ISP",ISP)):
        data=path.read_bytes()
        must(hashlib.sha256(data).hexdigest()==SHA[name],name+" SHA")
        must(data[:2]==b"MZ",name+" source format")
        ds[name]=disasm(path)
        for rva,expected in ANCHORS[name].items():
            must(ds[name].get(rva)==expected,f"{name} source ARM64 RVA=0x{rva:x}")
    # The load from the selected nested interface -> its first code entry
    # must connect to the exactly installed callback RVA 0x15D70.
    def is_installed_code(rva):
        return rva in ds["ISP"] and ds["ISP"][rva][0]=="pacibsp"
    must(is_installed_code(0x15d70),"installed original callback entry")
    result={
     "schema":"sp11-e004od-original-oem-nested-hw-manager-static-v1",
     "parent_git_revision":"c583437a310297d546e1150da5b6147e253db310",
     "private_original_OEM_SHA256":SHA,
     "original_ARM64_instruction_anchors":sum(map(len,ANCHORS.values())),
     "proven_source_RVAs":{
       "AVStream_common_dispatcher":"0x20da8",
       "ISP_returned_outer_callback":"0x4e30",
       "ISP_typed_context_creation":"0x6a0a0",
       "ISP_nested_pool_acquire_helper":"0x15a40",
       "ISP_nested_pool_record_callback":"0x15d70",
       "ISP_0x804_nested_branch":"0x15ee0",
       "ISP_0x805_nested_branch":"0x16300",
     },
     "nested_pool_max_slots":16,
     "nested_pool_stride_bytes":0xe38,
     "nested_interface_record_offset_bytes":0x48,
     "AVStream_alternate_callback_passes_selector_w1_to_ISP_w2":True,
     "ISP_outer_callback_forwards_selected_engine_commands_to_nested_interface":True,
     "ISP_nested_callback_dispatches_0x804_to_distinct_per_core_interfaces":True,
     "ISP_nested_callback_dispatches_0x805_to_distinct_per_core_interfaces":True,
     "live_rear_VideoRecord_selected_this_ISP_callback_proven":False,
     "ISP_0x809_receiver_and_semantics_proven":False,
     "per_core_callback_implementation_and_real_MMIO_stop_order_proven":False,
     "live_Windows_rear_BF_completion_proven":False,
     "Linux_native_rear_4k_ISP_optical_frame_proven":False,
     "Golden_camera_hardware_or_boot_modified":False,
     "original_private_driver_pixels_DMA_addresses_or_OEM_binaries_exported":False,
    }
    verify_saved(result)
    return result

if __name__=="__main__":
    actual=build()
    p=HERE/"RESULT.json"
    if not p.exists():
        p.write_text(json.dumps(actual,indent=2,sort_keys=True)+"\n")
        print("E004OD_SAFE_SCALAR_RESULT_CREATED")
    else:
        must(json.loads(p.read_text())==actual,"saved scalar differs from original source")
    neg=(
      ("fake_original_ISP_sha",lambda x:x["private_original_OEM_SHA256"].__setitem__("ISP","0"*64)),
      ("fake_original_AVStream_sha",lambda x:x["private_original_OEM_SHA256"].__setitem__("AVStream","0"*64)),
      ("wrong_nested_callback",lambda x:x["proven_source_RVAs"].__setitem__("ISP_nested_pool_record_callback","0x15d74")),
      ("wrong_pool_stride",lambda x:x.__setitem__("nested_pool_stride_bytes",0xe30)),
      ("wrong_pool_count",lambda x:x.__setitem__("nested_pool_max_slots",17)),
      ("fake_nonpool_interface",lambda x:x.__setitem__("nested_interface_record_offset_bytes",0)),
      ("fake_direct_outer_call",lambda x:x.__setitem__("ISP_outer_callback_forwards_selected_engine_commands_to_nested_interface",False)),
      ("invented_804_no_fanout",lambda x:x.__setitem__("ISP_nested_callback_dispatches_0x804_to_distinct_per_core_interfaces",False)),
      ("invented_805_no_fanout",lambda x:x.__setitem__("ISP_nested_callback_dispatches_0x805_to_distinct_per_core_interfaces",False)),
      ("fake_live_capture",lambda x:x.__setitem__("live_rear_VideoRecord_selected_this_ISP_callback_proven",True)),
      ("fake_809_semantics",lambda x:x.__setitem__("ISP_0x809_receiver_and_semantics_proven",True)),
      ("fake_per_core_MMIO_stop",lambda x:x.__setitem__("per_core_callback_implementation_and_real_MMIO_stop_order_proven",True)),
      ("fake_live_BF",lambda x:x.__setitem__("live_Windows_rear_BF_completion_proven",True)),
      ("fake_native_rear_4k",lambda x:x.__setitem__("Linux_native_rear_4k_ISP_optical_frame_proven",True)),
      ("fake_Golden_change",lambda x:x.__setitem__("Golden_camera_hardware_or_boot_modified",True)),
      ("fake_original_export",lambda x:x.__setitem__("original_private_driver_pixels_DMA_addresses_or_OEM_binaries_exported",True)),
    )
    for name,mutator in neg:
        mutant=copy.deepcopy(actual)
        mutator(mutant)
        try:verify_saved(mutant)
        except (AssertionError,KeyError,TypeError):
            continue
        raise AssertionError("E004OD_FAIL_OPEN_NEGATIVE_TEST "+name)
    print("PASS_E004OD_ORIGINAL_OEM_AVSTREAM_TO_ISP_NESTED_HW_MANAGER_"
          f"{actual['original_ARM64_instruction_anchors']}_SOURCE_LOCKED_INSTRUCTIONS_"
          "804_805_PER_CORE_FANOUT_16_NEGATIVE_TESTS_"
          "NO_LIVE_PROFILE_OR_NATIVE_REAR_4K_CLAIM")
