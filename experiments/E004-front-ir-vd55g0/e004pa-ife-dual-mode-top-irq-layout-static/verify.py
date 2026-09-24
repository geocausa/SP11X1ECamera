#!/usr/bin/env python3
"""E004pa: two exact original IFE status-snapshot callbacks, native TOP map.

Static source only; cannot infer actual live rear VFE mode or DMA ACK.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
VFE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-vfe-680.c")
VFE_SHA="99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208"
SOURCE="""
19fa8|add|x8, x19, #0x6b, lsl #12
19fac|ldr|w8, [x8, #0x678]
19fb0|cmp|w8, #0x0
1a05c|adrp|x8, 0x14001c000 <.text+0x1b000>
1a060|add|x9, x8, #0x2b0
1a064|adrp|x8, 0x14001d000 <.text+0x1c000>
1a068|add|x8, x8, #0xc20
1a06c|csel|x9, x9, x8, ne
1a070|add|x8, x19, #0x6b, lsl #12
1a074|str|x9, [x8, #0x6b0]
1a0e8|adrp|x8, 0x14001c000 <.text+0x1b000>
1a0ec|add|x9, x8, #0x9d0
1a0f0|adrp|x8, 0x14001e000 <.text+0x1d000>
1a0f4|add|x8, x8, #0xf90
1a0f8|csel|x9, x9, x8, ne
1a100|str|x9, [x8, #0x6d8]
24a3c|add|x8, x0, #0x6b, lsl #12
24a40|ldr|x8, [x8, #0x6b0]
24a54|blr|x15
1c2b0|pacibsp|
1c2c4|mov|x19, x0
1c2c8|ldr|x8, [x19, #0x140]
1c2cc|mov|x20, x1
1c2d0|ldr|w8, [x8, #0x1c]
1c2d4|str|w8, [x20, #0x4]
1c2d8|ldr|x8, [x19, #0x140]
1c2dc|ldr|w8, [x8, #0x20]
1c2e0|str|w8, [x20, #0x8]
1c2e4|ldr|x8, [x19, #0x150]
1c2e8|ldr|w8, [x8, #0x28]
1c2ec|str|w8, [x20, #0xc]
1c328|ldr|w2, [x20, #0x4]
1c32c|mov|x1, #0x2c
1c338|str|w2, [x8, #0x2c]
1c340|ldr|w2, [x20, #0x8]
1c348|mov|x1, #0x30
1c34c|str|w2, [x8, #0x30]
1c354|ldr|x8, [x19, #0x140]
1c358|mov|w10, #0x1
1c35c|mov|w2, #0x1
1c360|mov|x1, #0x38
1c364|str|w10, [x8, #0x38]
1c36c|ldr|w8, [x20, #0xc]
1c370|ldr|x9, [x19, #0x150]
1c374|str|w8, [x9, #0x60]
1c378|ldr|x8, [x19, #0x150]
1c37c|str|w10, [x8, #0x30]
1dc20|pacibsp|
1dc38|ldr|x8, [x19, #0x140]
1dc40|ldr|w8, [x8, #0x44]
1dc44|str|w8, [x20, #0x4]
1dc48|ldr|x8, [x19, #0x140]
1dc4c|ldr|w8, [x8, #0x48]
1dc50|str|w8, [x20, #0x8]
1dc54|ldr|x8, [x19, #0x150]
1dc58|ldr|w8, [x8, #0x28]
1dc5c|str|w8, [x20, #0xc]
1dc60|ldr|x8, [x19, #0x150]
1dc64|ldr|w8, [x8, #0x2c]
1dc68|str|w8, [x20, #0x10]
1dcb4|str|w2, [x8, #0x3c]
1dcc8|str|w2, [x8, #0x40]
1dce0|str|w10, [x8, #0x30]
1dce8|ldr|w8, [x20, #0xc]
1dcec|ldr|x9, [x19, #0x150]
1dcf0|str|w8, [x9, #0x3c]
1dcf4|ldr|w8, [x20, #0x10]
1dcf8|ldr|x9, [x19, #0x150]
1dcfc|str|w8, [x9, #0x40]
1dd04|str|w10, [x8, #0x30]
1efd8|cmp|w8, #0x1
1efe8|ldr|x23, [x20, #0x8]
1eff0|ldp|w8, w2, [x23, #0x4]
1f048|ubfx|w15, w2, #7, #1
1f190|mov|w15, #0xf
1fc8c|mov|w1, #0x8
1fc94|bl|0x140026460 <.text+0x25460>
"""
ANCHORS={int(a,16):(m,o) for a,m,o in (row.split("|",2) for row in SOURCE.strip().splitlines())}
def require(ok,why):
    if not ok:raise AssertionError("E004PA_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004pa-original-modezero-full-versus-nonzero-lite-pattern-TOP-snapshot-register-layout-static-v1",
      "parent_git_revision":"a6935a397c19a3633d12dc08280278eed88318eb",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "accepted_Linux_VFE680_source_sha256":VFE_SHA,
      "original_exact_ARM64_instruction_anchors":len(ANCHORS),
      "original_IFE_mode_zero_snapshot_callback_RVA":"0x1dc20",
      "original_IFE_mode_nonzero_snapshot_callback_RVA":"0x1c2b0",
      "original_mode_zero_TOP_status_offsets":["0x44","0x48"],
      "original_mode_nonzero_TOP_status_offsets":["0x1c","0x20"],
      "both_modes_TOP_status0_and_status1_record_offsets":["0x4","0x8"],
      "original_mode_zero_TOP_clear_command_offsets":["0x3c","0x40","0x30"],
      "original_mode_nonzero_TOP_clear_command_offsets":["0x2c","0x30","0x38"],
      "accepted_Linux_nonlite_TOP_status_offsets":["0x44","0x48"],
      "accepted_Linux_lite_TOP_status_offsets":["0x1c","0x20"],
      "accepted_Linux_nonlite_TOP_clear_command_offsets":["0x3c","0x40","0x30"],
      "accepted_Linux_lite_TOP_clear_command_offsets":["0x2c","0x30","0x38"],
      "original_mode_zero_BUS_status_selected_window_offsets":["0x28","0x2c"],
      "original_mode_nonzero_BUS_status_selected_window_offsets":["0x28"],
      "original_mode_zero_BUS_side_write_selected_window_offsets":["0x3c","0x40","0x30"],
      "original_mode_nonzero_BUS_side_write_selected_window_offsets":["0x60","0x30"],
      "original_mode_zero_BUS_side_writes_match_accepted_Linux_nonlite_BUS_clear":False,
      "original_mode_nonzero_BUS_side_writes_match_accepted_Linux_lite_BUS_clear":False,
      "original_mode_nonzero_callback_proves_physically_selected_IFELITE_or_rear4k_mode":False,
      "original_mode_zero_TOP_status1_bit7_is_directly_valid_for_mode_nonzero_BF_event":False,
      "original_live_rear4k_selected_IFE_callback_mode_and_BF0x0f_observed":False,
      "original_snapshot_TO_type_one_event_pointer_identity_proven":False,
      "native_Linux_rear_IRQ_ack_and_WM16_DMA_generation_retirement_proven":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_proven":False,
      "Golden_boot_camera_or_kernel_modified":False,
      "OEM_private_binary_bulk_disassembly_physical_DMA_KD_optical_exported":False,
    }
def strict(x):require(x==facts(),"saved scalar differs or false hardware conclusion")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original OEM ISP SHA")
    require(hashlib.sha256(VFE.read_bytes()).hexdigest()==VFE_SHA,"accepted Linux VFE680 SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-0x140000000:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for a,w in ANCHORS.items():require(ins.get(a)==w,"original ISA RVA %x"%a)
    v=VFE.read_text()
    for line in (
      "#define VFE_TOP_IRQn_STATUS(vfe, n)\t\t((vfe_is_lite(vfe) ? 0x1c : 0x44) + (n) * 4)",
      "#define VFE_TOP_IRQn_CLEAR(vfe, n)\t\t((vfe_is_lite(vfe) ? 0x2c : 0x3c) + (n) * 4)",
      "#define VFE_TOP_IRQ_CMD(vfe)\t\t\t(vfe_is_lite(vfe) ? 0x38 : 0x30)",
      "#define VFE_BUS_IRQn_CLEAR(vfe, n)\t\t((vfe_is_lite(vfe) ? 0x220 : 0xc20) + (n) * 4)",
      "#define VFE_BUS_IRQ_GLOBAL_CLEAR(vfe)\t\t(vfe_is_lite(vfe) ? 0x230 : 0xc30)",
    ):require(line in v,"original accepted Linux branch register definition "+line[:38])
    oz=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004oz-original-ife-dual-callback-registration-static/RESULT.json").read_text())
    require(oz["original_snapshot_wrapper_invoker_and_type_one_event_record_producer_proven"] is False and
            oz["original_live_rear4k_IFE_mode_and_BF_event_proven"] is False,
            "original callback registration not same-session mode evidence")
    f=facts();saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==f,"saved scalar result altered")
    else:saved.write_text(json.dumps(f,sort_keys=True,indent=2)+"\n")
    muts=(
      ("sha","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("linux","accepted_Linux_VFE680_source_sha256","0"*64),
      ("zero","original_IFE_mode_zero_snapshot_callback_RVA","0x1c2b0"),
      ("nonzero","original_IFE_mode_nonzero_snapshot_callback_RVA","0x1dc20"),
      ("zero_top","original_mode_zero_TOP_status_offsets",["0x1c","0x20"]),
      ("nonzero_top","original_mode_nonzero_TOP_status_offsets",["0x44","0x48"]),
      ("zero_clear","original_mode_zero_TOP_clear_command_offsets",["0x2c","0x30","0x38"]),
      ("nonzero_clear","original_mode_nonzero_TOP_clear_command_offsets",["0x3c","0x40","0x30"]),
      ("linux_full","accepted_Linux_nonlite_TOP_status_offsets",["0x1c","0x20"]),
      ("linux_lite","accepted_Linux_lite_TOP_status_offsets",["0x44","0x48"]),
      ("buszero","original_mode_zero_BUS_side_write_selected_window_offsets",["0x20","0x24","0x30"]),
      ("bus_nonzero","original_mode_nonzero_BUS_side_write_selected_window_offsets",["0x20","0x30"]),
      ("bus_ack","original_mode_zero_BUS_side_writes_match_accepted_Linux_nonlite_BUS_clear",True),
      ("bus_ack_lite","original_mode_nonzero_BUS_side_writes_match_accepted_Linux_lite_BUS_clear",True),
      ("fake_lite","original_mode_nonzero_callback_proves_physically_selected_IFELITE_or_rear4k_mode",True),
      ("fake_general_BF","original_mode_zero_TOP_status1_bit7_is_directly_valid_for_mode_nonzero_BF_event",True),
      ("fake_live","original_live_rear4k_selected_IFE_callback_mode_and_BF0x0f_observed",True),
      ("fake_record","original_snapshot_TO_type_one_event_pointer_identity_proven",True),
      ("fake_DMA","native_Linux_rear_IRQ_ack_and_WM16_DMA_generation_retirement_proven",True),
      ("fake_4k","native_Linux_rear_processed_hardware_ISP_4k_optical_proven",True),
      ("fake_Golden","Golden_boot_camera_or_kernel_modified",True),
      ("fake_private","OEM_private_binary_bulk_disassembly_physical_DMA_KD_optical_exported",True),
    )
    for name,k,value in muts:
        bad=copy.deepcopy(f);bad[k]=value
        try:strict(bad)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PA_NEGATIVE_FAILED_OPEN "+name)
    print("PASS_E004PA_%d_EXACT_ORIGINAL_ARM64_ANCHORS_22_NEGATIVES_MODE0_FULL_TOP_VS_NONZERO_LITE_PATTERN_HW_MODE_BF_DMA_UNPROVEN_GOLDEN_SAFE"%len(ANCHORS))
