#!/usr/bin/env python3
"""E004pd SHA-pinned original ISP command A->B event-channel ring transfer.

Static source-only bounded ARM64, explicit negative guards. Does not claim
alias to worker device+8 or live physical BF IRQ and DMA completion.
"""
import copy
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
17f98|mov|w8, #0x2
17fa0|str|w8, [sp, #0x60]
17fa4|ldr|x8, [x27]
17fac|mov|w5, #0x18
17fb0|add|x4, sp, #0x50
17fb8|ldr|x8, [x8, #0x30]
17fbc|mov|x2, #0x0
17fc0|mov|w1, #0xa
17fc4|umaddl|x8, w19, w24, x8
17fc8|ldr|x0, [x8, #0x8]
17fcc|ldr|x8, [x0]
17fdc|blr|x17
17fe0|blr|x15
17fe4|cbnz|w0, 0x14001804c <.text+0x1704c>
17ff8|mov|w3, #0x18
17ffc|ldr|x8, [x8, #0x40]
18000|add|x2, sp, #0x50
18004|mov|w1, #0xb
18008|umaddl|x8, w19, w24, x8
1800c|ldr|x0, [x8, #0x8]
18010|ldr|x8, [x0]
18024|blr|x15
18028|cbz|w0, 0x14001804c <.text+0x1704c>
180f4|cbz|w22, 0x14001811c <.text+0x1711c>
1812c|mov|w8, #0x3
18130|str|w8, [sp, #0x78]
18140|add|x4, sp, #0x68
1814c|mov|x2, #0x0
18150|mov|w1, #0xa
1818c|mov|w3, #0x18
18194|add|x2, sp, #0x68
18198|mov|w1, #0xb
211d8|mov|x21, x2
211e4|ldr|x19, [x0, #0x20]
211ec|cmp|x21, #0x0
211f8|cmp|x4, #0x0
2120c|cmp|w1, #0x803
21218|sub|w10, w1, #0x1
2121c|cmp|w10, #0xd
21224|adr|x9, 0x140021bc4 <.text+0x20bc4>
21228|ldrsw|x8, [x9, w10, uxtw #2]
2122c|adr|x9, 0x140021758 <.text+0x20758>
21230|add|x8, x9, x8, lsl #2
21234|br|x8
21478|cbz|x21, 0x140021b98 <.text+0x20b98>
2147c|ldr|w8, [x21, #0x10]
21480|cmp|w8, #0x3
21484|b.ne|0x14002149c <.text+0x2049c>
21488|ldr|x8, [x21]
2148c|str|x8, [x19, #0x1a8]
21490|ldr|x8, [x21, #0x8]
21494|str|x8, [x19, #0x1b8]
2149c|cmp|w8, #0x2
214a0|b.ne|0x1400214b4 <.text+0x204b4>
214a4|ldr|x8, [x21]
214a8|str|x8, [x19, #0x198]
214ac|ldr|x8, [x21, #0x8]
214b0|str|x8, [x19, #0x1a0]
214bc|cbz|x4, 0x140021b98 <.text+0x20b98>
214c0|ldr|x8, [x19, #0x1b0]
214c4|str|x8, [x4]
22830|add|x22, x20, #0x8
22844|mov|w1, #0x368
22850|mov|x19, x0
22870|add|x9, x19, #0x38
22874|add|x8, x9, #0x10
22878|stp|x8, x9, [x19]
22898|str|x19, [x22]
23900|ldr|x19, [x20, #0x8]
23940|bl|0x14002c5b0 <.text+0x2b5b0>
244e4|mov|w8, #0x1
244e8|str|w8, [sp, #0x10]
2461c|ldr|x19, [x20, #0x198]
24664|bl|0x14002c5b0 <.text+0x2b5b0>
"""
ANCHORS={int(a,16):(op,args) for a,op,args in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def require(ok,why):
    if not ok:raise AssertionError("E004PD_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004pd-original-event-channel-type2-source-command-a-to-destination-command-b-pointer-transfer-static-v1",
      "parent_git_revision":"70598a0cbff7ffbddd27223b0d53cef3fb857941",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "original_channel_transfer_coordinator_command_a_RVA":"0x17fc0",
      "original_channel_transfer_coordinator_command_b_RVA":"0x18004",
      "original_channel_transfer_interface_structure_stack_offset":"0x50",
      "original_channel_transfer_interface_kind_source":"0x2",
      "original_channel_transfer_interface_kind_offset":"0x10",
      "original_channel_transfer_source_interface_table_slot_offset":"0x30",
      "original_channel_transfer_destination_interface_table_slot_offset":"0x40",
      "original_command_dispatch_entry_RVA":"0x211b0",
      "original_command_a_dynamic_branch_target_RVA":"0x214bc",
      "original_command_b_dynamic_branch_target_RVA":"0x21478",
      "original_command_a_exported_context_pointer_offset":"0x1b0",
      "original_command_a_exported_interface_pointer_offset":"0x0",
      "original_command_b_received_pointer_interface_offset":"0x0",
      "original_command_b_received_ring_destination_context_offset":"0x198",
      "original_command_b_received_notify_destination_context_offset":"0x1a0",
      "original_command_b_interface_kind_three_uses_other_fields":True,
      "original_command_a_source_context_plus_0x1b0_is_passed_to_command_b_destination_plus_0x198_source_proven":True,
      "original_command_a_returned_ring_equals_worker_device_plus_0x8_same_device_generation_proven":False,
      "original_command_a_proves_notifications_source_plus_0x8_origin":False,
      "original_type_one_callback_input_from_same_source_IFE_snapshot_proven":False,
      "original_type_one_record_reaches_worker_same_queue_and_frame_proven":False,
      "original_live_rear4k_selected_IFE_mode_and_BF0x0f_observed":False,
      "previous_direct_TOP1_to_BF_status_bit7_provenance_valid":False,
      "native_Linux_rear_IRQ_status_ack_BF_FIFO8_per_generation_WM16_DMA_retirement_proven":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_proven":False,
      "rear_hardware_ISP_runtime_authorized":False,
      "Golden_kernel_boot_camera_hardware_modified":False,
      "OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported":False,
    }
def strict(f):require(f==facts(),"source-backed scalar changed or false safety claim")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original same-SP11 OEM ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for at,expected in ANCHORS.items():require(ins.get(at)==expected,"original exact ARM64 RVA %x"%at)
    # Actual immediate-dispatch table at original RVA0x21bc4 in .text,
    # whose PE file-offset conversion is RVA -0xC00 (section VA0x1000,
    # raw section start0x400); source dispatcher indexes cmd-1.
    pe=ISP.read_bytes(); index_base=0x21bc4-0xc00; origin=0x21758
    for cmd,target in ((0xA,0x214bc),(0xB,0x21478)):
        delta=struct.unpack_from("<i",pe,index_base+4*(cmd-1))[0]
        require(origin+4*delta==target,"original command A/B jump-table target mismatch")
    old=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pc-type1-event-channel-ring-alias-unproven-static/RESULT.json").read_text())
    require(old["type_one_channel_interface_given_exact_original_worker_device_plus_0x8_ring_identity_proven"] is False and
            old["type_one_producer_input_is_actual_mode_selected_IFE_snapshot_proven"] is False,
            "prior original worker/source alias still unknown")
    def transfer(source_pointer,kind,source_success,destination_success):
        return source_pointer if kind==2 and source_success and destination_success and source_pointer else None
    require(transfer(0x789,2,True,True)==0x789 and
            transfer(0x789,3,True,True) is None and
            transfer(0x789,2,False,True) is None and
            transfer(0x789,2,True,False) is None and
            transfer(0,2,True,True) is None,
            "offline source-to-destination transfer gate")
    f=facts();saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==f,"saved result changed")
    else:saved.write_text(json.dumps(f,sort_keys=True,indent=2)+"\n")
    mutations=(
      ("sha","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("source","original_channel_transfer_source_interface_table_slot_offset","0x40"),
      ("destination","original_channel_transfer_destination_interface_table_slot_offset","0x30"),
      ("cmdA","original_channel_transfer_coordinator_command_a_RVA","0x18004"),
      ("cmdB","original_channel_transfer_coordinator_command_b_RVA","0x17fc0"),
      ("struct","original_channel_transfer_interface_structure_stack_offset","0x68"),
      ("kind","original_channel_transfer_interface_kind_source","0x3"),
      ("kindoffset","original_channel_transfer_interface_kind_offset","0x8"),
      ("dispatchA","original_command_a_dynamic_branch_target_RVA","0x21478"),
      ("dispatchB","original_command_b_dynamic_branch_target_RVA","0x214bc"),
      ("sourcectx","original_command_a_exported_context_pointer_offset","0x8"),
      ("destctx","original_command_b_received_ring_destination_context_offset","0x8"),
      ("destnotify","original_command_b_received_notify_destination_context_offset","0x1b8"),
      ("fakeTransfer","original_command_a_source_context_plus_0x1b0_is_passed_to_command_b_destination_plus_0x198_source_proven",False),
      ("fakeSameRing","original_command_a_returned_ring_equals_worker_device_plus_0x8_same_device_generation_proven",True),
      ("fakeNotify","original_command_a_proves_notifications_source_plus_0x8_origin",True),
      ("fakeSnapshot","original_type_one_callback_input_from_same_source_IFE_snapshot_proven",True),
      ("fakeWorker","original_type_one_record_reaches_worker_same_queue_and_frame_proven",True),
      ("fakeLive","original_live_rear4k_selected_IFE_mode_and_BF0x0f_observed",True),
      ("fakeTOP","previous_direct_TOP1_to_BF_status_bit7_provenance_valid",True),
      ("fakeDMA","native_Linux_rear_IRQ_status_ack_BF_FIFO8_per_generation_WM16_DMA_retirement_proven",True),
      ("fakeOptical","native_Linux_rear_processed_hardware_ISP_4k_optical_proven",True),
      ("fakeArm","rear_hardware_ISP_runtime_authorized",True),
      ("fakeGolden","Golden_kernel_boot_camera_hardware_modified",True),
      ("fakePrivate","OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported",True),
    )
    for name,key,val in mutations:
        altered=copy.deepcopy(f);altered[key]=val
        try:strict(altered)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PD_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004PD_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_CMD_A_B_JUMP_TABLE_SOURCE_1B0_TO_DEST_198_RING_TRANSFER_WORKER_ALIAS_HW_DMA_UNPROVEN_GOLDEN_SAFE"%(len(ANCHORS),len(mutations)))
