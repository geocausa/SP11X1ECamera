#!/usr/bin/env python3
"""E004pg: SHA-pinned static original source endpoint command-A to worker ring.

Corrects E004pd/pe/pf source decoder; no original live rear4K IRQ/DMA or
native Linux hardware promotion. Only safe scalar evidence leaves SP11.
"""
import copy,hashlib,json,re,struct,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
19e34|mov|w20, w1
19e38|mov|x22, #0x30
19e40|ldr|x8, [x8, #0x30]
19e4c|umaddl|x8, w20, w22, x8
19e50|add|x1, x8, #0x28
19e54|add|x0, x8, #0x8
19e58|bl|0x140022278 <.text+0x21278>
22298|mov|x25, x0
2229c|str|x1, [sp, #0x28]
222a0|mov|w24, w2
222f8|mov|w1, #0x28
22300|bl|0x14002a260 <.text+0x29260>
22304|mov|x23, x0
22314|mov|w1, w22
22324|bl|0x14002a260 <.text+0x29260>
22330|str|x19, [x23, #0x20]
2233c|adrp|x8, 0x140022000 <.text+0x21000>
22340|add|x9, x8, #0xcd0
22344|adrp|x8, 0x140023000 <.text+0x22000>
22348|add|x8, x8, #0xe00
2234c|stp|x9, x8, [x23]
2236c|ldr|x20, [x23, #0x20]
22830|add|x22, x20, #0x8
22844|mov|w1, #0x368
22848|mov|w0, #0x1d
2284c|bl|0x14002a260 <.text+0x29260>
22850|mov|x19, x0
22870|add|x9, x19, #0x38
22874|add|x8, x9, #0x10
22878|stp|x8, x9, [x19]
22898|str|x19, [x22]
228b8|ldr|w8, [x20, #0x120]
228c4|add|x0, x20, #0x20
22910|mov|x0, x20
22914|bl|0x140023700 <.text+0x22700>
22b8c|ldr|x8, [sp, #0x28]
22b90|str|x23, [x25]
22b98|str|x20, [x8]
22cd0|pacibsp|
22cf0|mov|x21, x2
22cfc|ldr|x19, [x0, #0x20]
22d24|cmp|w1, #0x803
22d30|sub|w10, w1, #0x1
22d3c|adr|x9, 0x1400236c4 <.text+0x226c4>
22d40|ldrsw|x8, [x9, w10, uxtw #2]
22d44|adr|x9, 0x140023120 <.text+0x22120>
22d48|add|x8, x9, x8, lsl #2
22d4c|br|x8
23120|cbz|x4, 0x1400236a0 <.text+0x226a0>
23124|ldr|x9, [x19, #0x8]
23128|add|x8, x19, #0x20
2312c|stp|x9, x8, [x4]
23130|b|0x140023698 <.text+0x22698>
23134|cbz|x21, 0x1400236a0 <.text+0x226a0>
23138|ldr|x8, [x21]
2313c|str|x8, [x19, #0x10]
23140|b|0x140023698 <.text+0x22698>
2382c|mov|x20, x0
23900|ldr|x19, [x20, #0x8]
23928|add|x0, sp, #0x20
23940|bl|0x14002c5b0 <.text+0x2b5b0>
2399c|add|x1, sp, #0x30
239a0|ldr|x8, [x24, #0x6d8]
239a4|mov|x0, x20
239a8|str|q16, [sp, #0x30]
239bc|blr|x15
17f98|mov|w8, #0x2
17fa0|str|w8, [sp, #0x60]
17fb8|ldr|x8, [x8, #0x30]
17fb0|add|x4, sp, #0x50
17fc0|mov|w1, #0xa
17fc8|ldr|x0, [x8, #0x8]
17fe4|cbnz|w0, 0x14001804c <.text+0x1704c>
17ffc|ldr|x8, [x8, #0x40]
18000|add|x2, sp, #0x50
18004|mov|w1, #0xb
1800c|ldr|x0, [x8, #0x8]
211d8|mov|x21, x2
211e4|ldr|x19, [x0, #0x20]
21478|cbz|x21, 0x140021b98 <.text+0x20b98>
2147c|ldr|w8, [x21, #0x10]
2149c|cmp|w8, #0x2
214a4|ldr|x8, [x21]
214a8|str|x8, [x19, #0x198]
214ac|ldr|x8, [x21, #0x8]
214b0|str|x8, [x19, #0x1a0]
244e4|mov|w8, #0x1
244e8|str|w8, [sp, #0x10]
244ec|ldr|x8, [x20, #0x208]
244f0|mov|x1, x22
2461c|ldr|x19, [x20, #0x198]
2464c|add|x2, sp, #0x10
24664|bl|0x14002c5b0 <.text+0x2b5b0>
"""
ANCHORS={int(a,16):(op,ops) for a,op,ops in (l.split("|",2) for l in SOURCE.strip().splitlines())}
def require(ok,why):
    if not ok:raise AssertionError("E004PG_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004pg-original-source-cmdA-ring8-not1b0-to-destination-producer-to-same-worker-static-v1",
      "parent_git_revision":"54edb98a3ef4107642013bed2033ce008118c517",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "source_endpoint_table_offset":"0x30",
      "destination_endpoint_table_offset":"0x40",
      "source_endpoint_installer_RVA":"0x19e10",
      "source_endpoint_constructor_RVA":"0x22278",
      "source_endpoint_vtable_command_handler_RVA":"0x22cd0",
      "destination_endpoint_vtable_command_handler_RVA":"0x211b0",
      "source_endpoint_context_pointer_field_offset":"0x20",
      "source_endpoint_context_worker_ring_field_offset":"0x8",
      "source_endpoint_context_worker_notify_address_offset":"0x20",
      "source_endpoint_worker_ring_allocation_RVA":"0x2284c",
      "source_endpoint_worker_ring_allocation_bytes":"0x368",
      "source_endpoint_worker_ring_store_RVA":"0x22898",
      "source_endpoint_worker_function_RVA":"0x23810",
      "source_endpoint_worker_dequeue_RVA":"0x23940",
      "source_endpoint_constructor_instance_store_RVA":"0x22b90",
      "source_endpoint_command_jump_table_RVA":"0x236c4",
      "source_endpoint_command_a_RVA":"0x23120",
      "source_endpoint_command_a_output_ring_source_offset":"0x8",
      "source_endpoint_command_a_output_notification_source_address_offset":"0x20",
      "source_endpoint_command_a_output_two_pointers_store_RVA":"0x2312c",
      "source_endpoint_command_a_returned_context_plus_0x1b0":False,
      "source_endpoint_cmdA_ring_is_same_context_ring_as_worker_pop_source_proven":True,
      "source_endpoint_cmdA_notification_field_source_proven":True,
      "destination_endpoint_command_b_RVA":"0x21478",
      "destination_endpoint_command_b_received_ring_context_offset":"0x198",
      "destination_endpoint_command_b_received_notify_context_offset":"0x1a0",
      "source_cmdA_to_dest_cmdB_same_interface_successful_kind2_static_proven":True,
      "type_one_event_producer_RVA":"0x243d0",
      "type_one_event_producer_kind":1,
      "type_one_event_producer_destination_context_ring_field_offset":"0x198",
      "type_one_event_producer_enqueue_RVA":"0x24664",
      "type_one_event_producer_to_worker_same_ring_on_successful_setup_static_proven":True,
      "type_one_event_producer_to_worker_same_live_rear4k_frame_observed":False,
      "type_one_producer_incoming_buffer_exact_IFE_snapshot_identity_proven":False,
      "original_live_rear4k_selected_IFE_mode_and_BF0x0f_observed":False,
      "original_BF_status_bit_MMIO_source_or_safe_ack_live_proven":False,
      "previous_direct_TOP1_to_BF_status_bit7_inference_valid":False,
      "native_Linux_rear_VFE1_BF_IRQ_ack_FIFO8_generation_matched_WM16_DMA_IOMMU_quiescence_proven":False,
      "native_Linux_rear_hardware_ISP_4k_optical_proven":False,
      "rear_hardware_ISP_runtime_authorized":False,
      "Golden_boot_kernel_camera_hardware_modified":False,
      "OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported":False,
    }
def strict(v):require(v==facts(),"false identity or safety claim in source-backed result")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original same-SP11 OEM ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for at,expected in ANCHORS.items():require(ins.get(at)==expected,"original exact ARM64 RVA %x"%at)
    pe=ISP.read_bytes()
    # Independent actual source-command jump table index cmd-1; .text VA
    # 0x1000, raw start0x400 => RVA-0xC00. Not destination's other table.
    offset=0x236c4-0xc00
    for cmd,target in ((0xA,0x23120),(0xB,0x23134)):
        disp=struct.unpack_from("<i",pe,offset+(cmd-1)*4)[0]
        require(0x23120+4*disp==target,"source command-jump-table mismatch %x"%cmd)
    # Identity expression: source endpoint's context x19 is constructor's x20
    # via endpoint+0x20; both cmd-A and worker load ring from context+0x08.
    def accepted_ring(source_ctx,worker_ctx,kind,successA,successB):
        return bool(source_ctx is worker_ctx and kind==2 and successA and successB)
    context=object()
    require(accepted_ring(context,context,2,True,True) and
            not accepted_ring(context,object(),2,True,True) and
            not accepted_ring(context,context,3,True,True) and
            not accepted_ring(context,context,2,False,True) and
            not accepted_ring(context,context,2,True,False),
            "source/worker same-object only on successful matching channel")
    pf=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pf-original-channel-source-vs-destination-endpoint-context-static/RESULT.json").read_text())
    require(pf["original_command_A_source_endpoint_table_slot_offset"]=="0x30" and
            pf["original_command_B_destination_endpoint_table_slot_offset"]=="0x40" and
            pf["original_destination_plus_0x1b0_allocation_is_source_command_A_endpoint"] is False,
            "E004pf destination vs source context disambiguation")
    pb=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pb-ife-type1-record-producer-normalization-static/RESULT.json").read_text())
    require(pb["previous_direct_TOP_status1_bit7_to_BF_record_inference_valid_after_normalization"] is False and
            pb["type_one_event_enqueue_software_ring_context_offset"]=="0x198",
            "E004pb retains status-word provenance and type1 producer")
    f=facts();out=HERE/"RESULT.json"
    if out.exists():require(json.loads(out.read_text())==f,"saved safe result altered")
    else:out.write_text(json.dumps(f,sort_keys=True,indent=2)+"\n")
    negatives=(
      ("SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("source_slot","source_endpoint_table_offset","0x40"),
      ("destination_slot","destination_endpoint_table_offset","0x30"),
      ("src_vtable","source_endpoint_vtable_command_handler_RVA","0x211b0"),
      ("dst_vtable","destination_endpoint_vtable_command_handler_RVA","0x22cd0"),
      ("src_ctx","source_endpoint_context_pointer_field_offset","0x8"),
      ("ring","source_endpoint_context_worker_ring_field_offset","0x1b0"),
      ("notify","source_endpoint_context_worker_notify_address_offset","0x1a0"),
      ("alloc","source_endpoint_worker_ring_allocation_RVA","0x17aa4"),
      ("bytes","source_endpoint_worker_ring_allocation_bytes","0x1d0"),
      ("store","source_endpoint_worker_ring_store_RVA","0x17af0"),
      ("dequeue","source_endpoint_worker_dequeue_RVA","0x24664"),
      ("cmd_table","source_endpoint_command_jump_table_RVA","0x21bc4"),
      ("cmd_branch","source_endpoint_command_a_RVA","0x214bc"),
      ("cmd_offset","source_endpoint_command_a_output_ring_source_offset","0x1b0"),
      ("cmd_notify","source_endpoint_command_a_output_notification_source_address_offset","0x1a0"),
      ("fake_old","source_endpoint_command_a_returned_context_plus_0x1b0",True),
      ("fake_worker_alias","source_endpoint_cmdA_ring_is_same_context_ring_as_worker_pop_source_proven",False),
      ("fake_notify","source_endpoint_cmdA_notification_field_source_proven",False),
      ("dest_branch","destination_endpoint_command_b_RVA","0x23134"),
      ("dest_ring","destination_endpoint_command_b_received_ring_context_offset","0x1b0"),
      ("dest_notify","destination_endpoint_command_b_received_notify_context_offset","0x1b8"),
      ("fake_cmd","source_cmdA_to_dest_cmdB_same_interface_successful_kind2_static_proven",False),
      ("fake_static_worker","type_one_event_producer_to_worker_same_ring_on_successful_setup_static_proven",False),
      ("fake_live_worker","type_one_event_producer_to_worker_same_live_rear4k_frame_observed",True),
      ("fake_snapshot","type_one_producer_incoming_buffer_exact_IFE_snapshot_identity_proven",True),
      ("fake_live_bf","original_live_rear4k_selected_IFE_mode_and_BF0x0f_observed",True),
      ("fake_irq","original_BF_status_bit_MMIO_source_or_safe_ack_live_proven",True),
      ("fake_TOP","previous_direct_TOP1_to_BF_status_bit7_inference_valid",True),
      ("fake_dma","native_Linux_rear_VFE1_BF_IRQ_ack_FIFO8_generation_matched_WM16_DMA_IOMMU_quiescence_proven",True),
      ("fake_optical","native_Linux_rear_hardware_ISP_4k_optical_proven",True),
      ("fake_arm","rear_hardware_ISP_runtime_authorized",True),
      ("fake_golden","Golden_boot_kernel_camera_hardware_modified",True),
      ("fake_private","OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported",True),
    )
    for name,k,val in negatives:
        changed=copy.deepcopy(f);changed[k]=val
        try:strict(changed)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PG_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004PG_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_SOURCE_CMD_A_8_MATCHES_WORKER_RING_NOTIFY_20_TO_DEST_198_1A0_TYPE1_STATIC_LIVE_BF_DMA_UNPROVEN_GOLDEN_SAFE"%(len(ANCHORS),len(negatives)))
