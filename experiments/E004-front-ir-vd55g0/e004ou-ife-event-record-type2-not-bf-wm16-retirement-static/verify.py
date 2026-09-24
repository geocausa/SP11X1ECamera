#!/usr/bin/env python3
"""E004ou: original mode-zero IFE type-2 event vs BF FIFO8/WM16 branch.

Static read-only same-SP11 OEM original source. No private OEM binary,
bulk original disassembly, physical/DMA addresses, images or KD exported.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
1efd8|cmp|w8, #0x1
1efe4|b.ne|0x14001fecc <.text+0x1eecc>
1efe8|ldr|x23, [x20, #0x8]
1eff0|ldp|w8, w2, [x23, #0x4]
1f048|ubfx|w15, w2, #7, #1
1f188|cbz|w15, 0x14001f19c <.text+0x1e19c>
1f190|mov|w15, #0xf
1f194|str|w15, [x7, w1, uxtw #2]
1fc60|cmp|w8, #0xf
1fc64|b.ne|0x14001fd48 <.text+0x1ed48>
1fc8c|mov|w1, #0x8
1fc90|mov|x0, x19
1fc94|bl|0x140026460 <.text+0x25460>
1fc9c|cbz|x23, 0x14001fe48 <.text+0x1ee48>
1fca4|mov|w2, #0xf
1fcac|ldr|x8, [x8, #0x6c0]
1fcc4|blr|x15
1d710|ldr|x8, [x0, #0x150]
1d714|ldr|w8, [x8, #0x1270]
1d718|str|w8, [x1, #0x4c]
1d71c|ldr|x8, [x0, #0x150]
1d720|ldr|w8, [x8, #0x1200]
1d724|and|w8, w8, #0x1
1d728|strb|w8, [x1, #0x48]
1fecc|cmp|w8, #0x2
1fed0|b.ne|0x14001ff70 <.text+0x1ef70>
1fed4|ldr|x21, [x20, #0x8]
1fed8|ldr|w8, [x21, #0xc]
1fedc|tst|w8, #0xc0000000
1fee8|b.eq|0x14001ff10 <.text+0x1ef10>
1feec|ldr|x8, [x19, #0x150]
1fef0|add|x0, x26, #0x800
1fef4|ldr|w3, [x8, #0x64]
1fef8|ldr|x8, [x19, #0x150]
1fefc|ldr|w4, [x8, #0x70]
1ff00|adrp|x8, 0x140037000 <.text+0x36000>
1ff04|add|x1, x8, #0xce8
1ff08|ldr|w2, [x19, #0x120]
1ff0c|bl|0x140029ad8 <.text+0x28ad8>
1ff10|mov|w8, #-0x1
1ff14|ldaxr|w9, [x21]
1ff18|add|w9, w9, w8
1ff1c|stlxr|w17, w9, [x21]
1ff20|cbnz|w17, 0x14001ff14 <.text+0x1ef14>
1ff24|dmb|ish
1ff28|cbnz|w9, 0x14001ff70 <.text+0x1ef70>
1ff2c|ldr|x8, [x20, #0x8]
1ff30|movi|v16.16b, #0x0
1ff34|add|x1, x20, #0x8
1ff38|str|q16, [x8]
1ff3c|str|s16, [x8, #0x10]
1ff40|ldr|x0, [x19, #0x33c8]
1ff44|bl|0x14002bef8 <.text+0x2aef8>
1ff48|cbz|w0, 0x14001ff70 <.text+0x1ef70>
1ff4c|adrp|x8, 0x140037000 <.text+0x36000>
1ff50|add|x1, x8, #0xd48
1ff54|add|x0, x26, #0x4e8
1ff58|b|0x14001ff6c <.text+0x1ef6c>
1ff70|add|sp, sp, #0xe0
2bef8|pacibsp|
2bf0c|mov|x19, x0
2bf10|mov|x21, x1
2bf14|mov|w20, #0xe
2bf18|cbz|x19, 0x14002bfb8 <.text+0x2afb8>
2bf1c|cbz|x21, 0x14002bfb8 <.text+0x2afb8>
2bf20|adrp|x8, 0x14003f000
2bf24|ldr|x8, [x8, #0x270]
2bf28|add|x0, x19, #0x20
2bf2c|blr|x8
2bf30|strb|w0, [x19, #0x28]
2bf34|ldr|w9, [x19, #0x18]
2bf38|ldr|w8, [x19, #0x10]
2bf3c|cmp|w9, w8
2bf40|b.hs|0x14002bfa0 <.text+0x2afa0>
2247c|mov|x9, #0xc00
22480|mov|x8, #0x1200
22484|csel|x8, x9, x8, lo
22488|add|x8, x8, x3
2248c|str|x8, [x20, #0x150]
"""
ANCHORS={int(r,16):(op,rest) for r,op,rest in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def need(ok,why):
    if not ok:raise AssertionError("E004OU_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004ou-original-IFE-mode0-event-record-type2-software-counter-not-BF-WM16-DMA-ack-static-v1",
      "parent_git_revision":"6d52523d13d09a86acce1a77d72ccfc2a1b9c7d7",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "original_IFE_mode_zero_dispatcher_entry_RVA":"0x1ef90",
      "type_one_branch_comparison_RVA":"0x1efd8",
      "type_two_branch_comparison_RVA":"0x1fecc",
      "type_two_record_ptr_loaded_RVA":"0x1fed4",
      "type_two_record_status_flags_offset":"0xc",
      "type_two_conditional_diagnostic_flags_mask":"0xc0000000",
      "type_two_conditional_diagnostic_original_selected_window_offsets":["0x64","0x70"],
      "type_two_conditional_diagnostic_mode_zero_original_base_offsets":["0xc64","0xc70"],
      "type_two_atomic_software_outstanding_counter_decrement_RVA":"0x1ff14",
      "type_two_software_zero_counter_branch_RVA":"0x1ff28",
      "type_two_record_clear_RVAs":["0x1ff38","0x1ff3c"],
      "type_two_optional_followup_software_queue_helper_RVA":"0x2bef8",
      "type_one_second_status_word_bit_seven_extract_RVA":"0x1f048",
      "type_one_BF_event_id":"0x0f",
      "type_one_BF_FIFO_group_index":8,
      "type_one_BF_original_selected_window_WM16_offsets":["0x1200","0x1270"],
      "type_one_BF_mode_zero_original_base_WM16_offsets":["0x1e00","0x1e70"],
      "type_two_diagnostic_registers_are_BF_WM16_CFG0_and_ADDR_STATUS0":False,
      "type_two_software_counter_zero_proves_BF_FIFO8_issued_or_WM16_IRQ_DMA_retired":False,
      "original_live_rear4k_selected_type_two_vs_type_one_and_BF_event_0x0f_observed":False,
      "original_IFE_hardware_IRQ_ack_and_per_WM_DMA_retirement_gate_fully_traced":False,
      "native_Linux_rear_hardware_ISP_processed_4k_optical_proven":False,
      "protected_Golden_boot_or_camera_hardware_modified":False,
      "private_OEM_binary_bulk_disassembly_physical_DMA_KD_optical_exported":False,
    }
def strict(x):need(x==facts(),"saved/source evidence or false DMA claim altered")
if __name__=="__main__":
    need(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original same-SP11 OEM ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    seen={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for a,want in ANCHORS.items():need(seen.get(a)==want,"original ISA RVA %x"%a)
    prev=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ot-original-ife-resource-name-four-selector-static/RESULT.json").read_text())
    need(prev["actual_live_rear4k_callback_dispatch_mode_and_BF_event_0x0f_proven"] is False and
         prev["BF_WM16_bus_IRQ_DMA_retirement_proven"] is False,"prior E004ot live uncertainty")
    need(0xc00+0x64==0xc64 and 0xc00+0x70==0xc70 and
         0xc00+0x1200==0x1e00 and 0xc00+0x1270==0x1e70,
         "mode-zero original register window arithmetic")
    j=facts();p=HERE/"RESULT.json"
    if p.exists():need(json.loads(p.read_text())==j,"saved scalar result altered")
    else:p.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    mutants=(
      ("wrong_SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("wrong_type","type_two_branch_comparison_RVA","0x1efd8"),
      ("wrong_flags","type_two_record_status_flags_offset","0x8"),
      ("wrong_read","type_two_conditional_diagnostic_original_selected_window_offsets",["0x1200","0x1270"]),
      ("wrong_math","type_two_conditional_diagnostic_mode_zero_original_base_offsets",["0x1e00","0x1e70"]),
      ("wrong_atomic","type_two_atomic_software_outstanding_counter_decrement_RVA","0x1ff10"),
      ("wrong_zero","type_two_software_zero_counter_branch_RVA","0x1ff20"),
      ("wrong_queue","type_two_optional_followup_software_queue_helper_RVA","0x26460"),
      ("wrong_BF","type_one_BF_FIFO_group_index",0),
      ("fake_same_registers","type_two_diagnostic_registers_are_BF_WM16_CFG0_and_ADDR_STATUS0",True),
      ("fake_dma","type_two_software_counter_zero_proves_BF_FIFO8_issued_or_WM16_IRQ_DMA_retired",True),
      ("fake_live","original_live_rear4k_selected_type_two_vs_type_one_and_BF_event_0x0f_observed",True),
      ("fake_all","original_IFE_hardware_IRQ_ack_and_per_WM_DMA_retirement_gate_fully_traced",True),
      ("fake_linux","native_Linux_rear_hardware_ISP_processed_4k_optical_proven",True),
      ("fake_golden","protected_Golden_boot_or_camera_hardware_modified",True),
      ("fake_private","private_OEM_binary_bulk_disassembly_physical_DMA_KD_optical_exported",True),
    )
    for name,k,v in mutants:
        fake=copy.deepcopy(j);fake[k]=v
        try:strict(fake)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OU_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OU_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_IFE_TYPE2_COUNTER_IS_NOT_BF_WM16_DMA_RETIREMENT_GOLDEN_SAFE"%(len(ANCHORS),len(mutants)))
