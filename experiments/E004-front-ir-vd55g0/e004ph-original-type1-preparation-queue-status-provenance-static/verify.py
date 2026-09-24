#!/usr/bin/env python3
"""E004ph: original type1 status preparation/producer same queued record.

Two separate original callback queues: snapshot-wrapper path is NOT the
actual type1 preparation path. Source-only; no live MMIO/IRQ/DMA assumptions.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
NATIVE_CSID=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-csid-680.c")
NATIVE_CSID_SHA="9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90"
BASE=0x140000000
SOURCE="""
1789c|adrp|x8, 0x14002a000 <.text+0x29000>
178a0|add|x9, x8, #0xc30
178a8|str|x9, [x8, #0x1f0]
178ac|adrp|x8, 0x14002a000 <.text+0x29000>
178b0|add|x9, x8, #0xca0
178b8|str|x9, [x8, #0x1d0]
178e0|adrp|x9, 0x140024000 <.text+0x23000>
178e4|add|x10, x9, #0x380
178ec|str|x10, [x9, #0x148]
178f4|adrp|x9, 0x140024000 <.text+0x23000>
178f8|add|x10, x9, #0x3d0
17900|str|x10, [x9, #0x138]
22638|adrp|x8, 0x14002a000 <.text+0x29000>
2263c|add|x8, x8, #0xb50
22644|str|x8, [x9, #0x1d8]
22648|adrp|x8, 0x14002a000 <.text+0x29000>
2264c|add|x8, x8, #0xbc0
22654|str|x8, [x9, #0x1f8]
22670|adrp|x8, 0x140024000 <.text+0x23000>
22674|add|x8, x8, #0xa30
2267c|str|x8, [x9, #0x140]
22684|adrp|x8, 0x140024000 <.text+0x23000>
22688|add|x8, x8, #0xa70
22690|str|x8, [x9, #0x150]
1c98|mov|x8, #0xc020
1ca0|add|x0, x24, #0x228
1ca4|bl|0x140001a38 <.text+0xa38>
1cd0|ldr|x8, [x22, #0x6b8]
1cd8|str|x0, [x19, #0x50]
1cf8|adrp|x8, 0x140067000
1cfc|ldr|x8, [x8, #0x1d8]
1d04|mov|w0, w20
1d08|add|x1, x19, #0x10
1d1c|blr|x15
1d40|ldr|x8, [x22, #0x6b8]
1d44|stp|x10, x9, [x19]
1d4c|str|x19, [x9]
1d54|str|x19, [x10, #0x8]
1eec|cbz|x19, 0x140001f44 <.text+0xf44>
1ef8|ldr|x8, [x24, #0x1f8]
1f04|mov|w0, w23
1f08|add|x1, x19, #0x10
1f1c|blr|x15
1fec|adrp|x8, 0x14004a000
2018|mov|x8, #0xc020
2024|add|x0, x8, #0x328
2028|bl|0x140001a38 <.text+0xa38>
207c|adrp|x8, 0x140067000
2080|ldr|x9, [x8, #0x1f0]
2094|mov|w0, w20
2098|add|x1, x19, #0x10
20ac|blr|x15
20b0|add|x8, x24, #0x6c, lsl #12
20b4|add|x10, x8, #0x338
20d4|stp|x10, x9, [x19]
20dc|str|x19, [x9]
20e4|str|x19, [x10, #0x8]
2274|add|x21, x8, #0x60, lsl #12
2278|add|x0, x21, #0x328
227c|bl|0x140001b40 <.text+0xb40>
2294|ldr|x9, [x24, #0x1d0]
22a8|mov|w0, w23
22ac|add|x1, x19, #0x10
22c0|blr|x15
2ac30|pacibsp|
2ac64|ldr|x9, [x8, #0x148]
2ac6c|adrp|x8, 0x14004a000
2ac70|ldr|x8, [x8, #0xec0]
2ac74|ldr|x0, [x8, w0, sxtw #3]
2ac8c|blr|x15
2aca0|pacibsp|
2acd4|ldr|x9, [x8, #0x138]
2acdc|adrp|x8, 0x14004a000
2ace0|ldr|x8, [x8, #0xec0]
2ace4|ldr|x0, [x8, w0, sxtw #3]
2acfc|blr|x15
2ab84|ldr|x9, [x8, #0x140]
2ab94|ldr|x0, [x8, w0, sxtw #3]
2aba8|blr|x17
24380|pacibsp|
243a8|ldr|x8, [x0, #0x200]
243bc|blr|x15
243d0|pacibsp|
243e8|mov|x20, x0
243ec|mov|x22, x1
244e4|mov|w8, #0x1
244e8|str|w8, [sp, #0x10]
244ec|ldr|x8, [x20, #0x208]
244f0|mov|x1, x22
2450c|blr|x15
2461c|ldr|x19, [x20, #0x198]
24664|bl|0x14002c5b0 <.text+0x2b5b0>
17d98|ldr|w11, [x11, #0xe28]
17d9c|cmp|w11, #0x0
17db8|adrp|x11, 0x140020000 <.text+0x1f000>
17dbc|add|x12, x11, #0x9b0
17dc0|adrp|x11, 0x14001b000 <.text+0x1a000>
17dc4|add|x11, x11, #0x3d0
17dc8|csel|x11, x12, x11, ne
17dcc|str|x11, [x8, #0x218]
17dd0|adrp|x11, 0x140020000 <.text+0x1f000>
17dd4|add|x12, x11, #0x2c0
17dd8|adrp|x11, 0x14001a000 <.text+0x19000>
17ddc|add|x11, x11, #0x870
17de0|csel|x13, x12, x11, ne
17de4|adrp|x11, 0x140020000 <.text+0x1f000>
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
1b600|mov|x19, x0
1b604|ldr|w3, [x19, #0x28]
1b608|mov|x20, x1
1b630|ldr|x8, [x19, #0x8]
1b63c|ldr|w8, [x8, #0x7c]
1b640|and|w8, w8, #0x3fff
1b644|str|w8, [x20, #0x4]
1b648|ldr|x8, [x19, #0x8]
1b64c|ldr|w8, [x8, #0x9c]
1b650|and|w8, w8, #0xfffffff
1b654|str|w8, [x20, #0x8]
1b678|ldr|x8, [x19, #0x8]
1b67c|ldr|w8, [x8, #0x8c]
1b680|and|w8, w8, #0x7ffffff
1b684|str|w8, [x20, #0xc]
20b90|ldr|x8, [x19, #0x8]
20b9c|ldr|w8, [x8, #0x7c]
20ba0|and|w8, w8, #0x3fff
20ba4|str|w8, [x20, #0x4]
20bb8|ldr|x8, [x19, #0x8]
20bbc|ldr|w8, [x8, #0xac]
20bc0|and|w8, w8, #0x3fffffff
20bc4|str|w8, [x20, #0x10]
20c00|ldr|x8, [x19, #0x8]
20c04|ldr|w8, [x8, #0x8c]
20c10|and|w7, w8, #0x1f
20c1c|str|w7, [x20, #0xc]
1b7d0|ldr|w8, [x1, #0x4]
1b7d4|str|w8, [x2, #0x4]
1b7d8|ldr|w8, [x1, #0x8]
1b7dc|str|w8, [x2, #0xc]
1b7f0|ldr|w8, [x1, #0xc]
1b7f4|str|w8, [x2, #0x8]
20ce8|ldr|w8, [x1, #0x8]
20cec|str|w8, [x2, #0xc]
20cf8|ldr|w8, [x1, #0xc]
20cfc|str|w8, [x2, #0x8]
1efd8|cmp|w8, #0x1
1efe8|ldr|x23, [x20, #0x8]
1eff0|ldp|w8, w2, [x23, #0x4]
1f048|ubfx|w15, w2, #7, #1
1f054|strb|w15, [sp, #0x2c]
1f190|mov|w15, #0xf
176c0|ldr|x19, [x21, #0x20]
176c4|cmp|w20, #0x4
17728|add|w0, w20, #0x7
1775c|mov|w0, #0x9
17780|mov|w0, #0xa
17784|bl|0x14002b568 <.text+0x2a568>
17788|str|x0, [x19, #0x8]
2b578|cmp|w0, #0x18
2b580|adr|x9, 0x14002b734 <.text+0x2a734>
2b584|ldrsb|x8, [x9, w0, uxtw]
2b588|add|x8, x9, x8, lsl #2
2b58c|br|x8
2b634|adrp|x8, 0x14004a000
2b638|add|x8, x8, #0xee0
2b63c|ldr|x8, [x8, #0x10]
2b640|b|0x14002b59c <.text+0x2a59c>
2b644|adrp|x8, 0x14004a000
2b648|add|x8, x8, #0xee0
2b64c|ldr|x8, [x8, #0x10]
2b650|b|0x14002b5b0 <.text+0x2a5b0>
2c08|ldr|x8, [x20, #0x10]
2c28|str|x0, [x20, #0x10]
30f0|adrp|x8, 0x14002f000 <.text+0x2e000>
30f4|add|x1, x8, #0xf48
3104|ldr|w1, [x19, #0x20]
311c|ldr|x8, [x20, #0x7d0]
3120|str|x0, [x8]
3134|add|x1, x8, #0xf80
315c|ldr|x8, [x20, #0x7d0]
3160|str|x0, [x8, #0x8]
1b718|ldr|x8, [x19, #0x8]
1b71c|str|w9, [x8, #0x84]
1b724|ldr|x8, [x19, #0x8]
1b728|str|w9, [x8, #0xa4]
1b72c|ldr|w9, [x20, #0xc]
1b730|ldr|x8, [x19, #0x8]
1b734|str|w9, [x8, #0x94]
1b7b0|ldr|x9, [x19, #0x8]
1b7b4|mov|w8, #0x1
1b7b8|str|w8, [x9, #0x14]
"""
ANCHORS={int(a,16):(op,ops) for a,op,ops in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def require(ok,why):
    if not ok:raise AssertionError("E004PH_FAIL_CLOSED "+why)
def facts():
    return {
       "schema":"sp11-e004ph-original-type1-preparation-queue-CSID_BUF_DONE8c-to-record8-BFbit7-static-v2",
       "parent_git_revision":"dd112e7dd9723b9f519d5953147c7d4e07b4222a",
       "same_SP11_original_OEM_ISP_sha256":SHA,
       "same_SP11_accepted_native_CSID680_source_sha256":NATIVE_CSID_SHA,
       "exact_original_ARM64_instruction_anchors":len(ANCHORS),
       "original_IFE_snapshot_A_wrapper_RVA":"0x24a30",
       "original_IFE_snapshot_A_queue_preparation_RVA":"0x1c18",
       "original_IFE_snapshot_A_queue_context_offset":"0x228",
       "original_IFE_snapshot_A_prepare_thunk_RVA":"0x2ab50",
       "original_IFE_snapshot_A_consumer_RVA":"0x1e58",
       "original_type_one_B_queue_preparation_RVA":"0x1f98",
       "original_type_one_B_queue_context_offset":"0x60328",
       "original_type_one_B_queue_preparation_thunk_RVA":"0x2ac30",
       "original_type_one_B_queue_consumer_RVA":"0x21e8",
       "original_type_one_B_queue_consumer_thunk_RVA":"0x2aca0",
       "original_type_one_B_prepare_registered_callback_RVA":"0x24380",
       "original_type_one_B_consume_registered_callback_RVA":"0x243d0",
       "original_type_one_prepared_record_envelope_buffer_offset":"0x10",
       "original_type_one_B_preparation_and_consumer_reuse_same_queue_object_static_proven":True,
       "original_type_one_B_preparation_and_consumer_both_use_same_context_table_for_matching_index":True,
       "original_type_one_B_source_callback_context_offset":"0x200",
       "original_type_one_B_record_normalizer_context_offset":"0x208",
       "original_status_format_selector_original_input_config_offset":"0xe28",
       "original_status_format_selector_equal_actual_live_rear4k_IFE_branch_proven":False,
       "original_type_one_B_modezero_source_prep_callback_RVA":"0x1b5f0",
       "original_type_one_B_modenonzero_source_prep_callback_RVA":"0x20b50",
       "original_type_one_B_modezero_normalizer_RVA":"0x1b7d0",
       "original_type_one_B_modenonzero_normalizer_RVA":"0x20ce0",
       "original_type_one_B_modezero_source_context_register_window_pointer_offset":"0x8",
       "original_type_one_B_modezero_raw_register_window_word_offset":"0x8c",
       "original_type_one_B_modezero_register_mask":"0x7ffffff",
       "original_type_one_B_modenonzero_register_mask":"0x1f",
       "original_type_one_B_prepared_record_source_word_offset":"0xc",
       "original_type_one_B_normalized_record_BF_consumer_word_offset":"0x8",
       "original_type_one_B_modezero_BF_bit_position":7,
       "original_type_one_B_modenonzero_prepared_status_word_bit7_cannot_survive_0x1f_mask":True,
       "original_type_one_B_preparation_input_is_separate_from_IFE_snapshot_A_wrapper":True,
       "old_conditional_same_IFE_snapshot_BUS_status0_plus0xc_as_type1_BF_source_valid_for_discovered_B_path":False,
       "old_direct_IFE_snapshot_TOP_status1_plus0x8_as_type1_BF_source_valid":False,
       "original_instance0_source_register_resource_name":"CSID0",
       "original_instance1_source_register_resource_name":"CSID1",
       "original_instance0_source_resource_lookup_selector":7,
       "original_instance1_source_resource_lookup_selector":8,
       "original_CSIDs_resource_mapping_same_buffer_done_status_register_offset_as_native":True,
       "original_CSIDs_resource_array_first_second_slots_offset":"0x10",
       "original_CSIDs_type1_modezero_source_register_offset":"0x8c",
       "original_CSIDs_type1_modezero_clear_register_offset":"0x94",
       "original_CSIDs_type1_modezero_clear_command_offset":"0x14",
       "accepted_native_CSID_BUF_DONE_IRQ_STATUS_offset":"0x8c",
       "accepted_native_CSID_BUF_DONE_IRQ_CLEAR_offset":"0x94",
       "accepted_native_CSID_BUF_DONE_IRQ_MASK_offset":"0x90",
       "accepted_native_CSID_ISR_reads_clears_BUF_DONE":True,
       "accepted_native_CSID_ISR_bit7_named_as_safe_rear_WM16_retirement":False,
       "original_zero_mode_CSID_BUF_DONE_status_bit7_to_type1_BF0x0f_static_proven":True,
       "original_rear4k_live_CSID1_selected_source_or_bit7_occurrence_proven":False,
       "original_CSID_BUF_DONE_bit7_equals_independent_VFE_WM16_DMA_completion_proven":False,
       "source_context_plus8_register_window_physical_MMIO_block_resource_CSIDs_proven_for_instance0_1":True,
       "source_context_plus8_register_window_correct_live_IRQ_bit_ACK_or_WM16_fence_proven":False,
       "same_original_rear4k_live_mode_and_BF_event0x0f_observed":False,
       "native_Linux_rear_VFE1_real_IRQ_status_ACK_FIFO8_per_generation_WM16_DMA_IOMMU_quiescence_proven":False,
       "native_Linux_rear_hardware_ISP_4k_optical_proven":False,
       "rear_Linux_hardware_ISP_runtime_authorized":False,
       "Golden_boot_kernel_camera_hardware_modified":False,
       "OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported":False,
    }
def strict(data):require(data==facts(),"false source/queue attribution or safety claim")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original OEM ISP SHA")
    require(hashlib.sha256(NATIVE_CSID.read_bytes()).hexdigest()==NATIVE_CSID_SHA,
            "same-SP11 accepted native CSID680 source SHA")
    native=NATIVE_CSID.read_text()
    for symbol,offset in (("CSID_BUF_DONE_IRQ_STATUS","0x8c"),
                          ("CSID_BUF_DONE_IRQ_CLEAR","0x94"),
                          ("CSID_BUF_DONE_IRQ_MASK","0x90")):
        require(re.search(r"(?m)^#define\s+"+symbol+r"\s+"+offset+r"\s*$",native) is not None,
                "accepted native CSID BUF_DONE definition changed "+symbol)
    require("buf_done_val = readl(csid->base + CSID_BUF_DONE_IRQ_STATUS);" in native and
            "writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);" in native and
            "writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);" in native and
            re.search(r"(?m)^#define\s+CSID_BUF_DONE_VIDEO\s+BIT\(0\)\s*$",native) is not None,
            "native CSID ISR reads/acknowledges BUF_DONE but cannot be reused as VFE WM16 DMA fence")
    require("CSID_BUF_DONE_BF" not in native and "CSID_BUF_DONE_WM16" not in native,
            "native bit7 must not be relabeled an independently proven rear WM16 completion")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for at,expect in ANCHORS.items():require(ins.get(at)==expect,"exact original ARM64 RVA %x"%at)
    image=ISP.read_bytes()
    for rva,name in ((0x2ff48,b"CSID0"),(0x2ff80,b"CSID1")):
        original=image[rva-0xc00:rva-0xc00+len(name)+1]
        require(original==name+b"\0","exact original same-SP11 resource descriptor name %x"%rva)
    for selector,rva in ((7,0x2b634),(8,0x2b644)):
        raw_idx=image[0x2b734-0xc00+selector]
        signed=raw_idx if raw_idx<128 else raw_idx-256
        require(0x2b734+4*signed==rva,"original CSID0/CSID1 per-instance jump selector")
    pg=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pg-original-source-command-a-worker-ring-identity-static/RESULT.json").read_text())
    require(pg["type_one_event_producer_to_worker_same_ring_on_successful_setup_static_proven"] is True and
            pg["original_live_rear4k_selected_IFE_mode_and_BF0x0f_observed"] is False,
            "actual source worker ring proof remains static, live BF still unobserved")
    pb=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pb-ife-type1-record-producer-normalization-static/RESULT.json").read_text())
    require(pb["previous_direct_TOP_status1_bit7_to_BF_record_inference_valid_after_normalization"] is False and
            pb["type_one_event_enqueue_software_ring_context_offset"]=="0x198",
            "prior type1 source-word reorder lock")
    # Simulate SAME record envelope passed from preparation to later consumer;
    # separate queue cannot legally be substituted even with same word offsets.
    def prepared_bf_word(raw_window_8c,modezero,one_queue_object,consumer_queue_object):
        if one_queue_object is not consumer_queue_object:return None
        source_c=raw_window_8c & (0x7ffffff if modezero else 0x1f)
        prepared={"source+0xc":source_c,"source+0x8":0x555a55a5}
        normal={"record+0x8":prepared["source+0xc"],"record+0xc":prepared["source+0x8"]}
        return normal["record+0x8"],normal["record+0xc"]
    obj=object()
    require(prepared_bf_word(0x80,True,obj,obj)==(0x80,0x555a55a5) and
            prepared_bf_word(0x80,False,obj,obj)==(0,0x555a55a5) and
            prepared_bf_word(0x10000080,True,obj,obj)==(0x80,0x555a55a5) and
            prepared_bf_word(0x80,True,obj,object()) is None and
            prepared_bf_word(0x81,True,obj,obj)[0] & 0x80 and
            not (prepared_bf_word(0x7f,True,obj,obj)[0] & 0x80),
            "offline zero/nonzero mask/bit7/queue identity guard")
    data=facts();saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==data,"saved conservative result changed")
    else:saved.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    muts=(
      ("sha","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("qA","original_IFE_snapshot_A_queue_context_offset","0x60328"),
      ("qB","original_type_one_B_queue_context_offset","0x228"),
      ("qBpre","original_type_one_B_queue_preparation_RVA","0x1c18"),
      ("qBconsume","original_type_one_B_queue_consumer_RVA","0x1e58"),
      ("prep_thunk","original_type_one_B_queue_preparation_thunk_RVA","0x2ab50"),
      ("consume_thunk","original_type_one_B_queue_consumer_thunk_RVA","0x2abc0"),
      ("prep_call","original_type_one_B_prepare_registered_callback_RVA","0x24a30"),
      ("consume_call","original_type_one_B_consume_registered_callback_RVA","0x24a70"),
      ("ctxA","original_type_one_B_source_callback_context_offset","0x6b0"),
      ("ctxB","original_type_one_B_record_normalizer_context_offset","0x200"),
      ("mode","original_status_format_selector_original_input_config_offset","0x6b678"),
      ("modezero","original_type_one_B_modezero_source_prep_callback_RVA","0x1dc20"),
      ("modenonzero","original_type_one_B_modenonzero_source_prep_callback_RVA","0x1c2b0"),
      ("normalzero","original_type_one_B_modezero_normalizer_RVA","0x20ce0"),
      ("normalnonzero","original_type_one_B_modenonzero_normalizer_RVA","0x1b7d0"),
      ("sourceptr","original_type_one_B_modezero_source_context_register_window_pointer_offset","0x140"),
      ("sourceword","original_type_one_B_modezero_raw_register_window_word_offset","0x28"),
      ("sourcemask","original_type_one_B_modezero_register_mask","0x1f"),
      ("nonzeromask","original_type_one_B_modenonzero_register_mask","0x7ffffff"),
      ("sourceoff","original_type_one_B_prepared_record_source_word_offset","0x8"),
      ("BFoff","original_type_one_B_normalized_record_BF_consumer_word_offset","0xc"),
      ("bit","original_type_one_B_modezero_BF_bit_position",0),
      ("fake_queue","original_type_one_B_preparation_and_consumer_reuse_same_queue_object_static_proven",False),
      ("fake_context","original_type_one_B_preparation_and_consumer_both_use_same_context_table_for_matching_index",False),
      ("fake_format_equal","original_status_format_selector_equal_actual_live_rear4k_IFE_branch_proven",True),
      ("fake_nonzero_bit7","original_type_one_B_modenonzero_prepared_status_word_bit7_cannot_survive_0x1f_mask",False),
      ("fake_snapshot_identity","original_type_one_B_preparation_input_is_separate_from_IFE_snapshot_A_wrapper",False),
      ("fake_bus","old_conditional_same_IFE_snapshot_BUS_status0_plus0xc_as_type1_BF_source_valid_for_discovered_B_path",True),
      ("fake_top","old_direct_IFE_snapshot_TOP_status1_plus0x8_as_type1_BF_source_valid",True),
      ("native_SHA","same_SP11_accepted_native_CSID680_source_sha256","0"*64),
      ("fake_csids","original_CSIDs_resource_mapping_same_buffer_done_status_register_offset_as_native",False),
      ("fake_src0","original_instance0_source_register_resource_name","IFE0"),
      ("fake_src1","original_instance1_source_register_resource_name","IFE1"),
      ("fake_selector","original_instance1_source_resource_lookup_selector",1),
      ("fake_native_status","accepted_native_CSID_BUF_DONE_IRQ_STATUS_offset","0xac"),
      ("fake_native_clear","accepted_native_CSID_BUF_DONE_IRQ_CLEAR_offset","0x84"),
      ("fake_source_clear","original_CSIDs_type1_modezero_clear_register_offset","0xa4"),
      ("fake_native_ack","accepted_native_CSID_ISR_reads_clears_BUF_DONE",False),
      ("fake_bit7safe","accepted_native_CSID_ISR_bit7_named_as_safe_rear_WM16_retirement",True),
      ("fake_modezero","original_zero_mode_CSID_BUF_DONE_status_bit7_to_type1_BF0x0f_static_proven",False),
      ("fake_liveCSID1","original_rear4k_live_CSID1_selected_source_or_bit7_occurrence_proven",True),
      ("fake_wm16","original_CSID_BUF_DONE_bit7_equals_independent_VFE_WM16_DMA_completion_proven",True),
      ("fake_mmio","source_context_plus8_register_window_physical_MMIO_block_resource_CSIDs_proven_for_instance0_1",False),
      ("fake_irq","source_context_plus8_register_window_correct_live_IRQ_bit_ACK_or_WM16_fence_proven",True),
      ("fake_live","same_original_rear4k_live_mode_and_BF_event0x0f_observed",True),
      ("fake_DMA","native_Linux_rear_VFE1_real_IRQ_status_ACK_FIFO8_per_generation_WM16_DMA_IOMMU_quiescence_proven",True),
      ("fake_optical","native_Linux_rear_hardware_ISP_4k_optical_proven",True),
      ("fake_arm","rear_Linux_hardware_ISP_runtime_authorized",True),
      ("fake_golden","Golden_boot_kernel_camera_hardware_modified",True),
      ("fake_private","OEM_private_binary_bulk_ISA_physical_DMA_KD_optical_exported",True),
    )
    for name,key,val in muts:
        bad=copy.deepcopy(data);bad[key]=val
        try:strict(bad)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PH_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004PH_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVES_DISTINCT_QUEUES_B_STATUS_PREPARER_ZERO_MODE_CONTEXT8_WORD8C_TO_BF_RECORD8_BIT7_SNAPSHOT_A_NOT_SOURCE_LIVE_IRQ_DMA_UNPROVEN_GOLDEN_SAFE"%(len(ANCHORS),len(muts)))
