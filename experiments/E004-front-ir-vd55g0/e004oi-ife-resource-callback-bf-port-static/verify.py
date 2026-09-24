#!/usr/bin/env python3
"""E004oi: identify two original IFE resource callbacks and BF 0x300D branch.

Original private SP11 ARM64 OEM ISP stays in its source directory. Export
safe source-derived code RVAs, flags and bounded negative tests, never
original binary, raw OEM code/diagnostics, DMA pointers, pixels, secrets.
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
ANCHORS={
 0x19fa8:("add","x8, x19, #0x6b, lsl #12"),
 0x19fac:("ldr","w8, [x8, #0x678]"),
 0x19fb0:("cmp","w8, #0x0"),
 0x19fd0:("adrp","x8, 0x14001c000 <.text+0x1b000>"),
 0x19fd4:("add","x9, x8, #0xf0"),
 0x19fd8:("adrp","x8, 0x14001d000 <.text+0x1c000>"),
 0x19fdc:("add","x8, x8, #0x830"),
 0x19fe0:("csel","x9, x9, x8, ne"),
 0x19fe4:("add","x8, x19, #0x6b, lsl #12"),
 0x19fe8:("str","x9, [x8, #0x688]"),
 0x19ffc:("csel","x9, x9, x8, ne"),
 0x1a004:("str","x9, [x8, #0x690]"),
  # Exact resource loop receiving the selected pointer, with 0 stop flag.
 0x272c8:("cmp","w21, #0x22"),
 0x272d8:("ldr","w1, [x19, x8, lsl #2]"),
 0x272dc:("cmp","w1, w20"),
 0x272e4:("ldr","x8, [x25, #0x688]"),
 0x272e8:("mov","w2, #0x0"),
 0x272ec:("mov","x0, x19"),
 0x27300:("blr","x15"),
 0x27340:("ldr","x8, [x8, #0x690]"),
 0x27358:("blr","x15"),
  # Both selected handlers are real PE callable function entries.
 0x1c0f0:("pacibsp",""),
 0x1c114:("mov","w20, w1"),
 0x1c11c:("cmp","w23, #0x1"),
 0x1c174:("mov","w8, #0x3006"),
 0x1c1a4:("mov","w8, #0x301f"),
 0x1d830:("pacibsp",""),
 0x1d84c:("mov","w22, w1"),
 0x1d850:("mov","w8, #0x300d"),
 0x1d854:("cmp","w8, w22"),
 0x1d860:("b.ne","0x14001d86c <.text+0x1c86c>"),
 0x1d884:("cmp","w23, #0x1"),
 0x1d904:("sub","w10, w22, #0x3, lsl #12"),
 0x1d908:("cmp","w10, #0x1c"),
 0x1d920:("br","x8"),
}
def must(ok,reason):
    if not ok:raise AssertionError("E004OI_FAIL_CLOSED "+reason)
def pdata(data):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    must(data[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",data,pe+4)[0]==0xaa64,"original ARM64 PE")
    head=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    for i in range(struct.unpack_from("<H",data,pe+6)[0]):
        o=head+i*40
        if data[o:o+8].rstrip(b"\0")==b".pdata":
            v,r,rs,raw=struct.unpack_from("<IIII",data,o+8)
            b=data[raw:raw+rs]
            return sorted(set(struct.unpack_from("<I",b,k)[0] for k in range(0,len(b)-7,8)))
    raise AssertionError("original PE missing .pdata")
def result():
    return {
      "schema":"sp11-e004oi-original-IFE-selectable-resource-callback-BF-port-static-v1",
      "parent_git_revision":"f94618a4b030a5fd0d6d53d206894dc7100f4efb",
      "original_same_SP11_OEM_ISP_SHA256":SHA,
      "original_ARM64_instruction_anchors":len(ANCHORS),
      "source_selected_IFE_callback_context_field_offset":0x6b688,
      "source_conditional_selector_state_field_offset":0x6b678,
      "normal_or_nonzero_state_callback_first_RVA":"0x1c0f0",
      "alternate_or_zero_state_callback_first_RVA":"0x1d830",
      "resource_selector_instruction_RVA":"0x19fe0",
      "callback_record_write_RVA":"0x19fe8",
      "bounded_0x805_IFE_per_resource_loop_RVA":"0x27278",
      "resource_loop_callback_load_RVA":"0x272e4",
      "resource_loop_callback_indirect_call_RVA":"0x27300",
      "resource_loop_passes_stop_flag_zero":True,
      "alternate_callback_explicit_BF_resource_port_0x300d_branch_RVA":"0x1d850",
      "alternate_callback_0x300d_compares_its_resource_ID_with_first_selector_param":True,
      "selected_callbacks_are_distinct_original_ARM64_PE_function_entries":True,
      "actual_live_rear4k_windows_selected_zero_or_nonzero_callback_state_known":False,
      "actual_0x300d_branch_executed_on_live_rear4k_known":False,
      "alternate_BF_resource_callback_proves_WM16_dma_retired":False,
      "normal_callback_no_BF_completed_in_live_rear4k_proven":False,
      "per_profile_resource_0x3022_active_list_and_MMIO_stop_acks_fully_decoded":False,
      "Windows_live_rear_BF_event_0x0f_observed":False,
      "Linux_native_rear4k_ISP_optical_frame_proven":False,
      "Golden_camera_device_or_boot_modified":False,
      "original_OEM_binary_raw_disassembly_optical_pixels_DMA_addresses_or_KD_exported":False,
    }
def validate(x):
    must(x==result(),"saved derived source facts vs unverified claims")
if __name__=="__main__":
    data=ISP.read_bytes()
    must(hashlib.sha256(data).hexdigest()==SHA,"original same-SP11 OEM SHA")
    src=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//",1)[0].strip()) for m in rx.finditer(src)}
    for rva,want in ANCHORS.items():
        must(asm.get(rva)==want,"original instruction RVA0x%x %s vs %s"%(rva,asm.get(rva),want))
    fun=pdata(data)
    for entry in (0x1c0f0,0x1d830,0x27278):
        k=bisect.bisect_right(fun,entry)-1
        must(k>=0 and fun[k]==entry,"original ARM64 function entry RVA0x%x"%entry)
    j=result();p=HERE/"RESULT.json"
    if p.exists():must(json.loads(p.read_text())==j,"saved source output changed")
    else:p.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    neg=(
      ("false_original_SHA",lambda v:v.__setitem__("original_same_SP11_OEM_ISP_SHA256","0"*64)),
      ("false_callback_offset",lambda v:v.__setitem__("source_selected_IFE_callback_context_field_offset",0x6b690)),
      ("wrong_zero_handler",lambda v:v.__setitem__("alternate_or_zero_state_callback_first_RVA","0x1c0f0")),
      ("fake_same_callbacks",lambda v:v.__setitem__("normal_or_nonzero_state_callback_first_RVA","0x1d830")),
      ("false_resource_dispatch",lambda v:v.__setitem__("resource_loop_callback_load_RVA","0x272e0")),
      ("false_BF_identity",lambda v:v.__setitem__("alternate_callback_explicit_BF_resource_port_0x300d_branch_RVA","0x1d854")),
      ("fake_no_stop_zero",lambda v:v.__setitem__("resource_loop_passes_stop_flag_zero",False)),
      ("invented_live_selection",lambda v:v.__setitem__("actual_live_rear4k_windows_selected_zero_or_nonzero_callback_state_known",True)),
      ("invented_BF_branch_execution",lambda v:v.__setitem__("actual_0x300d_branch_executed_on_live_rear4k_known",True)),
      ("fake_BF_DMA",lambda v:v.__setitem__("alternate_BF_resource_callback_proves_WM16_dma_retired",True)),
      ("fake_normal_BF",lambda v:v.__setitem__("normal_callback_no_BF_completed_in_live_rear4k_proven",True)),
      ("fake_MMIO_ack",lambda v:v.__setitem__("per_profile_resource_0x3022_active_list_and_MMIO_stop_acks_fully_decoded",True)),
      ("fake_live_0x0f",lambda v:v.__setitem__("Windows_live_rear_BF_event_0x0f_observed",True)),
      ("fake_linux_4k",lambda v:v.__setitem__("Linux_native_rear4k_ISP_optical_frame_proven",True)),
      ("fake_Golden_edit",lambda v:v.__setitem__("Golden_camera_device_or_boot_modified",True)),
      ("fake_private_export",lambda v:v.__setitem__("original_OEM_binary_raw_disassembly_optical_pixels_DMA_addresses_or_KD_exported",True)),
    )
    for name,m in neg:
        z=copy.deepcopy(j);m(z)
        try:validate(z)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OI_FAIL_OPEN_NEGATIVE "+name)
    print(f"PASS_E004OI_SOURCE_PINNED_IFE_RESOURCE_CALLBACK_SELECTION_{len(ANCHORS)}_ARM64_ANCHORS_"
          f"{len(neg)}_FAIL_CLOSED_NEGATIVES_ALTERNATE_PORT_0x300d_STATIC_ONLY_"
          "NO_LIVE_WM16_COMPLETION_OR_NATIVE_REAR4K_PROVEN_GOLDEN_SAFE")
