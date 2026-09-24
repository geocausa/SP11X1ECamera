#!/usr/bin/env python3
"""E004oq: original IFE mode-selected finalizer callback registers vs safe DMA.

Same-SP11 original OEM binary is read-only; no driver, bulk disassembly,
optical data, DMA address, firmware or KD logs are copied into Git.
"""
import bisect,copy,hashlib,json,re,struct,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
19fa8|add|x8, x19, #0x6b, lsl #12
19fac|ldr|w8, [x8, #0x678]
19fb0|cmp|w8, #0x0
19fec|adrp|x8, 0x14001b000 <.text+0x1a000>
19ff0|add|x9, x8, #0xe80
19ff4|adrp|x8, 0x14001d000 <.text+0x1c000>
19ff8|add|x8, x8, #0x2b0
19ffc|csel|x9, x9, x8, ne
1a000|add|x8, x19, #0x6b, lsl #12
1a004|str|x9, [x8, #0x690]
27278|pacibsp|
2732c|add|x2, x19, #0x164
27330|add|x8, x19, #0x6b, lsl #12
27340|ldr|x8, [x8, #0x690]
27344|mov|x0, x19
27348|mov|x15, x8
27358|blr|x15
2738c|strb|w23, [x19, #0x171]
1be80|pacibsp|
1be84|stp|x29, x30, [sp, #-0x10]!
1be88|mov|x29, sp
1be8c|mov|w8, #-0x24000000
1be90|str|w8, [x0, #0x164]
1be94|ldr|x8, [x0, #0x140]
1be98|mov|w9, #0x7
1be9c|str|w9, [x0, #0x15c]
1bea0|mov|x1, #0x24
1bea4|str|w9, [x8, #0x24]
1bea8|ldr|w2, [x0, #0x15c]
1beac|bl|0x14001c958 <.text+0x1b958>
1beb0|ldr|x9, [x0, #0x140]
1beb4|mov|x1, #0x28
1beb8|ldr|w8, [x0, #0x160]
1bebc|str|w8, [x9, #0x28]
1bec0|ldr|w2, [x0, #0x15c]
1bec4|bl|0x14001c958 <.text+0x1b958>
1bec8|ldr|x9, [x0, #0x150]
1becc|ldr|w8, [x0, #0x164]
1bed0|str|w8, [x9, #0x18]
1bed4|ldr|x9, [x0, #0x150]
1bed8|mov|w8, #0x1ff
1bedc|str|w8, [x9, #0x8]
1bee0|ldp|x29, x30, [sp], #0x10
1bee4|autibsp|
1bee8|ret|
1d2b0|pacibsp|
1d2b4|stp|x29, x30, [sp, #-0x10]!
1d2b8|mov|x29, sp
1d2bc|ldr|x9, 0x14001d340 <.text+0x1c340>
1d2c0|add|x10, x0, #0x15c
1d2c4|mov|x8, #0xd0000000
1d2c8|str|x9, [x10]
1d2cc|add|x11, x0, #0x164
1d2d0|str|x8, [x11]
1d2d4|ldr|x8, [x0, #0x140]
1d2d8|mov|x1, #0x34
1d2dc|str|w9, [x8, #0x34]
1d2e0|ldr|w2, [x10]
1d2e4|bl|0x14001c958 <.text+0x1b958>
1d2e8|ldr|x9, [x0, #0x140]
1d2ec|mov|x1, #0x38
1d2f0|ldr|w8, [x0, #0x160]
1d2f4|str|w8, [x9, #0x38]
1d2f8|ldr|w2, [x10]
1d2fc|bl|0x14001c958 <.text+0x1b958>
1d300|ldr|w8, [x11]
1d304|ldr|x9, [x0, #0x150]
1d308|str|w8, [x9, #0x18]
1d30c|ldr|w8, [x0, #0x168]
1d310|ldr|x9, [x0, #0x150]
1d314|str|w8, [x9, #0x1c]
1d318|add|x8, x0, #0x6b, lsl #12
1d31c|ldrb|w8, [x8, #0x6f0]
1d320|cbz|w8, 0x14001d330 <.text+0x1c330>
1d324|ldr|x9, [x0, #0x150]
1d328|mov|w8, #0xfffffff
1d32c|str|w8, [x9, #0x8]
1d330|ldp|x29, x30, [sp], #0x10
1d334|autibsp|
1d338|ret|
1c958|ldr|w8, [x0, #0x120]
1c95c|mov|x9, #0x0
1c960|cbnz|w8, 0x14001c96c <.text+0x1b96c>
1c964|add|x9, x1, #0xaf, lsl #12
1c968|b|0x14001c978 <.text+0x1b978>
1c96c|cmp|w8, #0x1
1c970|b.ne|0x14001c978 <.text+0x1b978>
1c974|add|x9, x1, #0xb6, lsl #12
1c978|add|x8, x1, #0x350
1c97c|lsl|x8, x8, #4
1c980|str|x9, [x8, x0]
1c984|add|x8, x0, x1, lsl #4
1c988|str|w2, [x8, #0x3508]
1c98c|ret|
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (row.split("|",2) for row in SOURCE.strip().splitlines())}
def need(ok,msg):
    if not ok:raise AssertionError("E004OQ_FAIL_CLOSED "+msg)
def pdata(data):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    need(data[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",data,pe+4)[0]==0xaa64,"original ARM64 PE")
    start=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    for i in range(struct.unpack_from("<H",data,pe+6)[0]):
        o=start+40*i
        if data[o:o+8].rstrip(b"\0")==b".pdata":
            _,_,size,raw=struct.unpack_from("<IIII",data,o+8)
            return sorted(set(struct.unpack_from("<I",data,raw+k)[0] for k in range(0,size-7,8)))
    raise AssertionError("original .pdata")
def result():
    return {
      "schema":"sp11-e004oq-original-IFE-mode-selected-finalizer-MMIO-writes-not-DMA-ack-static-v1",
      "parent_git_revision":"7f24b418d9296aeaf01ec09cf84fc9d54723ee32",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "original_exact_ARM64_instruction_anchors":len(ANCHORS),
      "IFE_finalization_callback_context_field_offset":"0x6b690",
      "conditional_selector_state_context_field_offset":"0x6b678",
      "original_selection_RVA":"0x19ffc",
      "original_callback_field_store_RVA":"0x1a004",
      "nonzero_state_selected_finalizer_entry_RVA":"0x1be80",
      "zero_state_selected_finalizer_entry_RVA":"0x1d2b0",
      "stop_helper_selected_finalizer_indirect_call_RVA":"0x27358",
      "stop_helper_pending_progress_flag_store_after_callback_RVA":"0x2738c",
      "nonzero_state_writes_original_base_register_offsets":["0x24","0x28"],
      "nonzero_state_writes_selected_window_register_offsets":["0x18","0x8"],
      "zero_state_writes_original_base_register_offsets":["0x34","0x38"],
      "zero_state_writes_selected_window_register_offsets":["0x18","0x1c"],
      "zero_state_conditional_selected_window_extra_register_offset":"0x8",
      "shared_software_bookkeeping_helper_RVA":"0x1c958",
      "shared_helper_full_original_instructions":14,
      "both_finalizers_have_register_control_writes_but_no_explicit_WM16_dma_irq_retire_wait_in_bounded_bodies":True,
      "active_rear_Windows_IFE_selected_finalizer_and_actual_MMIO_base_proven":False,
      "per_mode_hardware_bus_stop_IRQ_ack_and_DMA_retirement_proven":False,
      "live_Windows_rear_BF_0x0f_FIFO8_completion_observed":False,
      "Linux_native_rear_processed_ISP_4k_optical_frame_proven":False,
      "Golden_boot_or_camera_hardware_modified":False,
      "private_OEM_binary_disassembly_dma_KD_optical_data_exported":False,
    }
def strict(x):need(x==result(),"unverified claim or changed schema")
if __name__=="__main__":
    d=ISP.read_bytes();need(hashlib.sha256(d).hexdigest()==SHA,"same SP11 original ISP SHA")
    dump=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(dump)}
    for rva,inst in ANCHORS.items():need(asm.get(rva)==inst,"original ISA RVA %x"%rva)
    for lo,hi in ((0x1be80,0x1beec),(0x1d2b0,0x1d33c),(0x1c958,0x1c990)):
        need(all(a in ANCHORS for a in range(lo,hi,4)),"complete function body %x"%lo)
    fn=pdata(d)
    for entry in (0x1be80,0x1d2b0):
        i=bisect.bisect_left(fn,entry);need(i<len(fn) and fn[i]==entry,"original PE entry %x"%entry)
    for lo,hi in ((0x1be80,0x1beec),(0x1d2b0,0x1d33c)):
        need(all(ANCHORS[a][0] not in ("blr","br","dsb","wfe","wfi") for a in range(lo,hi,4)),"unknown indirect hardware wait")
    prior=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004op-ife-stop-pending-flag-two-event-modes-static/RESULT.json").read_text())
    need(prior["stop_resource_selected_callback_invocation_RVA"]=="0x27358" and
         prior["resource_callback_0x690_actual_hardware_bus_irq_dma_contract_proven"] is False and
         prior["stop_resource_pending_flag_set_after_callback_RVA"]=="0x2738c","E004op conservative finalizer boundary")
    j=result();saved=HERE/"RESULT.json"
    if saved.exists():need(json.loads(saved.read_text())==j,"saved scalar source mismatch")
    else:saved.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    mutations=(
      ("fake_SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("fake_nonzero","nonzero_state_selected_finalizer_entry_RVA","0x1d2b0"),
      ("fake_zero","zero_state_selected_finalizer_entry_RVA","0x1be80"),
      ("fake_slot","IFE_finalization_callback_context_field_offset","0x6b688"),
      ("fake_base","zero_state_writes_original_base_register_offsets",["0x24","0x28"]),
      ("fake_window","zero_state_writes_selected_window_register_offsets",["0x18","0x8"]),
      ("fake_helper","shared_software_bookkeeping_helper_RVA","0x1c990"),
      ("fake_wait","both_finalizers_have_register_control_writes_but_no_explicit_WM16_dma_irq_retire_wait_in_bounded_bodies",False),
      ("fake_live","active_rear_Windows_IFE_selected_finalizer_and_actual_MMIO_base_proven",True),
      ("fake_DMA","per_mode_hardware_bus_stop_IRQ_ack_and_DMA_retirement_proven",True),
      ("fake_BF","live_Windows_rear_BF_0x0f_FIFO8_completion_observed",True),
      ("fake_4k","Linux_native_rear_processed_ISP_4k_optical_frame_proven",True),
      ("fake_Golden","Golden_boot_or_camera_hardware_modified",True),
      ("fake_export","private_OEM_binary_disassembly_dma_KD_optical_data_exported",True),
    )
    for name,k,v in mutations:
        m=copy.deepcopy(j);m[k]=v
        try:strict(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OQ_NEGATIVE_FAILED_OPEN "+name)
    print("PASS_E004OQ_%d_ORIGINAL_ARM64_ANCHORS_2_ORIGINAL_PE_ENTRIES_%d_NEGATIVES_FINALIZER_REGISTER_WRITES_NOT_DMA_ACK_GOLDEN_SAFE"%(len(ANCHORS),len(mutations)))
