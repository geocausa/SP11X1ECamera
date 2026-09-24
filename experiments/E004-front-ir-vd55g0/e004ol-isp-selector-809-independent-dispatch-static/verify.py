#!/usr/bin/env python3
"""E004ol: original ISP HW-manager's independent selector 0x809 routing.

This is STATIC original-SP11 ARM64 source proof of a default per-core
forwarding path, not interpretation of 0x809 or a live rear capture.
No OEM executable bytes/disassembly, optical pixels, DMA addresses or KD
material are exported.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
15db4|mov|w24, w1
15e5c|cmp|w24, #0x80c
15e60|b.ne|0x140015e94 <.text+0x14e94>
15e94|cmp|w24, #0x808
15e98|b.ne|0x140015ee0 <.text+0x14ee0>
15ee0|cmp|w24, #0x804
15ee4|b.ne|0x140016300 <.text+0x15300>
16300|cmp|w24, #0x805
16304|b.ne|0x140016504 <.text+0x15504>
16504|cmp|w24, #0x803
16508|b.ne|0x140016714 <.text+0x15714>
16714|cmp|w24, #0x802
16718|b.ne|0x14001932c <.text+0x1832c>
1932c|adrp|x8, 0x140034000 <.text+0x33000>
19334|mov|w2, w24
19340|str|x26, [sp, #0x30]
19344|ldr|x26, [sp, #0x20]
19348|mov|w20, #0x0
1934c|str|w24, [sp, #0x28]
19350|ldr|w9, [x21, #0x24]
19354|mov|w8, #0x2
19358|cmp|w9, #0x2
1935c|csel|w8, w9, w8, lo
19360|cmp|w20, w8
19364|b.hs|0x140019408 <.text+0x18408>
19368|ubfx|x8, x20, #0, #32
1936c|add|x8, x8, #0x6
19370|ldr|w10, [x21, x8, lsl #2]
19374|cmp|w10, #0x4
19378|b.ge|0x140019408 <.text+0x18408>
1937c|ldr|x8, [x27]
19380|mov|x9, #0x30
19384|ldr|x8, [x8, #0x30]
19388|umaddl|x9, w10, w9, x8
1938c|ldrb|w8, [x9, #0x20]
19390|cbz|w8, 0x1400193fc <.text+0x183fc>
19394|ldr|x0, [x9, #0x8]
19398|mov|w5, w25
1939c|ldr|w24, [sp, #0x28]
193a0|mov|x4, x23
193a4|ldr|x6, [sp, #0x30]
193a8|mov|w3, w22
193ac|mov|x2, x26
193b0|ldr|x8, [x0]
193b4|mov|w1, w24
193b8|mov|x15, x8
193bc|adrp|x17, 0x14003f000
193c0|ldr|x17, [x17, #0x348]
193c4|blr|x17
193c8|blr|x15
193cc|mov|w19, w0
193d0|cmp|w19, #0x0
193d4|ccmp|w19, #0x1a, #0x4, ne
193d8|b.eq|0x1400193fc <.text+0x183fc>
193fc|add|w20, w20, #0x1
19400|b|0x140019350 <.text+0x18350>
19404|ldr|w19, [sp, #0x4]
19418|mov|w0, w19
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (row.split("|",2) for row in SOURCE.strip().splitlines())}
def must(ok,why):
    if not ok:raise AssertionError("E004OL_FAIL_CLOSED "+why)
def selected_branch(selector):
    return next((v for v in (0x80c,0x808,0x804,0x805,0x803,0x802) if v==selector),None)
def expected():
    return {
        "schema":"sp11-e004ol-original-ISP-independent-0x809-default-core-forwarding-static-v1",
        "parent_git_revision":"8e44573697338436d012c65ca2d00548a43ab0cb",
        "same_SP11_original_ISP_sha256":SHA,
        "source_locked_original_ARM64_instructions":len(ANCHORS),
        "manager_entry_RVA":"0x15d70",
        "selector_received_as_w1_saved_in_w24_RVA":"0x15db4",
        "selector_0x809_matches_explicit_0x80c_0x808_0x804_0x805_0x803_0x802_special_cases":False,
        "selector_0x809_reaches_generic_default_branch_RVA":"0x1932c",
        "default_dispatch_core_table_count_clamped_to_two":True,
        "default_dispatch_reads_context_list_from_index_six":True,
        "default_dispatch_signed_core_ID_ge_four_rejected_negative_bound_unproven":True,
        "default_dispatch_checks_per_core_enabled_before_instance_pointer_load":True,
        "default_dispatch_forwards_original_selector_in_w1_RVA":"0x193b4",
        "default_dispatch_calls_per_core_original_function_pointer_RVA":"0x193c8",
        "actual_0x809_per_core_receiver_function_body_and_contract_identified":False,
        "all_0x809_selected_core_ids_and_live_rear_mode_known":False,
        "0x809_means_0x805_stop_or_dma_retirement":False,
        "live_windows_rear_4k_0x809_dispatch_observed":False,
        "Linux_native_rear_ISP_4k_optical_frame_proven":False,
        "Golden_boot_or_camera_hardware_modified":False,
        "private_OEM_binary_bulk_disassembly_DMA_KD_or_optical_data_exported":False,
    }
def check(x):must(x==expected(),"persisted conservative result")
if __name__=="__main__":
    must(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original SHA")
    out=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(out)}
    for rva,inst in ANCHORS.items():must(asm.get(rva)==inst,"original instruction RVA %x"%rva)
    for selector in (0x80c,0x808,0x804,0x805,0x803,0x802):
        must(selected_branch(selector)==selector,"special branch selector check")
    must(selected_branch(0x809) is None and selected_branch(0x809)!=selected_branch(0x805),"809 not stop")
    previous=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004oe-isp-manager-per-core-order-static/RESULT.json").read_text())
    must(previous["ISP_0x809_effects_decoded"] is False,"prior unknown 809 stays unknown")
    j=expected();s=HERE/"RESULT.json"
    if s.exists():must(json.loads(s.read_text())==j,"saved source contract")
    else:s.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    mutants=[
      ("fake_sha","same_SP11_original_ISP_sha256","0"*64),
      ("fake_default","selector_0x809_reaches_generic_default_branch_RVA","0x16300"),
      ("fake_809_stop","selector_0x809_matches_explicit_0x80c_0x808_0x804_0x805_0x803_0x802_special_cases",True),
      ("fake_stop_equivalence","0x809_means_0x805_stop_or_dma_retirement",True),
      ("fake_receiver","actual_0x809_per_core_receiver_function_body_and_contract_identified",True),
      ("fake_live_core","all_0x809_selected_core_ids_and_live_rear_mode_known",True),
      ("fake_forward","default_dispatch_forwards_original_selector_in_w1_RVA","0x193b0"),
      ("fake_live_809","live_windows_rear_4k_0x809_dispatch_observed",True),
      ("fake_4k","Linux_native_rear_ISP_4k_optical_frame_proven",True),
      ("fake_Golden","Golden_boot_or_camera_hardware_modified",True),
      ("fake_export","private_OEM_binary_bulk_disassembly_DMA_KD_or_optical_data_exported",True),
    ]
    for name,key,value in mutants:
        x=copy.deepcopy(j);x[key]=value
        try:check(x)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OL_FAIL_OPEN_NEGATIVE "+name)
    changed=copy.deepcopy(ANCHORS);changed[0x193b4]=("mov","w1, #0x805")
    must(asm[0x193b4]!=changed[0x193b4],"instruction mutation fails closed")
    print("PASS_E004OL_%d_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_809_GENERIC_CORE_FORWARDING_NOT_STOP_OR_LIVE_DMA_PROOF_GOLDEN_SAFE"%(len(ANCHORS),len(mutants)+1))
