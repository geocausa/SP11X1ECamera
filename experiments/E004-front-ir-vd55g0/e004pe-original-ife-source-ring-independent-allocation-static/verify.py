#!/usr/bin/env python3
"""E004pe original two ring allocation sites and fail-closed pointer identity.

2026-09-24 ERRATUM: the context+0x1b0 allocation belongs to the command-B
DESTINATION endpoint, not the separate command-A source endpoint.
Static source only; destination/worker allocations cannot prove any live
source-to-worker alias, IRQ completion or DMA ACK.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
175f8|ldr|x8, [x27]
17600|ldr|x8, [x8, #0x40]
17604|umaddl|x8, w20, w24, x8
17608|str|x8, [sp, #0x40]
1760c|add|x8, x8, #0x8
17610|stp|xzr, x8, [sp, #0x30]
17688|bl|0x14002a260 <.text+0x29260>
1768c|str|x0, [x21, #0x20]
176bc|bl|0x14002df80 <.text+0x2cf80>
176c0|ldr|x19, [x21, #0x20]
17a90|add|x20, x19, #0x1b0
17a9c|mov|w1, #0x1d0
17aa0|mov|w0, #0x1d
17aa4|bl|0x14002a260 <.text+0x29260>
17aa8|mov|x22, x0
17aac|cbnz|x22, 0x140017ab8 <.text+0x16ab8>
17ab8|mov|x2, #0x1b8
17ac0|add|x0, x22, #0x18
17ac4|bl|0x14002df80 <.text+0x2cf80>
17ac8|add|x9, x22, #0x38
17acc|add|x8, x9, #0x8
17ad0|stp|x8, x9, [x22]
17ad4|add|x0, x22, #0x20
17ad8|str|x23, [x22, #0x10]
17adc|str|wzr, [x22, #0x18]
17ae0|stp|wzr, wzr, [x22, #0x2c]
17af0|str|x22, [x20]
17b34|ldr|x24, [x19, #0x1b0]
17bec|ldr|x8, [sp, #0x38]
17bf4|str|x21, [x8]
17b48|strb|w0, [x24, #0x28]
17b4c|ldr|w9, [x24, #0x18]
17b50|ldr|w8, [x24, #0x10]
17b5c|ldr|w11, [x24, #0x30]
17b60|add|x2, sp, #0x48
17b78|bl|0x14002c5b0 <.text+0x2b5b0>
17b80|add|w8, w8, #0x1
17bc4|cmp|w20, #0x32
211e4|ldr|x19, [x0, #0x20]
214bc|cbz|x4, 0x140021b98 <.text+0x20b98>
214c0|ldr|x8, [x19, #0x1b0]
214c4|str|x8, [x4]
214a4|ldr|x8, [x21]
214a8|str|x8, [x19, #0x198]
17fb8|ldr|x8, [x8, #0x30]
17fb0|add|x4, sp, #0x50
17fc0|mov|w1, #0xa
17ff8|mov|w3, #0x18
18000|add|x2, sp, #0x50
18004|mov|w1, #0xb
21f28|ldr|x8, [x20, #0x1b0]
21f30|ldr|w22, [x8, #0x18]
21f44|ldr|x21, [x20, #0x1b0]
21f4c|ldr|x8, [x24, #0x270]
21f54|blr|x8
22830|add|x22, x20, #0x8
22844|mov|w1, #0x368
22848|mov|w0, #0x1d
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
23900|ldr|x19, [x20, #0x8]
23940|bl|0x14002c5b0 <.text+0x2b5b0>
2461c|ldr|x19, [x20, #0x198]
24664|bl|0x14002c5b0 <.text+0x2b5b0>
"""
ANCHORS={int(a,16):(op,ops) for a,op,ops in (l.split("|",2) for l in SOURCE.strip().splitlines())}
def require(cond,why):
    if not cond:raise AssertionError("E004PE_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004pe-ERRATUM-original-IFE-destination-plus1b0-and-worker-plus8-separate-ring-allocation-sites-static-v2",
      "parent_git_revision":"b68dc190ef2c53e3df57b6970c6e6679b1a8a44b",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "original_exact_ARM64_instruction_anchors":len(ANCHORS),
      "historical_original_E004pe_source_allocation_assignment_superseded":True,
      "destination_context_original_allocation_owner_init_RVA":"0x176c0",
      "destination_context_ring_field_offset":"0x1b0",
      "destination_context_ring_allocation_RVA":"0x17aa4",
      "destination_context_ring_allocation_structure_bytes":"0x1d0",
      "destination_context_ring_store_RVA":"0x17af0",
      "destination_context_ring_local_setup_use_RVA":"0x17b34",
      "destination_context_ring_local_setup_loop_bound":50,
      "destination_context_ring_local_cleanup_use_RVA":"0x21f28",
      "distinct_source_endpoint_command_a_export_RVA":"0x214c0",
      "distinct_source_endpoint_command_a_to_destination_import_RVA":"0x214a8",
      "worker_context_ring_field_offset":"0x8",
      "worker_context_ring_allocation_RVA":"0x2284c",
      "worker_context_ring_allocation_structure_bytes":"0x368",
      "worker_context_ring_store_RVA":"0x22898",
      "worker_context_ring_dequeue_RVA":"0x23940",
      "original_destination_and_worker_own_ring_allocations_are_separate_code_paths":True,
      "allocated_destination_ring_is_command_A_source_ring_proven":False,
      "allocated_destination_endpoint_table_offset":"0x40",
      "distinct_command_A_source_endpoint_table_offset":"0x30",
      "command_A_source_plus_0x1b0_allocation_site_proven":False,
      "original_destination_ring_allocation_structure_bytes_equal_worker":False,
      "original_destination_and_worker_ring_exact_same_session_pointer_alias_proven":False,
      "original_destination_and_worker_ring_never_alias_any_live_session_proven":False,
      "original_type_one_record_reaches_worker_same_queue_generation_proven":False,
      "original_snapshot_wrapper_output_is_exact_type_one_input_proven":False,
      "original_rear4k_live_selected_mode_BF_event0x0f_observed":False,
      "old_direct_TOP1_to_BF_source_inference_valid":False,
      "native_rear_VFE1_BF_FIFO8_WM16_irq_bus_dma_iommu_safe_retirement_proven":False,
      "native_rear_hardware_ISP_4k_optical_proven":False,
      "rear_hardware_ISP_runtime_authorized":False,
      "protected_Golden_boot_kernel_camera_modified":False,
      "OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported":False,
    }
def strict(data):require(data==facts(),"unsafe conclusion, false alias or scalar source altered")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original ISP SHA")
    dis=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(dis)}
    for addr,expected in ANCHORS.items():require(ins.get(addr)==expected,"exact original ARM64 RVA %x"%addr)
    previous=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pd-original-ife-channel-command-a-b-pointer-transfer-static/RESULT.json").read_text())
    require(previous["original_command_a_source_context_plus_0x1b0_is_passed_to_command_b_destination_plus_0x198_source_proven"] is True and
            previous["original_command_a_returned_ring_equals_worker_device_plus_0x8_same_device_generation_proven"] is False,
            "prior pointer transfer source true but worker identity open")
    # Distinct original allocation sites and sizes do not establish either
    # alias or impossibility of alias for an unobserved future live session.
    def can_claim_alias(src_id,worker_id,same_session_verified,source_chain_verified):
        return bool(src_id is not None and worker_id is not None and
                    same_session_verified is True and source_chain_verified is True and src_id==worker_id)
    require(can_claim_alias(0x11,0x11,True,True) and
            not can_claim_alias(0x11,0x11,False,True) and
            not can_claim_alias(0x11,0x11,True,False) and
            not can_claim_alias(0x11,0x12,True,True) and
            not can_claim_alias(None,0x11,True,True),
            "offline ring alias requires independently verified same-session identity")
    f=facts(); saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==f,"saved safe scalar result changed")
    else:saved.write_text(json.dumps(f,sort_keys=True,indent=2)+"\n")
    muts=(
       ("sha","same_SP11_original_OEM_ISP_sha256","0"*64),
       ("source_field","destination_context_ring_field_offset","0x8"),
       ("source_alloc","destination_context_ring_allocation_RVA","0x2284c"),
       ("source_size","destination_context_ring_allocation_structure_bytes","0x368"),
       ("source_store","destination_context_ring_store_RVA","0x22898"),
       ("source_setup","destination_context_ring_local_setup_use_RVA","0x23940"),
       ("source_cleanup","destination_context_ring_local_cleanup_use_RVA","0x23940"),
       ("source_export","distinct_source_endpoint_command_a_export_RVA","0x23900"),
       ("source_to_dst","distinct_source_endpoint_command_a_to_destination_import_RVA","0x23940"),
       ("worker_field","worker_context_ring_field_offset","0x198"),
       ("worker_alloc","worker_context_ring_allocation_RVA","0x17aa4"),
       ("worker_size","worker_context_ring_allocation_structure_bytes","0x1d0"),
       ("worker_store","worker_context_ring_store_RVA","0x17af0"),
       ("worker_dequeue","worker_context_ring_dequeue_RVA","0x17b34"),
       ("fake_samealloc","original_destination_and_worker_own_ring_allocations_are_separate_code_paths",False),
       ("fake_source_allocation","allocated_destination_ring_is_command_A_source_ring_proven",True),
       ("fake_source_site","command_A_source_plus_0x1b0_allocation_site_proven",True),
       ("fake_endpoint","allocated_destination_endpoint_table_offset","0x30"),
       ("fake_source_endpoint","distinct_command_A_source_endpoint_table_offset","0x40"),
       ("fake_erratum","historical_original_E004pe_source_allocation_assignment_superseded",False),
       ("fake_size","original_destination_ring_allocation_structure_bytes_equal_worker",True),
       ("fake_alias","original_destination_and_worker_ring_exact_same_session_pointer_alias_proven",True),
       ("fake_noalias","original_destination_and_worker_ring_never_alias_any_live_session_proven",True),
       ("fake_worker","original_type_one_record_reaches_worker_same_queue_generation_proven",True),
       ("fake_snapshot","original_snapshot_wrapper_output_is_exact_type_one_input_proven",True),
       ("fake_live","original_rear4k_live_selected_mode_BF_event0x0f_observed",True),
       ("fake_TOP","old_direct_TOP1_to_BF_source_inference_valid",True),
       ("fake_dma","native_rear_VFE1_BF_FIFO8_WM16_irq_bus_dma_iommu_safe_retirement_proven",True),
       ("fake_optical","native_rear_hardware_ISP_4k_optical_proven",True),
       ("fake_arm","rear_hardware_ISP_runtime_authorized",True),
       ("fake_golden","protected_Golden_boot_kernel_camera_modified",True),
       ("fake_private","OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported",True),
    )
    for name,key,value in muts:
        changed=copy.deepcopy(f);changed[key]=value
        try:strict(changed)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PE_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004PE_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_ERRATUM_DESTINATION_1B0_VS_WORKER_8_SEPARATE_ALLOCATIONS_SOURCE_COMMAND_A_ALLOCATION_UNKNOWN_BF_DMA_UNPROVEN_GOLDEN_SAFE"%(len(ANCHORS),len(muts)))
