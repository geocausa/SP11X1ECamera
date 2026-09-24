#!/usr/bin/env python3
"""E004oz: source-verify registered snapshot vs external-event callback boundary.

Original same-SP11 OEM driver is SHA-locked and read only. No live camera,
OEM binary/disassembly/DMA addresses, or blocked KD material exported.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
2262c|adrp|x10, 0x14004b000
22630|ldrb|w8, [x10, #0x63]
22634|cbnz|w8, 0x140022660 <.text+0x21660>
22660|ldp|w8, w9, [x27]
22664|add|w8, w9, w8
22668|cmp|w2, w8
2266c|b.ge|0x140022608 <.text+0x21608>
22670|adrp|x8, 0x140024000 <.text+0x23000>
22674|add|x8, x8, #0xa30
22678|adrp|x9, 0x140067000
2267c|str|x8, [x9, #0x140]
22680|str|x12, [x11, w2, sxtw #3]
22684|adrp|x8, 0x140024000 <.text+0x23000>
22688|add|x8, x8, #0xa70
2268c|adrp|x9, 0x140067000
22690|str|x8, [x9, #0x150]
22694|mov|w8, #0x0
24a30|pacibsp|
24a34|stp|x29, x30, [sp, #-0x10]!
24a38|mov|x29, sp
24a3c|add|x8, x0, #0x6b, lsl #12
24a40|ldr|x8, [x8, #0x6b0]
24a44|mov|x15, x8
24a48|adrp|x17, 0x14003f000
24a4c|ldr|x17, [x17, #0x348]
24a50|blr|x17
24a54|blr|x15
24a58|ldp|x29, x30, [sp], #0x10
24a5c|autibsp|
24a60|ret|
19fa8|add|x8, x19, #0x6b, lsl #12
19fac|ldr|w8, [x8, #0x678]
19fb0|cmp|w8, #0x0
1a05c|adrp|x8, 0x14001c000 <.text+0x1b000>
1a060|add|x9, x8, #0x2b0
1a064|adrp|x8, 0x14001d000 <.text+0x1c000>
1a068|add|x8, x8, #0xc20
1a06c|csel|x9, x9, x8, ne
1a070|add|x8, x19, #0x6b, lsl #12
1a074|str|x9, [x8, #0x6b0]
1dc20|pacibsp|
1dc38|ldr|x8, [x19, #0x140]
1dc40|ldr|w8, [x8, #0x44]
1dc44|str|w8, [x20, #0x4]
1dc48|ldr|x8, [x19, #0x140]
1dc4c|ldr|w8, [x8, #0x48]
1dc50|str|w8, [x20, #0x8]
24a70|pacibsp|
24a8c|mov|x21, x0
24a90|mov|x20, x1
24ab0|add|x9, x21, #0x6b, lsl #12
24abc|add|x1, sp, #0x10
24ac0|ldr|x8, [x9, #0x6b8]
24ac4|mov|x0, x20
24ad8|blr|x15
24b78|mov|w8, #0x2
24b7c|ldr|x19, [x21, #0x33c8]
24b80|str|w8, [sp, #0x20]
24c24|ldr|w8, [x20, #0x4]
24c2c|str|w8, [x19, #0x4]
24c30|ldr|w4, [x20, #0x8]
24c34|str|w4, [x19, #0x8]
24d08|ldr|x20, [x21, #0x8]
24d38|add|x2, sp, #0x20
24d50|bl|0x14002c5b0 <.text+0x2b5b0>
23900|ldr|x19, [x20, #0x8]
23928|add|x0, sp, #0x20
23940|bl|0x14002c5b0 <.text+0x2b5b0>
23998|ldr|q16, [sp, #0x20]
2399c|add|x1, sp, #0x30
239a0|ldr|x8, [x24, #0x6d8]
239a4|mov|x0, x20
239a8|str|q16, [sp, #0x30]
239bc|blr|x15
1a0e8|adrp|x8, 0x14001c000 <.text+0x1b000>
1a0ec|add|x9, x8, #0x9d0
1a0f0|adrp|x8, 0x14001e000 <.text+0x1d000>
1a0f4|add|x8, x8, #0xf90
1a0f8|csel|x9, x9, x8, ne
1a100|str|x9, [x8, #0x6d8]
1efcc|ldr|w8, [x20]
1efd8|cmp|w8, #0x1
1efe4|b.ne|0x14001fecc <.text+0x1eecc>
1efe8|ldr|x23, [x20, #0x8]
1eff0|ldp|w8, w2, [x23, #0x4]
1f048|ubfx|w15, w2, #7, #1
1f188|cbz|w15, 0x14001f19c <.text+0x1e19c>
1f190|mov|w15, #0xf
1f194|str|w15, [x7, w1, uxtw #2]
1fecc|cmp|w8, #0x2
1fed4|ldr|x21, [x20, #0x8]
1ff14|ldaxr|w9, [x21]
"""
ANCHORS={int(r,16):(m,operand) for r,m,operand in (s.split("|",2) for s in SOURCE.strip().splitlines())}
def require(cond,why):
    if not cond:raise AssertionError("E004OZ_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004oz-original-IFE-snapshot-external-event-dual-callback-registration-static-v1",
      "parent_git_revision":"6a6c6830d942b77254436735539f53c48ff31f67",
      "original_same_SP11_OEM_ISP_sha256":SHA,
      "original_exact_ARM64_instruction_anchors":len(ANCHORS),
      "original_initializer_callback_register_gate_RVA":"0x2266c",
      "original_status_snapshot_wrapper_callback_RVA":"0x24a30",
      "original_status_snapshot_wrapper_global_slot_RVA":"0x67140",
      "original_status_snapshot_wrapper_per_device_slot_offset":"0x6b6b0",
      "original_mode_zero_status_snapshot_RVA":"0x1dc20",
      "original_mode_zero_TOP1_status_register_offset":"0x48",
      "original_mode_zero_TOP1_snapshot_record_offset":"0x8",
      "original_external_event_callback_RVA":"0x24a70",
      "original_external_event_callback_global_slot_RVA":"0x67150",
      "original_external_event_callback_per_device_slot_offset":"0x6b6b8",
      "original_external_event_callback_emitted_event_type":2,
      "original_external_type_two_event_enqueue_RVA":"0x24d50",
      "original_original_device_event_worker_ring_dequeue_RVA":"0x23940",
      "original_worker_mode_selected_handler_slot_offset":"0x6b6d8",
      "original_mode_zero_type_one_handler_RVA":"0x1ef90",
      "original_type_one_BF_status_bit":7,
      "original_type_one_BF_event_id":"0x0f",
      "original_type_one_BF_FIFO_group":8,
      "original_snapshot_wrapper_invoker_and_type_one_event_record_producer_proven":False,
      "original_snapshot_TO_type_one_buffer_pointer_identity_proven":False,
      "original_live_rear4k_IFE_mode_and_BF_event_proven":False,
      "original_BUS_IRQ_clear_offset_conflict_resolved":False,
      "native_Linux_rear_IRQ_ack_and_per_generation_BF_WM16_DMA_retirement_proven":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_proven":False,
      "Golden_camera_kernel_boot_modified":False,
      "OEM_private_binary_bulk_ISA_DMA_physical_KD_optical_exported":False,
    }
def strict(x):require(x==facts(),"saved scalar facts mismatch or false hardware promotion")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original OEM ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-0x140000000:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for r,w in ANCHORS.items():require(ins.get(r)==w,"original exact ISA RVA %x"%r)
    old=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004oy-ife-type2-event-record-ring-producer-static/RESULT.json").read_text())
    require(old["original_type_two_source_proves_BF_type_one_snapshot_pointer_or_live_BF0x0f"] is False,
            "type-two external event not type-one BF producer")
    candidate=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ox-original-ife-bf-top-status1-register-provenance-static/RESULT.json").read_text())
    require(candidate["snapshot_producer_to_exact_live_rear4k_BF_status_record_proven"] is False and
            candidate["original_BUS_side_snapshot_write_offsets_match_accepted_Linux_BUS_CLEAR0_1"] is False,
            "original conditional candidate and BUS clear mismatch remain open")
    f=facts();path=HERE/"RESULT.json"
    if path.exists():require(json.loads(path.read_text())==f,"saved scalar result altered")
    else:path.write_text(json.dumps(f,sort_keys=True,indent=2)+"\n")
    muts=(
      ("sha","original_same_SP11_OEM_ISP_sha256","0"*64),
      ("wrapper","original_status_snapshot_wrapper_callback_RVA","0x24a70"),
      ("external","original_external_event_callback_RVA","0x24a30"),
      ("slot_snapshot","original_status_snapshot_wrapper_global_slot_RVA","0x67150"),
      ("slot_external","original_external_event_callback_global_slot_RVA","0x67140"),
      ("per_device","original_status_snapshot_wrapper_per_device_slot_offset","0x6b6b8"),
      ("mode0","original_mode_zero_status_snapshot_RVA","0x1c2b0"),
      ("top1","original_mode_zero_TOP1_status_register_offset","0xc2c"),
      ("event_type","original_external_event_callback_emitted_event_type",1),
      ("enqueue","original_external_type_two_event_enqueue_RVA","0x23940"),
      ("dequeue","original_original_device_event_worker_ring_dequeue_RVA","0x24d50"),
      ("handler","original_worker_mode_selected_handler_slot_offset","0x6b6b0"),
      ("bf_bit","original_type_one_BF_status_bit",21),
      ("bf_fifo","original_type_one_BF_FIFO_group",0),
      ("fake_producer","original_snapshot_wrapper_invoker_and_type_one_event_record_producer_proven",True),
      ("fake_identity","original_snapshot_TO_type_one_buffer_pointer_identity_proven",True),
      ("fake_live","original_live_rear4k_IFE_mode_and_BF_event_proven",True),
      ("fake_clear","original_BUS_IRQ_clear_offset_conflict_resolved",True),
      ("fake_dma","native_Linux_rear_IRQ_ack_and_per_generation_BF_WM16_DMA_retirement_proven",True),
      ("fake_optical","native_Linux_rear_processed_hardware_ISP_4k_optical_proven",True),
      ("fake_golden","Golden_camera_kernel_boot_modified",True),
      ("fake_private","OEM_private_binary_bulk_ISA_DMA_physical_KD_optical_exported",True),
    )
    for name,key,val in muts:
        bad=copy.deepcopy(f);bad[key]=val
        try:strict(bad)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OZ_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OZ_%d_ORIGINAL_EXACT_ISA_ANCHORS_22_NEGATIVES_DUAL_CALLBACKS_TYPE_ONE_UPSTREAM_HW_ACK_DMA_UNPROVEN_GOLDEN_SAFE"%len(ANCHORS))
