#!/usr/bin/env python3
"""E004pf corrects E004pe context misattribution with independently locked ISA.

The +0x1b0 0x1d0-byte allocation is in command-B DESTINATION table+0x40.
Command-A SOURCE uses a different table+0x30 endpoint. Not live DMA evidence.
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
17660|mov|w1, #0x28
17668|bl|0x14002a260 <.text+0x29260>
1766c|mov|x21, x0
17678|mov|w1, #0x5f8
17688|bl|0x14002a260 <.text+0x29260>
1768c|str|x0, [x21, #0x20]
17694|adrp|x8, 0x140021000 <.text+0x20000>
17698|add|x9, x8, #0x1b0
1769c|adrp|x8, 0x140021000 <.text+0x20000>
176a0|add|x8, x8, #0xc00
176a4|stp|x9, x8, [x21]
176b8|mov|w1, #0x0
176bc|bl|0x14002df80 <.text+0x2cf80>
176c0|ldr|x19, [x21, #0x20]
17a90|add|x20, x19, #0x1b0
17a9c|mov|w1, #0x1d0
17aa0|mov|w0, #0x1d
17aa4|bl|0x14002a260 <.text+0x29260>
17aa8|mov|x22, x0
17ab8|mov|x2, #0x1b8
17ac0|add|x0, x22, #0x18
17ac4|bl|0x14002df80 <.text+0x2cf80>
17ac8|add|x9, x22, #0x38
17acc|add|x8, x9, #0x8
17ad0|stp|x8, x9, [x22]
17af0|str|x22, [x20]
17bec|ldr|x8, [sp, #0x38]
17bf4|str|x21, [x8]
17fb0|add|x4, sp, #0x50
17fb8|ldr|x8, [x8, #0x30]
17fc0|mov|w1, #0xa
17fc4|umaddl|x8, w19, w24, x8
17fc8|ldr|x0, [x8, #0x8]
17fe4|cbnz|w0, 0x14001804c <.text+0x1704c>
17ffc|ldr|x8, [x8, #0x40]
18000|add|x2, sp, #0x50
18004|mov|w1, #0xb
18008|umaddl|x8, w19, w24, x8
1800c|ldr|x0, [x8, #0x8]
214bc|cbz|x4, 0x140021b98 <.text+0x20b98>
214c0|ldr|x8, [x19, #0x1b0]
214c4|str|x8, [x4]
2147c|ldr|w8, [x21, #0x10]
2149c|cmp|w8, #0x2
214a4|ldr|x8, [x21]
214a8|str|x8, [x19, #0x198]
214ac|ldr|x8, [x21, #0x8]
214b0|str|x8, [x19, #0x1a0]
22830|add|x22, x20, #0x8
22844|mov|w1, #0x368
2284c|bl|0x14002a260 <.text+0x29260>
22898|str|x19, [x22]
23900|ldr|x19, [x20, #0x8]
23940|bl|0x14002c5b0 <.text+0x2b5b0>
"""
ANCHORS={int(a,16):(op,args) for a,op,args in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def require(ok,why):
    if not ok:raise AssertionError("E004PF_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004pf-corrected-source-vs-destination-context-original-IFE-interface-static-v1",
      "parent_git_revision":"1ba51d254d758f63e391ffb84b537cb1e885e6b3",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "original_command_A_source_endpoint_table_slot_offset":"0x30",
      "original_command_B_destination_endpoint_table_slot_offset":"0x40",
      "original_destination_endpoint_selected_slot_RVA":"0x17608",
      "original_destination_endpoint_object_store_RVA":"0x17bf4",
      "original_destination_endpoint_object_context_load_RVA":"0x176c0",
      "original_destination_endpoint_context_plus_0x1b0_ring_allocation_RVA":"0x17aa4",
      "original_destination_endpoint_context_plus_0x1b0_ring_object_bytes":"0x1d0",
      "original_destination_endpoint_context_plus_0x1b0_ring_store_RVA":"0x17af0",
      "original_command_A_source_context_plus_0x1b0_pointer_export_RVA":"0x214c0",
      "original_command_B_destination_context_plus_0x198_pointer_import_RVA":"0x214a8",
      "original_worker_device_plus_0x8_ring_allocation_RVA":"0x2284c",
      "original_worker_device_plus_0x8_ring_object_bytes":"0x368",
      "original_worker_device_plus_0x8_ring_store_RVA":"0x22898",
      "original_destination_plus_0x1b0_allocation_is_source_command_A_endpoint":False,
      "original_command_A_source_plus_0x1b0_allocation_site_source_proven":False,
      "original_source_endpoint_pointer_equals_destination_endpoint_same_session_proven":False,
      "original_source_plus_0x1b0_equals_worker_device_plus_0x8_ring_proven":False,
      "original_destination_plus_0x1b0_equals_worker_device_plus_0x8_ring_proven":False,
      "original_type_one_event_source_buffer_equals_IFE_snapshot_proven":False,
      "original_type_one_event_consumed_by_original_worker_same_generation_proven":False,
      "original_live_rear4k_IFE_mode_BF_event_0x0f_observed":False,
      "old_direct_TOP1_to_BF_bit7_status_inference_valid":False,
      "native_rear_VFE1_BF_FIFO8_per_generation_WM16_IRQ_bus_dma_iommu_retirement_proven":False,
      "native_rear_hardware_ISP_4k_optical_proven":False,
      "rear_hardware_ISP_runtime_authorized":False,
      "Golden_boot_kernel_camera_hardware_modified":False,
      "OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported":False,
    }
def strict(v):require(v==facts(),"sourced context identity or safe scalar changed")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original OEM ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for at,expect in ANCHORS.items():require(ins.get(at)==expect,"original exact ISA RVA %x"%at)
    pe=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pe-original-ife-source-ring-independent-allocation-static/RESULT.json").read_text())
    require(pe["historical_original_E004pe_source_allocation_assignment_superseded"] is True and
            pe["allocated_destination_ring_is_command_A_source_ring_proven"] is False and
            pe["allocated_destination_endpoint_table_offset"]=="0x40" and
            pe["distinct_command_A_source_endpoint_table_offset"]=="0x30" and
            pe["destination_context_ring_allocation_structure_bytes"]=="0x1d0",
            "old E004pe misleading source allocation MUST have explicit verified erratum")
    pd=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pd-original-ife-channel-command-a-b-pointer-transfer-static/RESULT.json").read_text())
    require(pd["original_command_a_source_context_plus_0x1b0_is_passed_to_command_b_destination_plus_0x198_source_proven"] is True and
            pd["original_command_a_returned_ring_equals_worker_device_plus_0x8_same_device_generation_proven"] is False,
            "original command A->B transferred pointer but same worker identity unproven")
    def source_allocation_proved(allocated_endpoint_slot,source_endpoint_slot):
        return allocated_endpoint_slot==source_endpoint_slot
    require(not source_allocation_proved(0x40,0x30) and source_allocation_proved(0x40,0x40),
            "different endpoint-table slots cannot establish same owner")
    f=facts();saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==f,"saved corrected scalar result changed")
    else:saved.write_text(json.dumps(f,sort_keys=True,indent=2)+"\n")
    mut=(
      ("sha","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("source_slot","original_command_A_source_endpoint_table_slot_offset","0x40"),
      ("dest_slot","original_command_B_destination_endpoint_table_slot_offset","0x30"),
      ("dest_create","original_destination_endpoint_selected_slot_RVA","0x17fb8"),
      ("dest_store","original_destination_endpoint_object_store_RVA","0x22898"),
      ("dest_ctx","original_destination_endpoint_object_context_load_RVA","0x211e4"),
      ("dest_alloc","original_destination_endpoint_context_plus_0x1b0_ring_allocation_RVA","0x2284c"),
      ("dest_size","original_destination_endpoint_context_plus_0x1b0_ring_object_bytes","0x368"),
      ("dest_ring_store","original_destination_endpoint_context_plus_0x1b0_ring_store_RVA","0x22898"),
      ("cmdA","original_command_A_source_context_plus_0x1b0_pointer_export_RVA","0x214a8"),
      ("cmdB","original_command_B_destination_context_plus_0x198_pointer_import_RVA","0x214c0"),
      ("worker_alloc","original_worker_device_plus_0x8_ring_allocation_RVA","0x17aa4"),
      ("worker_size","original_worker_device_plus_0x8_ring_object_bytes","0x1d0"),
      ("fake_same_context","original_destination_plus_0x1b0_allocation_is_source_command_A_endpoint",True),
      ("fake_source_site","original_command_A_source_plus_0x1b0_allocation_site_source_proven",True),
      ("fake_source_dest_alias","original_source_endpoint_pointer_equals_destination_endpoint_same_session_proven",True),
      ("fake_source_worker_alias","original_source_plus_0x1b0_equals_worker_device_plus_0x8_ring_proven",True),
      ("fake_dest_worker_alias","original_destination_plus_0x1b0_equals_worker_device_plus_0x8_ring_proven",True),
      ("fake_snapshot","original_type_one_event_source_buffer_equals_IFE_snapshot_proven",True),
      ("fake_worker","original_type_one_event_consumed_by_original_worker_same_generation_proven",True),
      ("fake_live","original_live_rear4k_IFE_mode_BF_event_0x0f_observed",True),
      ("fake_top","old_direct_TOP1_to_BF_bit7_status_inference_valid",True),
      ("fake_dma","native_rear_VFE1_BF_FIFO8_per_generation_WM16_IRQ_bus_dma_iommu_retirement_proven",True),
      ("fake_optical","native_rear_hardware_ISP_4k_optical_proven",True),
      ("fake_arm","rear_hardware_ISP_runtime_authorized",True),
      ("fake_golden","Golden_boot_kernel_camera_hardware_modified",True),
      ("fake_private","OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported",True),
    )
    for name,key,val in mut:
        bad=copy.deepcopy(f);bad[key]=val
        try:strict(bad)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PF_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004PF_%d_ORIGINAL_EXACT_ARM64_ANCHORS_%d_NEGATIVES_CORRECTED_DESTINATION_1B0_ALLOCATION_SOURCE_30_UNKNOWN_WORKER_ID_DMA_UNPROVEN_GOLDEN_SAFE"%(len(ANCHORS),len(mut)))
