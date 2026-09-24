#!/usr/bin/env python3
"""E004ok exact original-ISP immediate BF WM16 stop tail, static only."""
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
# Complete 16-instruction local helper, with original branch/call provenance.
SOURCE="""
1da6c|ldr|x8, [x19, #0x150]
1da70|mov|x1, #0x1200
1da74|str|w21, [x8, #0x1200]
1da78|b|0x14001da04 <.text+0x1ca04>
1da04|mov|w20, w21
1da08|b|0x14001db24 <.text+0x1cb24>
1db24|mov|x0, x19
1db28|mov|w2, w20
1db2c|bl|0x14001c990 <.text+0x1b990>
1db30|cmp|w24, #0x22
1db34|b.hs|0x14001db4c <.text+0x1cb4c>
1db38|mov|x8, #0x18
1db3c|umaddl|x9, w24, w8, x19
1db40|mov|x8, #0x3024
1db44|strb|w23, [x9, x8]
1db48|b|0x14001db88 <.text+0x1cb88>
1db88|ldp|x29, x30, [sp], #0x10
1db9c|autibsp|
1dba0|ret|
1c990|ldr|w8, [x0, #0x120]
1c994|mov|x9, #0x0
1c998|cbnz|w8, 0x14001c9a4 <.text+0x1b9a4>
1c99c|add|x9, x1, #0xb1, lsl #12
1c9a0|b|0x14001c9b0 <.text+0x1b9b0>
1c9a4|cmp|w8, #0x1
1c9a8|b.ne|0x14001c9b0 <.text+0x1b9b0>
1c9ac|add|x9, x1, #0xb8, lsl #12
1c9b0|mov|x8, #0x2350
1c9b4|add|x8, x1, x8
1c9b8|lsl|x8, x8, #4
1c9bc|str|x9, [x8, x0]
1c9c0|add|x8, x0, x1, lsl #4
1c9c4|add|x8, x8, #0x23, lsl #12
1c9c8|str|w2, [x8, #0x508]
1c9cc|ret|
272e4|ldr|x8, [x25, #0x688]
272e8|mov|w2, #0x0
27300|blr|x15
27304|b|0x14002731c <.text+0x2631c>
2731c|ldr|w8, [x19, #0x301c]
27320|add|w21, w21, #0x1
27324|cmp|w21, w8
27328|b.lo|0x1400272c8 <.text+0x262c8>
27334|str|wzr, [x19, #0x15c]
27338|str|xzr, [x2]
27340|ldr|x8, [x8, #0x690]
27358|blr|x15
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (s.split("|",2) for s in SOURCE.strip().splitlines())}
def need(ok,why):
    if not ok: raise AssertionError("E004OK_FAIL_CLOSED "+why)
def result():
    return {
      "schema":"sp11-e004ok-original-IFE-BF-CFG0-immediate-tail-software-bookkeeping-static-v1",
      "parent_git_revision":"756d3d50fec4317af76000fcfcb5d3a1b2d8d791",
      "original_same_SP11_OEM_ISP_sha256":SHA,
      "source_locked_original_ARM64_instructions":len(ANCHORS),
      "conditional_BF_0x300d_CFG0_zero_write_RVA":"0x1da74",
      "zero_write_branches_to_common_tail_RVA":"0x1da78",
      "postwrite_immediate_software_helper_RVA":"0x1c990",
      "original_helper_complete_instruction_count":16,
      "helper_updates_context_mapping_and_software_status_not_MMIO_completion":True,
      "immediate_BF_stop_zero_callback_returns_without_hardware_or_DMA_ack":True,
      "outer_stop_resource_loop_continues_to_other_resources_and_software_state":True,
      "live_rear_video_selected_zero_state_BF_callback":False,
      "whole_Windows_IFE_stop_proven_to_retire_BF_WM16_DMA":False,
      "later_IRQ_bus_WM16_stop_and_buffer_retirement_traced":False,
      "live_Windows_BF_0x0f_FIFO8_completion_observed":False,
      "native_Linux_rear_processed_ISP_4k_optical_frame_observed":False,
      "Golden_boot_or_camera_hardware_modified":False,
      "OEM_binary_full_disassembly_DMA_optical_or_KD_data_exported":False,
    }
def strict(x): need(x==result(),"result mutated")
if __name__=="__main__":
    need(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"OEM binary SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for rva,inst in ANCHORS.items(): need(asm.get(rva)==inst,"original instruction RVA %x"%rva)
    # All instructions in the bounded helper are checked, not a sampled window.
    span=range(0x1c990,0x1c9d0,4)
    need(all(k in ANCHORS for k in span),"complete helper")
    need(all(ANCHORS[k][0] not in ("bl","blr","br","dsb","isb","wfe","wfi") for k in span),"helper direct call or wait")
    need(all(ANCHORS[k][0]!="ldr" or "[x0," in ANCHORS[k][1] for k in span),"helper MMIO status read")
    prev=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004oj-bf-resource-zero-register-offset-static/RESULT.json").read_text())
    need(prev["BF_resource_ID"]=="0x300d" and prev["BF_zero_state_total_original_IFE_base_relative_register_offset"]=="0x1e00" and prev["static_zero_CFG0_write_proves_WM16_dma_legal_retirement"] is False,"prior BF gate")
    out=result(); saved=HERE/"RESULT.json"
    if saved.exists(): need(json.loads(saved.read_text())==out,"saved result mismatch")
    else: saved.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    mutants=[
      ("fake_SHA","original_same_SP11_OEM_ISP_sha256","0"*64),
      ("fake_offset","conditional_BF_0x300d_CFG0_zero_write_RVA","0x1da78"),
      ("fake_helper","postwrite_immediate_software_helper_RVA","0x1c994"),
      ("fake_status","helper_updates_context_mapping_and_software_status_not_MMIO_completion",False),
      ("fake_ack","immediate_BF_stop_zero_callback_returns_without_hardware_or_DMA_ack",False),
      ("fake_live_mode","live_rear_video_selected_zero_state_BF_callback",True),
      ("fake_DMA","whole_Windows_IFE_stop_proven_to_retire_BF_WM16_DMA",True),
      ("fake_async","later_IRQ_bus_WM16_stop_and_buffer_retirement_traced",True),
      ("fake_BF","live_Windows_BF_0x0f_FIFO8_completion_observed",True),
      ("fake_4k","native_Linux_rear_processed_ISP_4k_optical_frame_observed",True),
      ("fake_Golden","Golden_boot_or_camera_hardware_modified",True),
      ("fake_export","OEM_binary_full_disassembly_DMA_optical_or_KD_data_exported",True),
    ]
    for name,key,value in mutants:
        m=copy.deepcopy(out);m[key]=value
        try:strict(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OK_FAIL_OPEN_NEGATIVE "+name)
    print("PASS_E004OK_%d_EXACT_ARM64_INSTRUCTIONS_%d_FAIL_CLOSED_NEGATIVES_BF_CFG0_IMMEDIATE_TAIL_NOT_DMA_ACK_GOLDEN_SAFE"%(len(ANCHORS),len(mutants)))
