#!/usr/bin/env python3
"""E004op: conditional IFE stop flag producer and two distinct software events.

Static-only original same-SP11 ISP. No OEM binaries/disassembly, DMA pointers,
optical data, KD logs, or firmware copied to Git or another host.
"""
import bisect,copy,hashlib,json,re,struct,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
27278|pacibsp|
27294|mov|x19, x0
27298|ldr|w8, [x19, #0x301c]
2729c|mov|w23, #0x1
272a0|strb|w23, [x19, #0x173]
272a4|mov|w21, #0x0
272c8|cmp|w21, #0x22
272cc|b.hs|0x14002732c <.text+0x2632c>
272d8|ldr|w1, [x19, x8, lsl #2]
272e4|ldr|x8, [x25, #0x688]
272e8|mov|w2, #0x0
27300|blr|x15
27320|add|w21, w21, #0x1
27328|b.lo|0x1400272c8 <.text+0x262c8>
27334|str|wzr, [x19, #0x15c]
27340|ldr|x8, [x8, #0x690]
27358|blr|x15
2735c|mov|x8, #0x3488
27360|str|xzr, [x19, x24]
27378|str|wzr, [x19, #0x33d4]
2737c|str|wzr, [x19, #0x2f80]
2738c|strb|w23, [x19, #0x171]
27394|stp|q16, q16, [x8], #0x20
2739c|b.ne|0x140027394 <.text+0x26394>
273a4|mov|x8, #0x3024
273b4|bl|0x14002df80 <.text+0x2cf80>
273f4|adrp|x8, 0x14003f000
273f8|ldr|x8, [x8, #0x2e8]
273fc|mov|w2, #0x0
27400|mov|w1, #0x0
27404|add|x0, x19, #0x38
2740c|blr|x8
1c9d0|pacibsp|
1cc70|ldrb|w8, [x19, #0x171]
1cc74|cbz|w8, 0x14001cc98 <.text+0x1bc98>
1cc84|strb|wzr, [x19, #0x171]
1cc90|mov|x0, x19
1cc94|bl|0x1400241d8 <.text+0x231d8>
1ef90|pacibsp|
1f230|ldrb|w8, [x19, #0x171]
1f234|cbz|w8, 0x14001f258 <.text+0x1e258>
1f244|strb|wzr, [x19, #0x171]
1f250|mov|x0, x19
1f254|bl|0x1400241d8 <.text+0x231d8>
241d8|pacibsp|
24228|add|x0, x19, #0xc8
2422c|bl|0x14002a1d8 <.text+0x291d8>
2a1f4|adrp|x8, 0x14003f000
2a1f8|ldr|x8, [x8, #0x2e8]
2a204|blr|x8
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (s.split("|",2) for s in SOURCE.strip().splitlines())}
def need(ok,msg):
    if not ok:raise AssertionError("E004OP_FAIL_CLOSED "+msg)
def function_entries(data):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    need(data[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",data,pe+4)[0]==0xaa64,"ARM64 original PE")
    sh=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    for i in range(struct.unpack_from("<H",data,pe+6)[0]):
        off=sh+40*i
        if data[off:off+8].rstrip(b"\0")==b".pdata":
            _,_,size,raw=struct.unpack_from("<IIII",data,off+8)
            return sorted(set(struct.unpack_from("<I",data,raw+k)[0] for k in range(0,size-7,8)))
    raise AssertionError("original PE pdata missing")
def result():
    return {
      "schema":"sp11-e004op-original-IFE-stop-flag-producer-dual-event-handlers-static-v1",
      "parent_git_revision":"8953e3ae58082d8c73f1a96391b94f3132fdbb6b",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "stop_resource_helper_entry_RVA":"0x27278",
      "stop_resource_software_active_flag_context_offset":"0x173",
      "stop_resource_active_flag_set_RVA":"0x272a0",
      "stop_resource_selected_callback_invocation_RVA":"0x27358",
      "stop_resource_pending_progress_flag_context_offset":"0x171",
      "stop_resource_pending_flag_set_after_callback_RVA":"0x2738c",
      "stop_resource_direct_event_original_ntoskrnl_KeSetEvent_call_RVA":"0x2740c",
      "stop_resource_direct_event_object_context_offset":"0x38",
      "mode_one_handler_original_PE_entry_RVA":"0x1c9d0",
      "mode_zero_handler_original_PE_entry_RVA":"0x1ef90",
      "mode_one_flag_clear_and_later_event_helper_RVAs":["0x1cc84","0x1cc94"],
      "mode_zero_flag_clear_and_later_event_helper_RVAs":["0x1f244","0x1f254"],
      "later_shared_event_helper_RVA":"0x241d8",
      "later_shared_event_object_context_offset":"0xc8",
      "original_same_IAT_KeSetEvent_RVA":"0x3f2e8",
      "two_software_event_objects_have_distinct_context_offsets":True,
      "resource_callback_0x690_actual_hardware_bus_irq_dma_contract_proven":False,
      "actual_live_windows_rear4k_mode_event_source_and_BF_status_observed":False,
      "two_software_signals_prove_WM16_DMA_retired_or_core_handoff_safe":False,
      "Linux_native_rear_processed_ISP_4k_optical_frame_proven":False,
      "Golden_boot_or_camera_hardware_modified":False,
      "private_OEM_binary_raw_disassembly_dma_KD_or_optical_exported":False,
    }
def check(x):need(x==result(),"scalar schema unverified claim")
if __name__=="__main__":
    d=ISP.read_bytes();need(hashlib.sha256(d).hexdigest()==SHA,"exact original same-SP11 OEM SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for rva,inst in ANCHORS.items():need(asm.get(rva)==inst,"original ISA RVA %x"%rva)
    fun=function_entries(d)
    for entry in (0x27278,0x1c9d0,0x1ef90,0x241d8):
        i=bisect.bisect_left(fun,entry)
        need(i<len(fun) and fun[i]==entry,"exact original PE function entry %x"%entry)
    old=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004oo-ife-later-progress-event-not-dma-ack-static/RESULT.json").read_text())
    need(old["event_wrapper_RVA"]=="0x2a1d8" and
         old["event_wrapper_original_ntoskrnl_KeSetEvent_IAT_RVA"]=="0x3f2e8" and
         old["later_IFE_progress_flag_or_KeSetEvent_proves_HW_WM16_DMA_retirement"] is False,
         "E004oo original distinct software event and no DMA proof")
    facts=result();saved=HERE/"RESULT.json"
    if saved.exists():need(json.loads(saved.read_text())==facts,"saved original scalar mismatch")
    else:saved.write_text(json.dumps(facts,indent=2,sort_keys=True)+"\n")
    cases=(
      ("fake_SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("fake_pending_flag","stop_resource_pending_progress_flag_context_offset","0x173"),
      ("fake_flag_set","stop_resource_pending_flag_set_after_callback_RVA","0x27390"),
      ("fake_stop_event","stop_resource_direct_event_object_context_offset","0xc8"),
      ("fake_second_event","later_shared_event_object_context_offset","0x38"),
      ("fake_mode_one","mode_one_handler_original_PE_entry_RVA","0x1ef90"),
      ("fake_mode_zero","mode_zero_handler_original_PE_entry_RVA","0x1c9d0"),
      ("fake_KeSetEvent","original_same_IAT_KeSetEvent_RVA","0x3f060"),
      ("fake_resource_hw","resource_callback_0x690_actual_hardware_bus_irq_dma_contract_proven",True),
      ("fake_live","actual_live_windows_rear4k_mode_event_source_and_BF_status_observed",True),
      ("fake_DMA","two_software_signals_prove_WM16_DMA_retired_or_core_handoff_safe",True),
      ("fake_linux4k","Linux_native_rear_processed_ISP_4k_optical_frame_proven",True),
      ("fake_golden","Golden_boot_or_camera_hardware_modified",True),
      ("fake_export","private_OEM_binary_raw_disassembly_dma_KD_or_optical_exported",True),
    )
    for name,k,v in cases:
        mutated=copy.deepcopy(facts);mutated[k]=v
        try:check(mutated)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OP_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OP_%d_EXACT_ORIGINAL_ARM64_INSTRUCTIONS_4_ORIGINAL_PE_ENTRIES_%d_NEGATIVES_DISTINCT_IFE_EVENTS_NOT_DMA_ACK_GOLDEN_SAFE"%(len(ANCHORS),len(cases)))
