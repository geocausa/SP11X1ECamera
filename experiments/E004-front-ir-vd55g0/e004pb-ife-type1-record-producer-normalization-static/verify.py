#!/usr/bin/env python3
"""E004pb exact original type-1 producer and status-word normalization.

Same-SP11 read-only original ISP. All evidence static; original upstream
snapshot invoker/live rear4k selected mode/actual hardware IRQ/DMA unproven.
Only safe scalar RVAs/offsets and bounded original ISA anchors in Git.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ISP = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA = "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE = 0x140000000
SOURCE = """
178e0|adrp|x9, 0x140024000 <.text+0x23000>
178e4|add|x10, x9, #0x380
178e8|adrp|x9, 0x140067000
178ec|str|x10, [x9, #0x148]
178f4|adrp|x9, 0x140024000 <.text+0x23000>
178f8|add|x10, x9, #0x3d0
178fc|adrp|x9, 0x140067000
17900|str|x10, [x9, #0x138]
17d98|ldr|w11, [x11, #0xe28]
17d9c|cmp|w11, #0x0
17e44|adrp|x11, 0x140020000 <.text+0x1f000>
17e48|add|x12, x11, #0xce0
17e4c|adrp|x11, 0x14001b000 <.text+0x1a000>
17e50|add|x11, x11, #0x7d0
17e54|csel|x11, x12, x11, ne
17e58|str|x11, [x8, #0x208]
21478|cbz|x21, 0x140021b98 <.text+0x20b98>
2147c|ldr|w8, [x21, #0x10]
2149c|cmp|w8, #0x2
214a4|ldr|x8, [x21]
214a8|str|x8, [x19, #0x198]
214ac|ldr|x8, [x21, #0x8]
214b0|str|x8, [x19, #0x1a0]
243d0|pacibsp|
243e8|mov|x20, x0
243ec|mov|x22, x1
243f0|str|q16, [sp, #0x10]
24414|ldr|w3, [x20, #0x28]
24418|cmp|w3, #0x1
2441c|b.eq|0x14002443c <.text+0x2343c>
2443c|ldr|x19, [x20, #0x1b0]
24458|ldr|w8, [x19, #0x18]
24460|ldr|w11, [x19, #0x2c]
24464|add|x0, sp, #0x18
24468|ldr|w10, [x19, #0x14]
2446c|ldr|x8, [x19]
24474|madd|x2, x10, x11, x8
24478|sxtw|x1, w10
2447c|bl|0x14002c5b0 <.text+0x2b5b0>
244c8|ldr|x2, [sp, #0x18]
244cc|cbnz|x2, 0x1400244e4 <.text+0x234e4>
244e4|mov|w8, #0x1
244e8|str|w8, [sp, #0x10]
244ec|ldr|x8, [x20, #0x208]
244f0|mov|x1, x22
244f4|mov|x0, x20
244f8|mov|x21, x2
2450c|blr|x15
24510|mov|x2, x21
24514|ldaxr|w8, [x2]
24518|add|w8, w8, #0x1
2451c|stlxr|w17, w8, [x2]
24520|cbnz|w17, 0x140024514 <.text+0x23514>
24524|dmb|ish
2461c|ldr|x19, [x20, #0x198]
2463c|ldr|w8, [x19, #0x10]
24640|cmp|w9, w8
24648|ldr|w11, [x19, #0x30]
2464c|add|x2, sp, #0x10
24650|ldr|w10, [x19, #0x14]
24654|ldr|x8, [x19]
2465c|madd|x0, x10, x11, x8
24660|sxtw|x1, w10
24664|bl|0x14002c5b0 <.text+0x2b5b0>
24668|ldr|w8, [x19, #0x18]
2466c|add|w8, w8, #0x1
24670|str|w8, [x19, #0x18]
246c0|ldr|x0, [x20, #0x1a0]
246c4|adrp|x8, 0x14003f000
246c8|ldr|x8, [x8, #0x2e8]
246d4|blr|x8
20ce0|ldr|w8, [x1, #0x4]
20ce4|str|w8, [x2, #0x4]
20ce8|ldr|w8, [x1, #0x8]
20cec|str|w8, [x2, #0xc]
20cf0|ldr|w8, [x1, #0x10]
20cf4|str|w8, [x2, #0x10]
20cf8|ldr|w8, [x1, #0xc]
20cfc|str|w8, [x2, #0x8]
20d00|ldr|x8, [x0, #0x8]
20d04|ldr|w9, [x8, #0x398]
20d0c|ldr|w8, [x8, #0x39c]
20d10|bfi|x9, x8, #32, #24
20d14|str|x9, [x2, #0x28]
20d20|ret|
1b7d0|ldr|w8, [x1, #0x4]
1b7d4|str|w8, [x2, #0x4]
1b7d8|ldr|w8, [x1, #0x8]
1b7dc|str|w8, [x2, #0xc]
1b7e0|ldr|w8, [x1, #0x10]
1b7e4|str|w8, [x2, #0x10]
1b7e8|ldr|w8, [x1, #0x14]
1b7ec|str|w8, [x2, #0x14]
1b7f0|ldr|w8, [x1, #0xc]
1b7f4|str|w8, [x2, #0x8]
1b818|ldr|w8, [x1, #0x28]
1b81c|str|w8, [x2, #0x28]
1b820|ret|
19fa8|add|x8, x19, #0x6b, lsl #12
19fac|ldr|w8, [x8, #0x678]
19fb0|cmp|w8, #0x0
1a05c|adrp|x8, 0x14001c000 <.text+0x1b000>
1a060|add|x9, x8, #0x2b0
1a064|adrp|x8, 0x14001d000 <.text+0x1c000>
1a068|add|x8, x8, #0xc20
1a06c|csel|x9, x9, x8, ne
1a074|str|x9, [x8, #0x6b0]
1c2d0|ldr|w8, [x8, #0x1c]
1c2d4|str|w8, [x20, #0x4]
1c2dc|ldr|w8, [x8, #0x20]
1c2e0|str|w8, [x20, #0x8]
1c2e8|ldr|w8, [x8, #0x28]
1c2ec|str|w8, [x20, #0xc]
1dc40|ldr|w8, [x8, #0x44]
1dc44|str|w8, [x20, #0x4]
1dc4c|ldr|w8, [x8, #0x48]
1dc50|str|w8, [x20, #0x8]
1dc58|ldr|w8, [x8, #0x28]
1dc5c|str|w8, [x20, #0xc]
1dc64|ldr|w8, [x8, #0x2c]
1dc68|str|w8, [x20, #0x10]
1efd8|cmp|w8, #0x1
1efe8|ldr|x23, [x20, #0x8]
1eff0|ldp|w8, w2, [x23, #0x4]
1f048|ubfx|w15, w2, #7, #1
1f188|cbz|w15, 0x14001f19c <.text+0x1e19c>
1f190|mov|w15, #0xf
1fc8c|mov|w1, #0x8
1fc94|bl|0x140026460 <.text+0x25460>
"""
ANCHORS={int(a,16):(op,arg) for a,op,arg in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def require(ok,why):
    if not ok:raise AssertionError("E004PB_FAIL_CLOSED "+why)
def source_format(image,extended=False):
    """Offline synthetic exact dataflow of the two SOURCE-locked copy handlers."""
    require(all(k in image for k in (4,8,12,16)),"input fields available")
    out={4:image[4],8:image[12],12:image[8],16:image[16]}
    if extended:
        require(all(k in image for k in (20,40)),"extended source fields available")
        out[20]=image[20];out[40]=image[40]
    return out
def facts():
    return {
      "schema":"sp11-e004pb-original-type1-producer-swapped-status-words-BF_source_c_not_8-static-v1",
      "parent_git_revision":"779e77ef89284b6aeeb37e8b5b09c584dc04b763",
      "original_same_SP11_OEM_ISP_sha256":SHA,
      "original_exact_ARM64_instruction_anchors":len(ANCHORS),
      "registered_type_one_record_callback_RVA":"0x243d0",
      "original_registered_type_one_global_slot_RVA":"0x67138",
      "registered_status_snapshot_wrapper_global_slot_RVA":"0x67140",
      "registered_type_two_external_global_slot_RVA":"0x67150",
      "type_one_local_event_record_stamp_RVA":"0x244e8",
      "type_one_event_record_object_pointer_stack_offset":"0x18",
      "type_one_event_local_record_stack_offset":"0x10",
      "type_one_record_object_pool_context_offset":"0x1b0",
      "type_one_per_context_normalization_callback_offset":"0x208",
      "normalizer_nonzero_select_condition_offset":"0xe28",
      "normalizer_nonzero_select_RVA":"0x20ce0",
      "normalizer_zero_select_RVA":"0x1b7d0",
      "both_normalizers_source_word_offsets":[4,8,12,16],
      "both_normalizers_destination_word_offsets_for_source_4_8_c_10":[4,12,8,16],
      "type_one_BF_handler_second_status_word_object_offset":"0x8",
      "type_one_BF_status_bit":7,
      "type_one_BF_event_id":"0x0f",
      "type_one_BF_FIFO_group":8,
      "if_exact_modezero_snapshot_is_input_type_one_BF_word_source":"snapshot+0x0c_original_mode_zero_BUS_status0",
      "if_exact_nonzero_snapshot_is_input_type_one_BF_word_source":"snapshot+0x0c_original_mode_nonzero_BUS_status0",
      "previous_direct_TOP_status1_bit7_to_BF_record_inference_valid_after_normalization":False,
      "type_one_event_enqueue_software_ring_context_offset":"0x198",
      "type_one_event_work_notify_context_offset":"0x1a0",
      "type_two_worker_device_event_ring_offset":"0x8",
      "type_one_event_ring_identity_to_existing_type_two_worker_device_0x8_proven":False,
      "type_one_event_source_input_proven_from_registered_IFE_snapshot_wrapper":False,
      "type_one_normalizer_condition_proven_same_as_selected_IFE_mode_0x6b678":False,
      "actual_live_rear4k_selected_IFE_mode_or_BF_event_observed":False,
      "actual_native_Linux_rear_VFE_irq_ack_FIFO8_WM16_per_generation_DMA_retirement_proven":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_proven":False,
      "protected_Golden_boot_camera_kernel_modified":False,
      "OEM_private_binary_bulk_disassembly_physical_DMA_KD_optical_exported":False,
    }
def strict(data):require(data==facts(),"scalar source-evidence claim altered")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for r,expected in ANCHORS.items():require(ins.get(r)==expected,"original ISA RVA %x"%r)
    # Counterexample to earlier assumption: if input +8 TOP1 and +c BUS0
    # are distinct, normalized type1 consumer +8 is BUS0, not TOP1.
    sample={4:0x11111111,8:0x22222222,12:0x33333380,16:0x44444444,20:0x55555555,40:0x66666666}
    for ext in (False,True):
        output=source_format(sample,ext)
        require(output[8]==sample[12] and output[8]!=sample[8] and
                output[12]==sample[8] and ((output[8]>>7)&1)==1 and
                ((sample[8]>>7)&1)==0,
                "selected original normalizer swaps second status word")
    pa=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pa-ife-dual-mode-top-irq-layout-static/RESULT.json").read_text())
    require(pa["original_mode_zero_TOP_status_offsets"]==["0x44","0x48"] and
            pa["original_mode_nonzero_TOP_status_offsets"]==["0x1c","0x20"] and
            pa["original_snapshot_TO_type_one_event_pointer_identity_proven"] is False,
            "prior matched snapshot record layout was not type1 producer lineage")
    oz=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004oz-original-ife-dual-callback-registration-static/RESULT.json").read_text())
    require(oz["original_snapshot_TO_type_one_buffer_pointer_identity_proven"] is False,
            "prior callback registration not direct type1 buffer identity")
    data=facts();saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==data,"saved scalar evidence changed")
    else:saved.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    muts=(
      ("sha","original_same_SP11_OEM_ISP_sha256","0"*64),
      ("callback","registered_type_one_record_callback_RVA","0x24a30"),
      ("slot","original_registered_type_one_global_slot_RVA","0x67140"),
      ("stamp","type_one_local_event_record_stamp_RVA","0x24b80"),
      ("ring","type_one_event_enqueue_software_ring_context_offset","0x8"),
      ("object","type_one_record_object_pool_context_offset","0x33c8"),
      ("normalize","type_one_per_context_normalization_callback_offset","0x6b6b0"),
      ("nonzero_func","normalizer_nonzero_select_RVA","0x1b7d0"),
      ("zero_func","normalizer_zero_select_RVA","0x20ce0"),
      ("normalize_source","both_normalizers_source_word_offsets",[4,8,16,12]),
      ("normalize_destination","both_normalizers_destination_word_offsets_for_source_4_8_c_10",[4,8,12,16]),
      ("BF_offset","type_one_BF_handler_second_status_word_object_offset","0xc"),
      ("BF_bit","type_one_BF_status_bit",21),
      ("BF_FIFO","type_one_BF_FIFO_group",0),
      ("snapshot0","if_exact_modezero_snapshot_is_input_type_one_BF_word_source","snapshot+0x08_TOP_status1"),
      ("snapshot1","if_exact_nonzero_snapshot_is_input_type_one_BF_word_source","snapshot+0x08_TOP_status1"),
      ("fake_top","previous_direct_TOP_status1_bit7_to_BF_record_inference_valid_after_normalization",True),
      ("fake_ring","type_one_event_ring_identity_to_existing_type_two_worker_device_0x8_proven",True),
      ("fake_upstream","type_one_event_source_input_proven_from_registered_IFE_snapshot_wrapper",True),
      ("fake_mode","type_one_normalizer_condition_proven_same_as_selected_IFE_mode_0x6b678",True),
      ("fake_live","actual_live_rear4k_selected_IFE_mode_or_BF_event_observed",True),
      ("fake_DMA","actual_native_Linux_rear_VFE_irq_ack_FIFO8_WM16_per_generation_DMA_retirement_proven",True),
      ("fake_optical","native_Linux_rear_processed_hardware_ISP_4k_optical_proven",True),
      ("fake_golden","protected_Golden_boot_camera_kernel_modified",True),
      ("fake_private","OEM_private_binary_bulk_disassembly_physical_DMA_KD_optical_exported",True),
    )
    for name,key,val in muts:
        mutated=copy.deepcopy(data);mutated[key]=val
        try:strict(mutated)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PB_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004PB_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_TYPE1_PRODUCER_WORD_REORDER_REVOKES_DIRECT_TOP1_BF_MAPPING_HW_DMA_UNPROVEN_GOLDEN_SAFE"%(len(ANCHORS),len(muts)))
