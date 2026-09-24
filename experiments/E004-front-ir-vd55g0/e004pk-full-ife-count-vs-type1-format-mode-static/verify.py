#!/usr/bin/env python3
"""E004pk SHA-pinned source-only original ISP IFE class vs type1 source-format.

Two independent selectors. Matching on two hypothetical original resources
does not establish real live BF event, exact WM16 per-frame DMA or rear arm.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
B=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
2fb4|adrp|x8, 0x14002f000 <.text+0x2e000>
2fb8|add|x1, x8, #0xe28
31ac|adrp|x8, 0x14002f000 <.text+0x2e000>
31b0|add|x1, x8, #0xfe8
31b4|add|x0, x19, #0x24
31b8|bl|0x14002dae8 <.text+0x2cae8>
31bc|cbnz|w0, 0x1400031e4 <.text+0x21e4>
31d8|ldr|x8, [x20, #0x810]
31dc|str|x0, [x8]
31e4|adrp|x8, 0x140030000 <.text+0x2f000>
31e8|add|x1, x8, #0x10
31ec|add|x0, x19, #0x24
31f0|bl|0x14002dae8 <.text+0x2cae8>
31f4|cbnz|w0, 0x14000323c <.text+0x223c>
3210|ldr|x8, [x20, #0x810]
3214|str|x0, [x8, #0x8]
3234|add|w22, w22, #0x1
3370|adrp|x8, 0x140067000
3374|add|x9, x8, #0xf0
3378|str|w22, [x9]
337c|strh|w22, [x9, #0x8]
3380|str|w22, [x9, #0xc]
3384|str|w23, [x9, #0x4]
222dc|add|x27, x8, #0xf0
222e0|ldp|w8, w9, [x27]
2237c|str|w24, [x20, #0x120]
22380|ldr|w8, [x27, #0xc]
22384|str|w8, [x20, #0x349c]
22464|ldr|w8, [x20, #0x349c]
2246c|cmp|w24, w8
22474|cset|w9, hs
22478|str|w9, [x8, #0x678]
19fa8|add|x8, x19, #0x6b, lsl #12
19fac|ldr|w8, [x8, #0x678]
19fb0|cmp|w8, #0x0
1a0e8|adrp|x8, 0x14001c000 <.text+0x1b000>
1a0ec|add|x9, x8, #0x9d0
1a0f0|adrp|x8, 0x14001e000 <.text+0x1d000>
1a0f4|add|x8, x8, #0xf90
1a0f8|csel|x9, x9, x8, ne
1a100|str|x9, [x8, #0x6d8]
16748|ldr|w8, [x23, #0x8c]
16758|ldr|w8, [x23, #0x8c]
1675c|tst|w8, #0x2
16760|ldr|x8, [sp, #0x38]
16764|cset|w9, ne
16768|str|w9, [x8, #0xe28]
17d94|ldr|x11, [sp, #0x8]
17d98|ldr|w11, [x11, #0xe28]
17d9c|cmp|w11, #0x0
17de8|add|x12, x11, #0xb50
17dec|adrp|x11, 0x14001b000 <.text+0x1a000>
17df0|add|x11, x11, #0x5f0
17df4|csel|x11, x12, x11, ne
17df8|stp|x13, x11, [x8, #0x1f8]
17e44|adrp|x11, 0x140020000 <.text+0x1f000>
17e48|add|x12, x11, #0xce0
17e4c|adrp|x11, 0x14001b000 <.text+0x1a000>
17e50|add|x11, x11, #0x7d0
17e54|csel|x11, x12, x11, ne
17e58|str|x11, [x8, #0x208]
1b678|ldr|x8, [x19, #0x8]
1b67c|ldr|w8, [x8, #0x8c]
1b680|and|w8, w8, #0x7ffffff
1b684|str|w8, [x20, #0xc]
20c00|ldr|x8, [x19, #0x8]
20c04|ldr|w8, [x8, #0x8c]
20c10|and|w7, w8, #0x1f
20c1c|str|w7, [x20, #0xc]
1f048|ubfx|w15, w2, #7, #1
1f190|mov|w15, #0xf
"""
ANCHORS={int(a,16):(op,args) for a,op,args in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def need(ok,why):
    if not ok:raise AssertionError("E004PK_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004pk-original-full-IFE-resource-count-vs-independent-type1-source-format-static-v1",
      "parent_git_revision":"10a3864d3a22f8f9ae7b4056d3787e45d0473561",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "original_full_IFE_resource_names":["IFE0","IFE1"],
      "original_full_IFE0_resource_match_RVA":"0x31b8",
      "original_full_IFE1_resource_match_RVA":"0x31f0",
      "original_full_IFE_resource_discovery_counter_increment_RVA":"0x3234",
      "original_full_IFE_resource_count_global_offset":"0x670fc",
      "original_full_IFE_resource_count_global_store_RVA":"0x3380",
      "original_IFE_worker_instance_index_context_offset":"0x120",
      "original_IFE_worker_full_resource_threshold_context_offset":"0x349c",
      "original_IFE_worker_full_resource_threshold_from_global_RVA":"0x22380",
      "original_IFE_worker_class_selector_RVA":"0x22474",
      "original_IFE_worker_class_flag_context_offset":"0x6b678",
      "original_IFE_worker_modezero_selected_handler_RVA":"0x1ef90",
      "original_IFE_worker_modenonzero_selected_handler_RVA":"0x1c9d0",
      "original_IFE1_worker_modezero_if_both_IFE0_IFE1_discovered_static_proven":True,
      "original_live_rear4k_full_IFE0_IFE1_resource_discovery_count_actually_observed":False,
      "original_live_rear4k_selected_IFE1_worker_BF_modezero_dynamically_observed":False,
      "original_type1_source_format_origin_config_word_offset":"0x8c",
      "original_type1_source_format_flag_input_config_offset":"0xe28",
      "original_type1_source_format_flag_from_config_word_bit_position":1,
      "original_type1_source_format_flag_store_RVA":"0x16768",
      "original_type1_source_format_select_preparer_normalizer_RVA":"0x17d98",
      "original_type1_configzero_preparer_RVA":"0x1b5f0",
      "original_type1_configzero_normalizer_RVA":"0x1b7d0",
      "original_type1_confignonzero_preparer_RVA":"0x20b50",
      "original_type1_confignonzero_normalizer_RVA":"0x20ce0",
      "original_type1_nonzero_prep_masks_CSID_BUF_DONE_bit7":True,
      "original_type1_source_format_equals_IFE_worker_resource_class_selector_source_proven":False,
      "original_live_rear4k_input_config_word0x8c_bit1_observed":False,
      "original_live_rear4k_configzero_prep_normalizer_and_BF_event0x0f_observed":False,
      "original_CSID1_BUF_DONE_bit7_physically_set_and_unmasked_in_two_rear4k_snapshots":True,
      "original_rear4k_BF_event0x0f_FIFO8_per_WM16_frame_completion_proven":False,
      "native_rear_WM16_CSIDs_or_VFE_irq_generation_DMA_IOMMU_safe_retirement_proven":False,
      "native_rear_hardware_ISP_4k_optical_proven":False,
      "rear_hardware_ISP_runtime_authorized":False,
      "Golden_boot_kernel_camera_hardware_modified":False,
      "OEM_private_binary_bulk_ISA_KD_physical_DMA_optical_exported":False,
    }
def strict(x):need(x==facts(),"source-derived result or safety gate changed")
if __name__=="__main__":
    need(hashlib.sha256(B.read_bytes()).hexdigest()==SHA,"same-SP11 original OEM ISP SHA")
    d=subprocess.check_output(["llvm-objdump","-d",str(B)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(d)}
    for at,expected in ANCHORS.items():need(ins.get(at)==expected,"original ISA RVA %x"%at)
    original=B.read_bytes()
    for rva,label in ((0x2ffe8,b"IFE0"),(0x30010,b"IFE1")):
        need(original[rva-0xc00:rva-0xc00+len(label)+1]==label+b"\0",
             "original OEM full IFE resource name %x"%rva)
    ph=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ph-original-type1-preparation-queue-status-provenance-static/RESULT.json").read_text())
    pi=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pi-original-live-rear-csid-bf-bit7-wm16-fence-offline/RESULT.json").read_text())
    pj=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pj-csid-bf-statistics-completion-bridge-offline/RESULT.json").read_text())
    need(ph["original_type_one_B_modenonzero_prepared_status_word_bit7_cannot_survive_0x1f_mask"] is True and
         ph["original_status_format_selector_equal_actual_live_rear4k_IFE_branch_proven"] is False,
         "original type1 bit1 source-format independent from worker mode")
    need(pi["same_original_rear4k_two_live_physical_CSID1_BUF_DONE_bit7_set_and_unmasked"] is True and
         pi["original_live_rear4k_selected_BF_handler_and_event0x0f_observed"] is False,
         "two existing original rear4k snapshots not a BF event trace")
    need(pj["accepted_native_generic_vfe_buf_done_has_per_frame_six_stats_group8_FIFO_WM16_owner_fence"] is False and
         pj["rear_Linux_hardware_ISP_runtime_authorized"] is False,
         "generic Linux RDI/PIX not rear BF stats DMA retire")
    def selected(instance,count,input_config8c,csid_status8c):
        worker_zero = instance < count
        type1_zero = not bool(input_config8c & 2)
        source_word = csid_status8c & (0x7ffffff if type1_zero else 0x1f)
        return worker_zero,type1_zero,bool(worker_zero and type1_zero and source_word & 0x80)
    need(selected(1,2,0,0x2f1)==(True,True,True) and
         selected(1,2,2,0x2f1)==(True,False,False) and
         selected(1,1,0,0x2f1)==(False,True,False) and
         selected(1,2,0,0x271)==(True,True,False) and
         selected(0,0,0,0x2f1)==(False,True,False) and
         selected(1,2,2,0xff)==(True,False,False),
         "independent IFE count and input-config bit1 source-format not interchangeable")
    v=facts();out=HERE/"RESULT.json"
    if out.exists():need(json.loads(out.read_text())==v,"saved locked safe scalar evidence")
    else:out.write_text(json.dumps(v,sort_keys=True,indent=2)+"\n")
    mutations=(
      ("sha","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("resources","original_full_IFE_resource_names",["IFE1"]),
      ("count","original_full_IFE_resource_count_global_offset","0x670f4"),
      ("countstore","original_full_IFE_resource_count_global_store_RVA","0x3384"),
      ("workerindex","original_IFE_worker_instance_index_context_offset","0x2c"),
      ("workerthresh","original_IFE_worker_full_resource_threshold_context_offset","0x120"),
      ("workerclass","original_IFE_worker_class_selector_RVA","0x2246c"),
      ("workerflag","original_IFE_worker_class_flag_context_offset","0xe28"),
      ("BFmode","original_IFE_worker_modezero_selected_handler_RVA","0x1c9d0"),
      ("nonzero","original_IFE_worker_modenonzero_selected_handler_RVA","0x1ef90"),
      ("fake_livecount","original_live_rear4k_full_IFE0_IFE1_resource_discovery_count_actually_observed",True),
      ("fake_liveBFmode","original_live_rear4k_selected_IFE1_worker_BF_modezero_dynamically_observed",True),
      ("configword","original_type1_source_format_origin_config_word_offset","0x120"),
      ("configflag","original_type1_source_format_flag_input_config_offset","0x6b678"),
      ("bit1","original_type1_source_format_flag_from_config_word_bit_position",0),
      ("store","original_type1_source_format_flag_store_RVA","0x22478"),
      ("sel","original_type1_source_format_select_preparer_normalizer_RVA","0x19fac"),
      ("prep0","original_type1_configzero_preparer_RVA","0x20b50"),
      ("prepn","original_type1_confignonzero_preparer_RVA","0x1b5f0"),
      ("norm0","original_type1_configzero_normalizer_RVA","0x20ce0"),
      ("normn","original_type1_confignonzero_normalizer_RVA","0x1b7d0"),
      ("fake_equal","original_type1_source_format_equals_IFE_worker_resource_class_selector_source_proven",True),
      ("fake_liveconfig","original_live_rear4k_input_config_word0x8c_bit1_observed",True),
      ("fake_liveevent","original_live_rear4k_configzero_prep_normalizer_and_BF_event0x0f_observed",True),
      ("fake_mask","original_type1_nonzero_prep_masks_CSID_BUF_DONE_bit7",False),
      ("fake_WM16","original_rear4k_BF_event0x0f_FIFO8_per_WM16_frame_completion_proven",True),
      ("fake_native","native_rear_WM16_CSIDs_or_VFE_irq_generation_DMA_IOMMU_safe_retirement_proven",True),
      ("fake_optical","native_rear_hardware_ISP_4k_optical_proven",True),
      ("fake_arm","rear_hardware_ISP_runtime_authorized",True),
      ("fake_golden","Golden_boot_kernel_camera_hardware_modified",True),
      ("fake_export","OEM_private_binary_bulk_ISA_KD_physical_DMA_optical_exported",True),
    )
    for label,key,value in mutations:
        bad=copy.deepcopy(v);bad[key]=value
        try:strict(bad)
        except AssertionError:continue
        raise AssertionError("E004PK_NEGATIVE_FAILED_OPEN "+label)
    print("PASS_E004PK_%d_ORIGINAL_EXACT_ARM64_ISA_%d_NEGATIVES_FULL_IFE_INSTANCE_THRESHOLD_VS_INDEPENDENT_TYPE1_INPUT_CONFIG_BIT1_ZERO_MODE_CONDITIONAL_NO_LIVE_BF_NO_DMA_GOLDEN_SAFE"%(len(ANCHORS),len(mutations)))
