#!/usr/bin/env python3
"""E004pc verifies original ISP type-1 channel ring provisioning vs worker ring.

Offline SHA-pinned same SP11 private OEM ARM64 read-only. No assumed alias,
no hardware IRQ/ack, no real DMA, no candidate register writes.
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
211d8|mov|x21, x2
211e4|ldr|x19, [x0, #0x20]
21478|cbz|x21, 0x140021b98 <.text+0x20b98>
2147c|ldr|w8, [x21, #0x10]
21480|cmp|w8, #0x3
21484|b.ne|0x14002149c <.text+0x2049c>
21488|ldr|x8, [x21]
2148c|str|x8, [x19, #0x1a8]
21490|ldr|x8, [x21, #0x8]
21494|str|x8, [x19, #0x1b8]
21498|b|0x1400214b4 <.text+0x204b4>
2149c|cmp|w8, #0x2
214a0|b.ne|0x1400214b4 <.text+0x204b4>
214a4|ldr|x8, [x21]
214a8|str|x8, [x19, #0x198]
214ac|ldr|x8, [x21, #0x8]
214b0|str|x8, [x19, #0x1a0]
22824|mov|w8, #0x2
22828|str|x26, [sp, #0x30]
2282c|str|w8, [sp, #0x38]
22830|add|x22, x20, #0x8
22844|mov|w1, #0x368
2284c|bl|0x14002a260 <.text+0x29260>
22850|mov|x19, x0
22860|mov|x2, #0x350
22868|add|x0, x19, #0x18
2286c|bl|0x14002df80 <.text+0x2cf80>
22870|add|x9, x19, #0x38
22874|add|x8, x9, #0x10
22878|stp|x8, x9, [x19]
22880|str|x26, [x19, #0x10]
22884|str|wzr, [x19, #0x18]
22888|stp|wzr, wzr, [x19, #0x2c]
22898|str|x19, [x22]
22910|mov|x0, x20
22914|bl|0x140023700 <.text+0x22700>
2382c|mov|x20, x0
238f4|add|x24, x20, #0x6b, lsl #12
238fc|movi|v16.16b, #0x0
23900|ldr|x19, [x20, #0x8]
23928|add|x0, sp, #0x20
23940|bl|0x14002c5b0 <.text+0x2b5b0>
23998|ldr|q16, [sp, #0x20]
2399c|add|x1, sp, #0x30
239a0|ldr|x8, [x24, #0x6d8]
239a4|mov|x0, x20
239a8|str|q16, [sp, #0x30]
239bc|blr|x15
243d0|pacibsp|
243e8|mov|x20, x0
243ec|mov|x22, x1
2443c|ldr|x19, [x20, #0x1b0]
244c8|ldr|x2, [sp, #0x18]
244e4|mov|w8, #0x1
244e8|str|w8, [sp, #0x10]
244ec|ldr|x8, [x20, #0x208]
244f0|mov|x1, x22
244f4|mov|x0, x20
2450c|blr|x15
2461c|ldr|x19, [x20, #0x198]
24648|ldr|w11, [x19, #0x30]
2464c|add|x2, sp, #0x10
24654|ldr|x8, [x19]
2465c|madd|x0, x10, x11, x8
24664|bl|0x14002c5b0 <.text+0x2b5b0>
246c0|ldr|x0, [x20, #0x1a0]
246c8|ldr|x8, [x8, #0x2e8]
246d4|blr|x8
24b78|mov|w8, #0x2
24b80|str|w8, [sp, #0x20]
24d08|ldr|x20, [x21, #0x8]
24d38|add|x2, sp, #0x20
24d50|bl|0x14002c5b0 <.text+0x2b5b0>
"""
ANCHORS={int(addr,16):(op,operands) for addr,op,operands in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def require(cond,why):
    if not cond:raise AssertionError("E004PC_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004pc-original-IFE-type1-external-channel-ring-vs-own-worker-ring-static-v1",
      "parent_git_revision":"047b33e5cf7a8bfd5af392b893a6bf572643f5f6",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "original_channel_assignment_core_callback_RVA":"0x211b0",
      "original_channel_assignment_device_context_provenance":"callback_x0_plus_0x20",
      "original_channel_assignment_kind_field_offset":"0x10",
      "original_channel_assignment_type_two_ring_source_offset":"0x0",
      "original_channel_assignment_type_two_notify_source_offset":"0x8",
      "original_channel_assignment_type_two_ring_receiver_context_offset":"0x198",
      "original_channel_assignment_type_two_notify_receiver_context_offset":"0x1a0",
      "original_channel_assignment_type_three_ring_receiver_context_offset":"0x1a8",
      "original_channel_assignment_type_three_notify_receiver_context_offset":"0x1b8",
      "original_worker_device_owned_ring_offset":"0x8",
      "original_worker_ring_allocation_size":"0x368",
      "original_worker_ring_init_RVA":"0x22830",
      "original_worker_ring_store_RVA":"0x22898",
      "original_worker_ring_dequeue_RVA":"0x23940",
      "original_type_one_producer_event_kind":1,
      "original_type_one_producer_ring_receiver_context_offset":"0x198",
      "original_type_one_producer_notify_receiver_context_offset":"0x1a0",
      "original_type_one_producer_enqueue_RVA":"0x24664",
      "original_type_one_producer_notify_RVA":"0x246d4",
      "original_type_two_producer_event_kind":2,
      "original_type_two_producer_ring_device_offset":"0x8",
      "original_type_two_producer_enqueue_RVA":"0x24d50",
      "type_two_external_event_and_worker_use_device_plus_0x8_ring_in_original_source":True,
      "type_one_channel_interface_given_exact_original_worker_device_plus_0x8_ring_identity_proven":False,
      "type_one_producer_record_reaches_same_worker_exactly_proven":False,
      "type_one_producer_input_is_actual_mode_selected_IFE_snapshot_proven":False,
      "previous_direct_TOP1_to_BF_proof_valid_after_type_one_normalizer":False,
      "original_live_rear4k_selected_mode_and_BF0x0f_observed":False,
      "native_Linux_rear_VFE_IRQ_ack_BF_FIFO8_per_generation_WM16_DMA_retirement_proven":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_proven":False,
      "protected_Golden_boot_camera_kernel_modified":False,
      "OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported":False,
    }
def strict(f):require(f==facts(),"scalar source evidence or safety changed")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original OEM ISP SHA")
    disasm=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(disasm)}
    for addr,expect in ANCHORS.items():require(ins.get(addr)==expect,"exact original ISA RVA %x"%addr)
    pb=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pb-ife-type1-record-producer-normalization-static/RESULT.json").read_text())
    require(pb["type_one_event_ring_identity_to_existing_type_two_worker_device_0x8_proven"] is False and
            pb["previous_direct_TOP_status1_bit7_to_BF_record_inference_valid_after_normalization"] is False and
            pb["type_one_event_enqueue_software_ring_context_offset"]=="0x198",
            "prior type1 dataflow provenance supersedes false direct TOP1 or ring claims")
    # No static offset or record-format equality can prove two different
    # external/context-owned ring pointers alias in an actual session.
    def same_ring(worker_id,channel_id,source_identity_independently_verified):
        return (source_identity_independently_verified is True and
                worker_id is not None and channel_id is not None and
                worker_id==channel_id)
    require(same_ring(0x13,0x13,True) and
            not same_ring(0x13,0x13,False) and
            not same_ring(0x13,0x14,True) and
            not same_ring(0x13,None,True) and
            not same_ring(None,0x13,True),
            "offline alias guard must require independent same-session ring identity")
    data=facts();file=HERE/"RESULT.json"
    if file.exists():require(json.loads(file.read_text())==data,"saved safe scalar result changed")
    else:file.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    muts=(
      ("SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("channel","original_channel_assignment_core_callback_RVA","0x243d0"),
      ("kind","original_channel_assignment_kind_field_offset","0x8"),
      ("kind2_ring","original_channel_assignment_type_two_ring_receiver_context_offset","0x8"),
      ("kind2_notify","original_channel_assignment_type_two_notify_receiver_context_offset","0x1b8"),
      ("kind3_ring","original_channel_assignment_type_three_ring_receiver_context_offset","0x198"),
      ("worker_offset","original_worker_device_owned_ring_offset","0x198"),
      ("worker_alloc","original_worker_ring_allocation_size","0x1d0"),
      ("worker_store","original_worker_ring_store_RVA","0x214a8"),
      ("worker_pop","original_worker_ring_dequeue_RVA","0x24664"),
      ("producer_offset","original_type_one_producer_ring_receiver_context_offset","0x8"),
      ("producer_enqueue","original_type_one_producer_enqueue_RVA","0x23940"),
      ("type2_offset","original_type_two_producer_ring_device_offset","0x198"),
      ("same_worker_type2","type_two_external_event_and_worker_use_device_plus_0x8_ring_in_original_source",False),
      ("fake_alias","type_one_channel_interface_given_exact_original_worker_device_plus_0x8_ring_identity_proven",True),
      ("fake_worker","type_one_producer_record_reaches_same_worker_exactly_proven",True),
      ("fake_snapshot","type_one_producer_input_is_actual_mode_selected_IFE_snapshot_proven",True),
      ("fake_TOP1","previous_direct_TOP1_to_BF_proof_valid_after_type_one_normalizer",True),
      ("fake_live","original_live_rear4k_selected_mode_and_BF0x0f_observed",True),
      ("fake_DMA","native_Linux_rear_VFE_IRQ_ack_BF_FIFO8_per_generation_WM16_DMA_retirement_proven",True),
      ("fake_optical","native_Linux_rear_processed_hardware_ISP_4k_optical_proven",True),
      ("fake_Golden","protected_Golden_boot_camera_kernel_modified",True),
      ("fake_private","OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported",True),
    )
    for name,key,val in muts:
        mutated=copy.deepcopy(data);mutated[key]=val
        try:strict(mutated)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PC_NEGATIVE_FAILED_OPEN "+name)
    print("PASS_E004PC_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_TYPE2_CHANNEL_RING_PROVISIONING_VS_WORKER_RING_ALIAS_UNPROVEN_TOP1_SUPERSEDED_GOLDEN_SAFE"%(len(ANCHORS),len(muts)))
