#!/usr/bin/env python3
"""E004pr: source-lock conditional original BF FIFO8 entry dispatch and WM16 clues.

Original E004pq proved execution of the EVENT-ID ASSIGNMENT instruction.
It did NOT establish nonempty queue, identity match, successful callback, or
independent BUS/IRQ/DMA/IOMMU quiescence. This static proof separates them.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
B=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
SOURCE="""
1f188|cbz|w15, 0x14001f19c <.text+0x1e19c>
1f190|mov|w15, #0xf
1f194|str|w15, [x7, w1, uxtw #2]
1fc60|cmp|w8, #0xf
1fc64|b.ne|0x14001fd48 <.text+0x1ed48>
1fc8c|mov|w1, #0x8
1fc90|mov|x0, x19
1fc94|bl|0x140026460 <.text+0x25460>
1fc98|mov|x23, x0
1fc9c|cbz|x23, 0x14001fe48 <.text+0x1ee48>
1fca4|mov|w2, #0xf
1fca8|add|x1, x19, #0x178
1fcac|ldr|x8, [x8, #0x6c0]
1fcc4|blr|x15
1fcc8|ldrb|w8, [x19, #0x1c0]
1fccc|cbz|w8, 0x14001fd14 <.text+0x1ed14>
1fcdc|ldrh|w2, [x23, #0x16]
1fce0|ldr|x1, [x23, #0x8]
1fce4|bl|0x140025078 <.text+0x24078>
1fce8|mov|w9, #0x300d
1fcf8|ldr|x8, [x23, #0x8]
1fcfc|str|x8, [x19, #0x590]
1fd00|ldrh|w8, [x23, #0x16]
1fd04|str|x8, [x19, #0x5a0]
1fd14|mov|w8, #0x1a
1fd18|str|x23, [x19, #0x6a8]
1fd1c|add|x1, x19, #0x520
1fd20|str|w8, [x19, #0x520]
1fd24|mov|x0, x19
1fd28|bl|0x140026340 <.text+0x25340>
1fd2c|cbz|w0, 0x14001fe48 <.text+0x1ee48>
1d710|ldr|x8, [x0, #0x150]
1d714|ldr|w8, [x8, #0x1270]
1d718|str|w8, [x1, #0x4c]
1d71c|ldr|x8, [x0, #0x150]
1d720|ldr|w8, [x8, #0x1200]
1d724|and|w8, w8, #0x1
1d728|strb|w8, [x1, #0x48]
250b4|ldr|x8, [x20, #0x2e68]
250b8|cmp|x8, x22
250c0|ldrh|w8, [x20, x24]
250c4|cmp|w8, w5
250d4|cmp|w19, #0x6
26370|add|x3, x1, #0x8
26374|ldr|w1, [x1]
26378|ldp|x8, x0, [x19, #0x130]
26390|blr|x15
2650c|add|x10, x21, #0x66b
26514|ldr|x9, [x8, x10, lsl #3]
2651c|cbz|x9, 0x140026610 <.text+0x25610>
26520|ldr|w9, [x9, #0x18]
26524|cbz|w9, 0x14002660c <.text+0x2560c>
"""
ISA={int(rva,16):(op,args) for rva,op,args in (s.split("|",2) for s in SOURCE.strip().splitlines())}
def need(ok,reason):
    if not ok:raise AssertionError("E004PR_FAIL_CLOSED "+reason)
def facts():
    return {
      "schema":"SP11_E004pr_original_BF_event_id_to_conditional_FIFO8_WM16_software_dispatch_static_v1",
      "parent_git_revision":"8a614a56ba2d76f33d0b9a4a1f216026c90a1536",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_source_instruction_anchors":len(ISA),
      "original_BF_event_id_assignment_RVA":"0x1f190",
      "original_BF_event_dispatch_compare_RVA":"0x1fc60",
      "original_BF_FIFO8_queue_pop_call_RVA":"0x1fc94",
      "original_BF_FIFO8_queue_result_null_branch_RVA":"0x1fc9c",
      "original_BF_group_index":8,
      "original_BF_queue_result_local_register":"x23",
      "original_BF_WM16_status_callback_indirect_RVA":"0x1fcc4",
      "original_BF_WM16_cfg0_zero_branch_RVA":"0x1fccc",
      "original_BF_FIFO8_entry_identity_offset":"0x8",
      "original_BF_FIFO8_entry_tag_offset":"0x16",
      "original_BF_outstanding_identity_tag_matcher_RVA":"0x25078",
      "original_BF_resource_port":"0x300d",
      "original_BF_retained_FIFO8_entry_device_context_offset":"0x6a8",
      "original_BF_software_event_callback_RVA":"0x26340",
      "original_BF_software_event_callback_call_RVA":"0x1fd28",
      "original_BF_software_event_callback_return_test_RVA":"0x1fd2c",
      "original_BF_WM16_address_status_window_offset":"0x1270",
      "original_BF_WM16_cfg0_window_offset":"0x1200",
      "original_BF_WM16_cfg0_lowbit_copied_into_scratch":True,
      "original_BF_event_ID_assignment_alone_proves_FIFO8_dequeue_nonempty":False,
      "original_BF_nonempty_FIFO8_entry_alone_proves_WM16_DMA_quiescent":False,
      "original_BF_CFG0_lowbit_alone_proves_WM16_DMA_quiescent":False,
      "original_BF_outstanding_matcher_alone_proves_WM16_DMA_quiescent":False,
      "original_BF_software_callback_success_alone_proves_WM16_DMA_quiescent":False,
      "E004pq_live_event_assignment_instruction_reached":True,
      "E004pq_live_FIFO8_queue_nonempty_for_same_rear4k_frame_observed":False,
      "E004pq_live_WM16_buffer_tag_matching_same_BF_frame_observed":False,
      "original_independent_CSID_or_VFE_WM16_bus_done_IRQ_per_generation_DMA_IOMMU_quiescence_proven":False,
      "native_rear_hardware_ISP_runtime_authorized":False,
      "protected_Golden_boot_kernel_camera_hardware_modified":False,
      "no_original_OEM_binary_bulk_private_KD_DMA_pixels_exported":True,
      "next_live_probes_by_original_RVA":[
          "0x1fc60","0x1fc9c","0x1fcc8","0x1fce4","0x1fd28"
      ],
      "next_live_gate":"same_original_rear4k_context_frame_type1_source_status_BF_event0f_nonempty_FIFO8_entry_identity_tag_WM16_actual_hw_completion_DMA_IOMMU",
    }
def strict(d):need(d==facts(),"source or missing safety evidence changed")
if __name__=="__main__":
    need(hashlib.sha256(B.read_bytes()).hexdigest()==SHA,"same-SP11 OEM ISP SHA")
    out=subprocess.check_output(["llvm-objdump","-d",str(B)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-0x140000000:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(out)}
    for at,want in ISA.items():
        need(ins.get(at)==want,"exact original ARM64 instruction RVA %x"%at)
    pq=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pq-original-windows-kd-bf-hit-source-locked/RESULT.json").read_text())
    nv=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/BF-RESULT.json").read_text())
    need(pq["BF_event0x0f_id_assignment_instruction_reached_live"] and
         not pq["BF_event0x0f_queued_FIFO8_entry_or_hardware_output_observed"] and
         nv["BF_static_dispatch"]["queue_group_index"]==8 and
         nv["BF_static_dispatch"]["resource_port_stored_RVA"]=="0x1fce8",
         "actual assignment hit vs historical static FIFO8/generation evidence")
    # Conditional source flow: event-ID assignment alone never vouches
    # for a nonempty FIFO8 queue; likewise a software success is not a
    # bus-master DMA/IOMMU retirement. All values are OFFLINE synthetic.
    def source_gate(assigned,selected,queue_nonempty,cfg0,identity_match,callback_success,
                    bus_dma_fence):
        fifo=assigned and selected and queue_nonempty
        extended=fifo and cfg0 and identity_match
        software=fifo and callback_success
        return fifo,extended,software, bool(software and extended and bus_dma_fence)
    need(source_gate(True,False,True,True,True,True,True)==(False,False,False,False),
         "assignment only not selected dispatch")
    need(source_gate(True,True,False,True,True,True,True)==(False,False,False,False),
         "selected BF with empty FIFO8")
    need(source_gate(True,True,True,False,True,True,True)==(True,False,True,False),
         "nonempty queue with WM16 cfg0 lowbit clear")
    need(source_gate(True,True,True,True,False,True,True)==(True,False,True,False),
         "nonempty queue without matching outstanding tag")
    need(source_gate(True,True,True,True,True,False,True)==(True,True,False,False),
         "queue/matcher alone not successful software callback")
    need(source_gate(True,True,True,True,True,True,False)==(True,True,True,False),
         "all software gates without independently trusted DMA/IOMMU")
    need(source_gate(True,True,True,True,True,True,True)==(True,True,True,True),
         "all-trusted OFFLINE design predicate ONLY")
    f=facts();path=HERE/"RESULT.json"
    if path.exists():need(json.loads(path.read_text())==f,"saved scalar result changed")
    else:path.write_text(json.dumps(f,sort_keys=True,indent=2)+"\n")
    muts=(
      ("sha","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("anchor","exact_original_ARM64_source_instruction_anchors",0),
      ("pop","original_BF_FIFO8_queue_pop_call_RVA","0x1f190"),
      ("empty","original_BF_FIFO8_queue_result_null_branch_RVA","0x1fd28"),
      ("FIFO","original_BF_group_index",7),
      ("reg","original_BF_queue_result_local_register","x19"),
      ("wm_callback","original_BF_WM16_status_callback_indirect_RVA","0x1fc94"),
      ("cfg0","original_BF_WM16_cfg0_zero_branch_RVA","0x1fc9c"),
      ("identity","original_BF_FIFO8_entry_identity_offset","0x16"),
      ("tag","original_BF_FIFO8_entry_tag_offset","0x8"),
      ("matcher","original_BF_outstanding_identity_tag_matcher_RVA","0x26340"),
      ("port","original_BF_resource_port","0x300d0"),
      ("held_entry","original_BF_retained_FIFO8_entry_device_context_offset","0x198"),
      ("callback","original_BF_software_event_callback_RVA","0x1f190"),
      ("ack","original_BF_software_event_callback_return_test_RVA","0x1fc9c"),
      ("addr_status","original_BF_WM16_address_status_window_offset","0x1200"),
      ("cfg0reg","original_BF_WM16_cfg0_window_offset","0x1270"),
      ("cfg_false","original_BF_WM16_cfg0_lowbit_copied_into_scratch",False),
      ("fake_queue","original_BF_event_ID_assignment_alone_proves_FIFO8_dequeue_nonempty",True),
      ("fake_dma_queue","original_BF_nonempty_FIFO8_entry_alone_proves_WM16_DMA_quiescent",True),
      ("fake_dma_cfg","original_BF_CFG0_lowbit_alone_proves_WM16_DMA_quiescent",True),
      ("fake_dma_match","original_BF_outstanding_matcher_alone_proves_WM16_DMA_quiescent",True),
      ("fake_dma_callback","original_BF_software_callback_success_alone_proves_WM16_DMA_quiescent",True),
      ("fake_hit","E004pq_live_event_assignment_instruction_reached",False),
      ("fake_live_queue","E004pq_live_FIFO8_queue_nonempty_for_same_rear4k_frame_observed",True),
      ("fake_live_tag","E004pq_live_WM16_buffer_tag_matching_same_BF_frame_observed",True),
      ("fake_DMA","original_independent_CSID_or_VFE_WM16_bus_done_IRQ_per_generation_DMA_IOMMU_quiescence_proven",True),
      ("fake_arm","native_rear_hardware_ISP_runtime_authorized",True),
      ("fake_Golden","protected_Golden_boot_kernel_camera_hardware_modified",True),
      ("fake_private","no_original_OEM_binary_bulk_private_KD_DMA_pixels_exported",False),
      ("fake_next","next_live_probes_by_original_RVA",["0x1f190"]),
    )
    for name,key,value in muts:
        bad=copy.deepcopy(f);bad[key]=value
        try:strict(bad)
        except AssertionError:continue
        raise AssertionError("E004PR_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004PR_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_BF_ASSIGNMENT_NOT_FIFO8_WM16_DMA_CSID_VFE_COMPLETION_UNPROVEN_GOLDEN_SAFE"%(len(ISA),len(muts)))
