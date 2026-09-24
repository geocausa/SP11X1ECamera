#!/usr/bin/env python3
"""E004oy: original-SP11 OEM type2 software event producer→ring→worker→handler.

Static 1:1 software record routing only, not BF type1 IRQ source or DMA ACK.
Original driver and original instructions examined only on SP11; commit scalars.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
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
24ba8|add|x0, sp, #0x28
24bb0|ldr|x8, [x19]
24bc0|bl|0x14002c5b0 <.text+0x2b5b0>
24c0c|ldr|x19, [sp, #0x28]
24c10|cbnz|x19, 0x140024c24 <.text+0x23c24>
24c24|ldr|w8, [x20, #0x4]
24c2c|str|w8, [x19, #0x4]
24c30|ldr|w4, [x20, #0x8]
24c34|str|w4, [x19, #0x8]
24c38|ldur|x8, [x20, #0xc]
24c3c|stur|x8, [x19, #0xc]
24d08|ldr|x20, [x21, #0x8]
24d0c|cbz|x20, 0x140024de0 <.text+0x23de0>
24d34|ldr|w11, [x20, #0x30]
24d38|add|x2, sp, #0x20
24d3c|ldr|w10, [x20, #0x14]
24d40|ldr|x8, [x20]
24d48|madd|x0, x10, x11, x8
24d4c|sxtw|x1, w10
24d50|bl|0x14002c5b0 <.text+0x2b5b0>
24d54|ldr|w8, [x20, #0x18]
24d58|add|w8, w8, #0x1
24d5c|str|w8, [x20, #0x18]
24da8|cbnz|w23, 0x140024de0 <.text+0x23de0>
24dac|ldaxr|w8, [x19]
24db0|add|w8, w8, #0x1
24db4|stlxr|w17, w8, [x19]
24db8|cbnz|w17, 0x140024dac <.text+0x23dac>
24dbc|dmb|ish
24dc4|adrp|x8, 0x14003f000
24dc8|ldr|x8, [x8, #0x2e8]
24dd4|add|x0, x21, #0x20
24dd8|blr|x8
238fc|movi|v16.16b, #0x0
23900|ldr|x19, [x20, #0x8]
23904|str|q16, [sp, #0x20]
23908|cbz|x19, 0x140023864 <.text+0x22864>
23924|ldr|w11, [x19, #0x2c]
23928|add|x0, sp, #0x20
2392c|ldr|w10, [x19, #0x14]
23930|ldr|x8, [x19]
23938|madd|x2, x10, x11, x8
2393c|sxtw|x1, w10
23940|bl|0x14002c5b0 <.text+0x2b5b0>
23944|ldr|w8, [x19, #0x18]
23948|sub|w8, w8, #0x1
2394c|str|w8, [x19, #0x18]
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
1fecc|cmp|w8, #0x2
1fed0|b.ne|0x14001ff70 <.text+0x1ef70>
1fed4|ldr|x21, [x20, #0x8]
1fed8|ldr|w8, [x21, #0xc]
1fef4|ldr|w3, [x8, #0x64]
1fefc|ldr|w4, [x8, #0x70]
1ff10|mov|w8, #-0x1
1ff14|ldaxr|w9, [x21]
1ff18|add|w9, w9, w8
1ff1c|stlxr|w17, w9, [x21]
1ff28|cbnz|w9, 0x14001ff70 <.text+0x1ef70>
1ff40|ldr|x0, [x19, #0x33c8]
1ff44|bl|0x14002bef8 <.text+0x2aef8>
"""
ANCHORS={int(a,16):(op,ops) for a,op,ops in (row.split("|",2) for row in SOURCE.strip().splitlines())}
def require(ok,why):
    if not ok:raise AssertionError("E004OY_FAIL_CLOSED "+why)
def facts():
    return {
     "schema":"sp11-e004oy-original-IFE-type2-external-callback-device-event-ring-worker-handler-static-v1",
     "parent_git_revision":"a7474380b68fa31c5c1c37031cb70bed2311382e",
     "same_SP11_original_OEM_ISP_sha256":SHA,
     "original_exact_ARM64_instruction_anchors":len(ANCHORS),
     "original_external_callback_producer_RVA":"0x24a70",
     "original_external_callback_source_input_processing_slot":"0x6b6b8",
     "original_external_callback_event_type_two_stamp_RVA":"0x24b80",
     "original_external_callback_event_type_two_value":2,
     "original_type_two_record_object_ring_offset":"0x33c8",
     "original_type_two_record_object_source_copy_RVAs":["0x24c2c","0x24c34","0x24c3c"],
     "original_event_notification_ring_device_offset":"0x8",
     "original_type_two_enqueued_event_copy_RVA":"0x24d50",
     "original_ring_worker_event_pop_RVA":"0x23940",
     "original_ring_worker_dispatch_RVA":"0x239bc",
     "original_mode_zero_type_two_handler_RVA":"0x1fecc",
     "original_type_two_record_software_counter_decrement_RVA":"0x1ff14",
     "original_type_two_record_software_ring_recycle_RVA":"0x1ff44",
     "original_type_two_event_may_be_produced_without_type_one_BF_event":True,
     "original_type_two_source_proves_BF_type_one_snapshot_pointer_or_live_BF0x0f":False,
     "original_event_ring_software_count_zero_proves_physical_WM16_IRQ_DMA_completion":False,
     "original_rear4k_live_mode_and_BF0x0f_observed":False,
     "native_Linux_rear_per_generation_BF_FIFO8_WM16_DMA_retirement_proven":False,
     "native_Linux_rear_processed_hardware_ISP_4k_optical_proven":False,
     "Golden_camera_kernel_boot_modified":False,
     "private_OEM_bulk_disassembly_driver_physical_DMA_KD_optical_exported":False,
    }
def strict(x):require(x==facts(),"claim modified or false DMA proof")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original same-SP11 OEM ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for addr,want in ANCHORS.items():require(ins.get(addr)==want,"original exact ARM64 RVA %x"%addr)
    old=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ox-original-ife-bf-top-status1-register-provenance-static/RESULT.json").read_text())
    require(old["snapshot_producer_to_exact_live_rear4k_BF_status_record_proven"] is False and
            old["TOP_status1_bit7_alone_proves_fifo8_queued_entry_or_WM16_DMA_retirement"] is False,
            "prior TOP1 mode-zero status candidate is conditional")
    data=facts();path=HERE/"RESULT.json"
    if path.exists():require(json.loads(path.read_text())==data,"saved derived scalar record mismatch")
    else:path.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    mutants=(
     ("SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
     ("external","original_external_callback_producer_RVA","0x24a30"),
     ("type2","original_external_callback_event_type_two_value",1),
     ("source","original_type_two_record_object_ring_offset","0x8"),
     ("notification","original_event_notification_ring_device_offset","0x33c8"),
     ("push","original_type_two_enqueued_event_copy_RVA","0x23940"),
     ("pop","original_ring_worker_event_pop_RVA","0x24d50"),
     ("dispatcher","original_ring_worker_dispatch_RVA","0x23940"),
     ("handler","original_mode_zero_type_two_handler_RVA","0x1f048"),
     ("counter","original_type_two_record_software_counter_decrement_RVA","0x1f048"),
     ("recycle","original_type_two_record_software_ring_recycle_RVA","0x26460"),
     ("not_other","original_type_two_event_may_be_produced_without_type_one_BF_event",False),
     ("BF","original_type_two_source_proves_BF_type_one_snapshot_pointer_or_live_BF0x0f",True),
     ("DMA","original_event_ring_software_count_zero_proves_physical_WM16_IRQ_DMA_completion",True),
     ("LIVE","original_rear4k_live_mode_and_BF0x0f_observed",True),
     ("NATIVE","native_Linux_rear_per_generation_BF_FIFO8_WM16_DMA_retirement_proven",True),
     ("OPTICAL","native_Linux_rear_processed_hardware_ISP_4k_optical_proven",True),
     ("GOLDEN","Golden_camera_kernel_boot_modified",True),
     ("PRIVATE","private_OEM_bulk_disassembly_driver_physical_DMA_KD_optical_exported",True),
    )
    for name,key,val in mutants:
        bad=copy.deepcopy(data);bad[key]=val
        try:strict(bad)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OY_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OY_%d_EXACT_ORIGINAL_ARM64_ANCHORS_19_NEGATIVES_TYPE2_DEVICE_EVENT_RING_WORKER_NOT_BF_TYPE1_OR_DMA_ACK_GOLDEN_SAFE"%len(ANCHORS))
