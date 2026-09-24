#!/usr/bin/env python3
"""E004or: original-SP11 IFE register-window resource-selector provenance.

Verifies original ARM64 instructions and original PE jump-table bytes in
memory on SP11. Exports only scalar RVAs/offsets and conservative gates.
No proprietary executable, disassembly, DMA address, KD material or image
data enters project files.
"""
import copy,hashlib,json,re,struct,subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
2236c|ldr|x20, [x23, #0x20]
22370|cmp|w24, #0x4
22374|csel|w24, w24, wzr, lo
22378|csdb|
2237c|str|w24, [x20, #0x120]
22380|ldr|w8, [x27, #0xc]
22384|str|w8, [x20, #0x349c]
22388|bl|0x14002b4b8 <.text+0x2a4b8>
2238c|cmp|w0, #0x22b
22390|b.eq|0x1400223c4 <.text+0x213c4>
22398|cmp|w0, #0x27b
2239c|b.ne|0x14002242c <.text+0x2142c>
223a0|ldr|w2, [x20, #0x120]
223a8|ldr|w8, [x20, #0x349c]
223ac|cmp|w2, w8
223b0|b.ge|0x1400223cc <.text+0x213cc>
223c4|mov|w0, w24
223c8|b|0x140022408 <.text+0x21408>
223cc|cmp|w2, #0x1
223d0|b.ne|0x1400223ec <.text+0x213ec>
223e4|mov|w0, #0x2
223e8|b|0x140022408 <.text+0x21408>
223ec|cmp|w2, #0x2
223f0|b.ne|0x140022418 <.text+0x21418>
22404|mov|w0, #0x3
22408|bl|0x14002b568 <.text+0x2a568>
2240c|mov|w19, #0x0
22410|str|x0, [x20, #0x140]
22440|ldr|x3, [x20, #0x140]
22444|cbnz|x3, 0x140022464 <.text+0x21464>
22464|ldr|w8, [x20, #0x349c]
2246c|cmp|w24, w8
22470|add|x8, x20, #0x6b, lsl #12
22474|cset|w9, hs
22478|str|w9, [x8, #0x678]
2247c|mov|x9, #0xc00
22480|mov|x8, #0x1200
22484|csel|x8, x9, x8, lo
22488|add|x8, x8, x3
2248c|str|x8, [x20, #0x150]
2b568|pacibsp|
2b578|cmp|w0, #0x18
2b57c|b.hi|0x14002b70c <.text+0x2a70c>
2b580|adr|x9, 0x14002b734 <.text+0x2a734>
2b584|ldrsb|x8, [x9, w0, uxtw]
2b588|add|x8, x9, x8, lsl #2
2b58c|br|x8
2b590|adrp|x8, 0x14004a000
2b594|add|x8, x8, #0xee0
2b598|ldr|x8, [x8, #0x50]
2b59c|ldr|x0, [x8]
2b5a0|b|0x14002b728 <.text+0x2a728>
2b5b8|adrp|x8, 0x14004a000
2b5bc|add|x8, x8, #0xee0
2b5c0|ldr|x8, [x8, #0x20]
2b5c4|b|0x14002b59c <.text+0x2a59c>
2b5c8|adrp|x8, 0x14004a000
2b5cc|add|x8, x8, #0xee0
2b5d0|ldr|x8, [x8, #0x20]
2b5d4|b|0x14002b5b0 <.text+0x2a5b0>
2b5b0|ldr|x0, [x8, #0x8]
2b728|ldp|x29, x30, [sp], #0x20
2b72c|autibsp|
2b730|ret|
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
1be80|pacibsp|
1d2b0|pacibsp|
1be94|ldr|x8, [x0, #0x140]
1bea0|mov|x1, #0x24
1bea4|str|w9, [x8, #0x24]
1beb4|mov|x1, #0x28
1bebc|str|w8, [x9, #0x28]
1bec8|ldr|x9, [x0, #0x150]
1bed0|str|w8, [x9, #0x18]
1bedc|str|w8, [x9, #0x8]
1d2d4|ldr|x8, [x0, #0x140]
1d2d8|mov|x1, #0x34
1d2dc|str|w9, [x8, #0x34]
1d2ec|mov|x1, #0x38
1d2f4|str|w8, [x9, #0x38]
1d304|ldr|x9, [x0, #0x150]
1d308|str|w8, [x9, #0x18]
1d314|str|w8, [x9, #0x1c]
1d32c|str|w8, [x9, #0x8]
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (row.split("|",2) for row in SOURCE.strip().splitlines())}
def require(ok,msg):
    if not ok:raise AssertionError("E004OR_FAIL_CLOSED "+msg)
def pe_rva_u8(image, target):
    pe=struct.unpack_from("<I",image,0x3c)[0]
    require(image[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",image,pe+4)[0]==0xaa64,"original PE ARM64")
    sh=pe+24+struct.unpack_from("<H",image,pe+20)[0]
    for i in range(struct.unpack_from("<H",image,pe+6)[0]):
        off=sh+40*i
        size,rva,raw_size,raw=struct.unpack_from("<IIII",image,off+8)
        if rva<=target<rva+raw_size:return image[raw+target-rva]
    raise AssertionError("original RVA not mapped %x"%target)
def selector_branch(image,n):
    b=pe_rva_u8(image,0x2b734+n)
    return 0x2b734+4*(b if b<128 else b-256)
def result():
    return {
      "schema":"sp11-e004or-original-IFE-register-window-selector-source-provenance-static-v1",
      "parent_git_revision":"6a943dc9bd4479d27c0e44faffbeb72df32b204c",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "original_instance_selector_lookup_helper_RVA":"0x2b568",
      "original_instance_selector_0_jump_target_RVA":"0x2b590",
      "original_instance_selector_2_jump_target_RVA":"0x2b5b8",
      "original_instance_selector_3_jump_target_RVA":"0x2b5c8",
      "selector_zero_reads_global_table_plus_0x50_first_pointer":True,
      "selector_two_reads_global_table_plus_0x20_first_pointer":True,
      "selector_three_reads_global_table_plus_0x20_second_pointer":True,
      "source_global_table_original_RVA":"0x4aee0",
      "IFE_context_original_base_field_offset":"0x140",
      "IFE_context_instance_index_field_offset":"0x120",
      "IFE_context_threshold_field_offset":"0x349c",
      "IFE_context_mode_state_field_offset":"0x6b678",
      "IFE_context_selected_window_field_offset":"0x150",
      "zero_state_selected_window_base_delta":"0xc00",
      "nonzero_state_selected_window_base_delta":"0x1200",
      "zero_state_finalizer_selected_window_effective_offsets":["0xc18","0xc1c","0xc08"],
      "nonzero_state_finalizer_selected_window_effective_offsets":["0x1218","0x1208"],
      "same_session_live_rear4k_selected_global_base_selector_mode_known":False,
      "global_resource_pointer_proven_physically_mapped_VFE1_for_live_rear4k":False,
      "finalizer_offsets_proven_equivalent_to_WM16_DMA_irq_retirement":False,
      "live_Windows_rear_BF_0x0f_FIFO8_completion_observed":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_frame_proven":False,
      "protected_Golden_boot_or_camera_hardware_modified":False,
      "private_OEM_binary_bulk_disassembly_DMA_optical_or_KD_exported":False,
    }
def strict(x):require(x==result(),"schema/claim altered")
if __name__=="__main__":
    image=ISP.read_bytes()
    require(hashlib.sha256(image).hexdigest()==SHA,"original same-SP11 ISP SHA")
    txt=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    instructions={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(txt)}
    for rva,inst in ANCHORS.items():
        require(instructions.get(rva)==inst,"exact original ARM64 RVA %x"%rva)
    for selector,expected in ((0,0x2b590),(2,0x2b5b8),(3,0x2b5c8)):
        require(selector_branch(image,selector)==expected,"source checked original jump-table selector %d"%selector)
    previous=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004oq-ife-mode-selected-finalizer-register-writes-static/RESULT.json").read_text())
    require(previous["zero_state_selected_finalizer_entry_RVA"]=="0x1d2b0" and
            previous["nonzero_state_selected_finalizer_entry_RVA"]=="0x1be80" and
            previous["per_mode_hardware_bus_stop_IRQ_ack_and_DMA_retirement_proven"] is False,
            "E004oq original finalizer conservative gate")
    require(0xc00+0x18==0xc18 and 0xc00+0x1c==0xc1c and 0xc00+0x8==0xc08 and
            0x1200+0x18==0x1218 and 0x1200+0x8==0x1208,"selected window arithmetic")
    facts=result();saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==facts,"saved derived result mismatch")
    else:saved.write_text(json.dumps(facts,indent=2,sort_keys=True)+"\n")
    mutants=(
        ("fake_sha","same_SP11_original_OEM_ISP_sha256","0"*64),
        ("fake_select2","original_instance_selector_2_jump_target_RVA","0x2b590"),
        ("fake_select3","original_instance_selector_3_jump_target_RVA","0x2b5b8"),
        ("fake_table","source_global_table_original_RVA","0x4aee8"),
        ("fake_base","IFE_context_original_base_field_offset","0x150"),
        ("fake_window","IFE_context_selected_window_field_offset","0x140"),
        ("fake_zero","zero_state_selected_window_base_delta","0x1200"),
        ("fake_nonzero","nonzero_state_selected_window_base_delta","0xc00"),
        ("fake_math","zero_state_finalizer_selected_window_effective_offsets",["0x1218","0x121c","0x1208"]),
        ("fake_phys","global_resource_pointer_proven_physically_mapped_VFE1_for_live_rear4k",True),
        ("fake_live","same_session_live_rear4k_selected_global_base_selector_mode_known",True),
        ("fake_DMA","finalizer_offsets_proven_equivalent_to_WM16_DMA_irq_retirement",True),
        ("fake_BF","live_Windows_rear_BF_0x0f_FIFO8_completion_observed",True),
        ("fake_linux","native_Linux_rear_processed_hardware_ISP_4k_optical_frame_proven",True),
        ("fake_golden","protected_Golden_boot_or_camera_hardware_modified",True),
        ("fake_private","private_OEM_binary_bulk_disassembly_DMA_optical_or_KD_exported",True),
    )
    for name,key,v in mutants:
        m=copy.deepcopy(facts);m[key]=v
        try:strict(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OR_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OR_%d_EXACT_ORIGINAL_ARM64_INSTRUCTIONS_3_ORIGINAL_PE_BRANCHES_%d_NEGATIVES_REGISTER_WINDOW_SOFTWARE_PROVENANCE_NOT_PHYSICAL_DMA_PROOF_GOLDEN_SAFE"%(len(ANCHORS),len(mutants)))
