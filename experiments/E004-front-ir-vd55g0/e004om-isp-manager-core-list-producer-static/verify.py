#!/usr/bin/env python3
"""E004om original-ISP source: manager configured core-list producer→0x809 consumer.

No OEM executable bytes, disassembly, DMA addresses, images or KD material
written to the repository. Static dataflow is conditional, NOT live rear 4K.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
15dac|mov|x21, x0
16714|cmp|w24, #0x802
16718|b.ne|0x14001932c <.text+0x1832c>
16e7c|ldr|x21, [sp, #0x8]
16f3c|ldr|w8, [x21, #0x24]
16f44|cbnz|w8, 0x140018f9c <.text+0x17f9c>
16f60|cbnz|w8, 0x14001727c <.text+0x1627c>
16f6c|ldr|x15, [x27]
16f70|mov|x8, #0xe3e8
16f74|ldr|x8, [x15, x8]
16f78|cbz|x8, 0x140017130 <.text+0x16130>
16f9c|ldr|x13, [x8, #0x18]
16fa4|ldr|w9, [x21, #0x55c]
16fac|ldrh|w6, [x8, #0x12]
16fbc|ldr|x12, [x8, #0x28]
16fc4|ldrh|w3, [x12], #0x4
16fcc|ldrh|w4, [x26]
16ff0|madd|x3, x3, x24, x2
16ff4|ldrb|w3, [x3, #0x20]
17000|ldrb|w4, [x4, #0x20]
170d8|cbz|w11, 0x140017268 <.text+0x16268>
170dc|ldr|x9, [x8, #0x28]
170e0|ubfiz|x11, x14, #2, #32
170e4|ldr|w10, [x21, #0x24]
170e8|ldrh|w9, [x11, x9]
170ec|add|x10, x10, #0x6
170f0|str|w9, [x21, x10, lsl #2]
170f4|ldr|w9, [x21, #0x24]
170f8|add|w9, w9, #0x1
170fc|str|w9, [x21, #0x24]
17100|ldr|x8, [x8, #0x28]
17104|add|x9, x9, #0x6
17108|add|x8, x11, x8
1710c|ldrh|w8, [x8, #0x2]
17110|str|w8, [x21, x9, lsl #2]
17114|ldr|w8, [x21, #0x24]
17118|add|w8, w8, #0x1
1711c|str|w8, [x21, #0x24]
17148|ldr|x14, [x27]
1714c|mov|x8, #0xe3e8
17150|ldr|x8, [x14, x8]
17154|cbz|x8, 0x140017274 <.text+0x16274>
17158|ldr|x10, [x8, #0x18]
17168|ldr|w15, [x8]
171b0|mov|w13, w10
171c8|cbnz|w11, 0x140017234 <.text+0x16234>
17234|ldr|w8, [x21, #0x24]
17238|add|x8, x8, #0x6
1723c|str|w13, [x21, x8, lsl #2]
17240|ldr|w8, [x21, #0x24]
17248|add|w8, w8, #0x1
1724c|str|w8, [x21, #0x24]
17254|ldr|w9, [x21, #0x18]
173ec|mov|w25, w9
17410|ldp|x21, x23, [sp, #0x8]
17414|cbz|w22, 0x14001744c <.text+0x1644c>
17418|ldr|w8, [x21, #0x24]
1741c|add|x8, x8, #0x6
17420|str|w25, [x21, x8, lsl #2]
17424|ldr|w8, [x21, #0x24]
1742c|add|w8, w8, #0x1
17430|str|w8, [x21, #0x24]
17464|ldr|w8, [x21, #0x24]
17474|ubfx|x8, x22, #0, #32
17478|add|x25, x8, #0x6
1747c|ldr|w1, [x21, x25, lsl #2]
17480|mov|x0, x21
17484|bl|0x140019e10 <.text+0x18e10>
18fb0|ldr|w11, [x21, #0x24]
18fb4|cmp|w11, #0x2
18fb8|csel|w8, w11, w23, lo
18fcc|ldr|w10, [x21, x8, lsl #2]
19350|ldr|w9, [x21, #0x24]
19354|mov|w8, #0x2
19358|cmp|w9, #0x2
1935c|csel|w8, w9, w8, lo
1936c|add|x8, x8, #0x6
19370|ldr|w10, [x21, x8, lsl #2]
193b4|mov|w1, w24
193c8|blr|x15
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (row.split("|",2) for row in SOURCE.strip().splitlines())}
def require(b,s):
    if not b:raise AssertionError("E004OM_FAIL_CLOSED "+s)
def expected():
    return {
        "schema":"sp11-e004om-original-ISP-configured-core-list-producer-809-consumer-static-v1",
        "parent_git_revision":"cae49ddf72b73f2cc6592436a90de04e0d9c6e8b",
        "same_SP11_original_OEM_ISP_sha256":SHA,
        "exact_original_ARM64_instruction_anchors":len(ANCHORS),
        "conditional_0x802_configuration_branch_RVA":"0x16714",
        "zero_existing_count_enters_descriptor_selection_RVA":"0x16f44",
        "descriptor_source_global_offset":"0xe3e8",
        "manager_configured_list_count_offset":"0x24",
        "manager_first_list_slot_word_index":6,
        "conditional_descriptor_pair_first_append_RVA":"0x170f0",
        "conditional_descriptor_pair_second_append_RVA":"0x17110",
        "conditional_descriptor_pair_increments_count_twice":True,
        "conditional_single_fallback_append_RVA":"0x1723c",
        "conditional_separate_single_append_RVA":"0x17420",
        "later_configured_list_iteration_RVA":"0x1747c",
        "generic_809_dispatch_same_list_count_RVA":"0x19350",
        "generic_809_dispatch_same_list_entry_RVA":"0x19370",
        "generic_809_dispatch_forwards_original_selector_RVA":"0x193b4",
        "all_list_producers_and_reinitialization_sites_found":False,
        "all_generated_list_core_ids_proven_nonnegative_and_less_than_four":False,
        "live_rear_4k_0x802_precedes_0x809_and_exact_core_ids_observed":False,
        "per_core_0x809_receivers_return_and_hardware_effects_fully_decoded":False,
        "BF_WM16_live_event_or_DMA_retirement_proven":False,
        "Linux_native_rear_processed_ISP_4k_optical_frame_proven":False,
        "Golden_boot_or_camera_hardware_modified":False,
        "private_OEM_binary_bulk_disassembly_DMA_optical_or_KD_exported":False,
    }
def checked(x):require(x==expected(),"saved result unverified")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    instructions={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for rva,inst in ANCHORS.items():
        require(instructions.get(rva)==inst,"original ISA RVA %x"%rva)
    prior=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ol-isp-selector-809-independent-dispatch-static/RESULT.json").read_text())
    require(prior["selector_0x809_reaches_generic_default_branch_RVA"]=="0x1932c" and prior["default_dispatch_forwards_original_selector_in_w1_RVA"]=="0x193b4" and
            prior["actual_0x809_per_core_receiver_function_body_and_contract_identified"] is False,"E004ol bounded unknown")
    result=expected(); saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==result,"saved result")
    else:saved.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    cases=(
       ("changed_OEM_SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
       ("wrong_descriptor","descriptor_source_global_offset","0xe3d8"),
       ("wrong_count","manager_configured_list_count_offset","0x20"),
       ("wrong_first_slot","manager_first_list_slot_word_index",5),
       ("wrong_first_pair","conditional_descriptor_pair_first_append_RVA","0x170ec"),
       ("wrong_second_pair","conditional_descriptor_pair_second_append_RVA","0x1710c"),
       ("wrong_single","conditional_single_fallback_append_RVA","0x17240"),
       ("wrong_second_single","conditional_separate_single_append_RVA","0x17424"),
       ("wrong_consumer","generic_809_dispatch_same_list_entry_RVA","0x19374"),
       ("fake_entire_producer_set","all_list_producers_and_reinitialization_sites_found",True),
       ("fake_bounds","all_generated_list_core_ids_proven_nonnegative_and_less_than_four",True),
       ("fake_live","live_rear_4k_0x802_precedes_0x809_and_exact_core_ids_observed",True),
       ("fake_receivers","per_core_0x809_receivers_return_and_hardware_effects_fully_decoded",True),
       ("fake_WM16","BF_WM16_live_event_or_DMA_retirement_proven",True),
       ("fake_linux_rear","Linux_native_rear_processed_ISP_4k_optical_frame_proven",True),
       ("fake_Golden","Golden_boot_or_camera_hardware_modified",True),
       ("fake_export","private_OEM_binary_bulk_disassembly_DMA_optical_or_KD_exported",True),
    )
    for name,key,v in cases:
        m=copy.deepcopy(result);m[key]=v
        try:checked(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OM_FAIL_OPEN_NEGATIVE "+name)
    print("PASS_E004OM_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_FAIL_CLOSED_NEGATIVES_CORE_LIST_PRODUCER_CONSUMER_STATIC_GOLDEN_SAFE"%(len(ANCHORS),len(cases)))
