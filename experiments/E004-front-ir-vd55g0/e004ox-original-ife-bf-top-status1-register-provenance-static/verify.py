#!/usr/bin/env python3
"""E004ox: mode-zero original ISP TOP status1 bit7 BF source candidate.

Offline exact original same-SP11 OEM ARM64 and accepted Linux MMIO definitions.
This verifies independent status record-format alignment but does not invent
the missing same-session producer-to-consumer link, IRQ ACK or DMA fence.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
VFE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-vfe-680.c")
VFESHA="99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208"
BASE=0x140000000
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
1a0fc|add|x8, x19, #0x6b, lsl #12
1a100|str|x9, [x8, #0x6d8]
24a3c|add|x8, x0, #0x6b, lsl #12
24a40|ldr|x8, [x8, #0x6b0]
24a54|blr|x15
1dc34|mov|x19, x0
1dc38|ldr|x8, [x19, #0x140]
1dc3c|mov|x20, x1
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
1dcac|ldr|x8, [x19, #0x140]
1dcb4|str|w2, [x8, #0x3c]
1dcbc|ldr|w2, [x20, #0x8]
1dcc0|ldr|x8, [x19, #0x140]
1dcc8|str|w2, [x8, #0x40]
1dcd0|ldr|x8, [x19, #0x140]
1dce0|str|w10, [x8, #0x30]
1dce8|ldr|w8, [x20, #0xc]
1dcec|ldr|x9, [x19, #0x150]
1dcf0|str|w8, [x9, #0x3c]
1dcf4|ldr|w8, [x20, #0x10]
1dcf8|ldr|x9, [x19, #0x150]
1dcfc|str|w8, [x9, #0x40]
1dd00|ldr|x8, [x19, #0x150]
1dd04|str|w10, [x8, #0x30]
1efd8|cmp|w8, #0x1
1efe4|b.ne|0x14001fecc <.text+0x1eecc>
1efe8|ldr|x23, [x20, #0x8]
1eff0|ldp|w8, w2, [x23, #0x4]
1f048|ubfx|w15, w2, #7, #1
1f188|cbz|w15, 0x14001f19c <.text+0x1e19c>
1f190|mov|w15, #0xf
1f194|str|w15, [x7, w1, uxtw #2]
1fc60|cmp|w8, #0xf
1fc8c|mov|w1, #0x8
1fc94|bl|0x140026460 <.text+0x25460>
1d710|ldr|x8, [x0, #0x150]
1d714|ldr|w8, [x8, #0x1270]
1d71c|ldr|x8, [x0, #0x150]
1d720|ldr|w8, [x8, #0x1200]
2247c|mov|x9, #0xc00
22480|mov|x8, #0x1200
22484|csel|x8, x9, x8, lo
22488|add|x8, x8, x3
2248c|str|x8, [x20, #0x150]
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (row.split("|",2) for row in SOURCE.strip().splitlines())}
def require(ok,why):
    if not ok:raise AssertionError("E004OX_FAIL_CLOSED "+why)
def facts():
    return {
      "schema":"sp11-e004ox-original-IFE-mode0-BF-status-word2-bit7-maps-TOP-status1-bit7-static-v1",
      "parent_git_revision":"f0174c819bf465a3e5f68531f50f4c4990ee9458",
      "original_same_SP11_OEM_ISP_sha256":SHA,
      "accepted_Linux_VFE680_source_sha256":VFESHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "original_IFE_mode_zero_status_snapshot_callback_RVA":"0x1dc20",
      "original_IFE_mode_zero_status_snapshot_install_RVA":"0x1a074",
      "original_IFE_mode_zero_event_dispatch_install_RVA":"0x1a100",
      "original_status_snapshot_TOP_status0_original_base_offset":"0x44",
      "original_status_snapshot_TOP_status1_original_base_offset":"0x48",
      "original_status_snapshot_TOP_status1_record_offset":"0x8",
      "original_status_snapshot_BUS_status0_mode0_base_offset":"0xc28",
      "original_status_snapshot_BUS_status1_mode0_base_offset":"0xc2c",
      "original_type_one_status_word2_record_offset":"0x8",
      "original_type_one_BF_bit_index_in_status_word2":7,
      "original_type_one_BF_event_id":"0x0f",
      "original_type_one_BF_fifo_group":8,
      "accepted_Linux_nonlite_VFE_TOP_STATUS1_offset":"0x48",
      "accepted_Linux_nonlite_VFE_BUS_STATUS1_offset":"0xc2c",
      "accepted_Linux_nonlite_VFE_BUS_CLEAR0_offset":"0xc20",
      "accepted_Linux_nonlite_VFE_BUS_CLEAR1_offset":"0xc24",
      "original_mode0_snapshot_BUS_side_write_offsets_relative_to_base":["0xc3c","0xc40","0xc30"],
      "original_BUS_side_snapshot_write_offsets_match_accepted_Linux_BUS_CLEAR0_1":False,
      "BF_top_status1_bit7_is_source_backed_mode0_candidate":True,
      "snapshot_producer_to_exact_live_rear4k_BF_status_record_proven":False,
      "original_rear4k_live_IFE_mode0_and_BF0x0f_observed":False,
      "TOP_status1_bit7_alone_proves_fifo8_queued_entry_or_WM16_DMA_retirement":False,
      "native_Linux_rear_VFE_IRQ_ack_and_per_generation_BF_WM16_DMA_retirement_proven":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_frame_proven":False,
      "protected_Golden_boot_camera_or_kernel_modified":False,
      "private_OEM_driver_bulk_disassembly_physical_DMA_KD_optical_exported":False,
    }
def strict(x):require(x==facts(),"scalar facts mismatch or safety promotion")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"same-SP11 original OEM ISP")
    require(hashlib.sha256(VFE.read_bytes()).hexdigest()==VFESHA,"accepted Linux VFE source")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    seen={int(m[1],16)-0x140000000:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for a,expected in ANCHORS.items():require(seen.get(a)==expected,"original exact instruction RVA %x"%a)
    source=VFE.read_text()
    for exact in (
        "#define VFE_TOP_IRQn_STATUS(vfe, n)\t\t((vfe_is_lite(vfe) ? 0x1c : 0x44) + (n) * 4)",
        "#define VFE_BUS_IRQn_STATUS(vfe, n)\t\t((vfe_is_lite(vfe) ? 0x228 : 0xc28) + (n) * 4)",
        "#define VFE_BUS_IRQn_CLEAR(vfe, n)\t\t((vfe_is_lite(vfe) ? 0x220 : 0xc20) + (n) * 4)",
        "#define VFE_BUS_IRQ_GLOBAL_CLEAR(vfe)\t\t(vfe_is_lite(vfe) ? 0x230 : 0xc30)",
        "#define VFE680_X1E_RAW_VIDEO\tBIT(0)",
    ):require(exact in source,"accepted VFE register identity "+exact[:52])
    require(0xc00+0x28==0xc28 and 0xc00+0x2c==0xc2c and
            0xc00+0x3c==0xc3c and 0xc00+0x40==0xc40 and
            (0x44+4)==0x48 and (0xc20+4)==0xc24,
            "mode-zero offset arithmetic and distinct BUS status/clear/write regions")
    previous=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ow-native-vfe-isr-stub-rear-bf-gate-source/RESULT.json").read_text())
    require(previous["vfe680_ISR_body_only_returns_IRQ_HANDLED"] is True and
            previous["native_Linux_rear_BF_FIFO8_hardware_status_irq_ack_DMA_retirement_proven"] is False,
            "earlier real Linux IRQ source missing")
    f=facts(); saved=HERE/"RESULT.json"
    if saved.exists():require(json.loads(saved.read_text())==f,"saved result changed")
    else:saved.write_text(json.dumps(f,sort_keys=True,indent=2)+"\n")
    muts=(
      ("fake_sha","original_same_SP11_OEM_ISP_sha256","0"*64),
      ("fake_callback","original_IFE_mode_zero_status_snapshot_callback_RVA","0x1c2b0"),
      ("fake_status","original_status_snapshot_TOP_status1_original_base_offset","0xc2c"),
      ("fake_record","original_status_snapshot_TOP_status1_record_offset","0xc"),
      ("fake_BF","original_type_one_BF_bit_index_in_status_word2",21),
      ("fake_Fifo","original_type_one_BF_fifo_group",0),
      ("fake_status_linux","accepted_Linux_nonlite_VFE_TOP_STATUS1_offset","0xc2c"),
      ("fake_clear","accepted_Linux_nonlite_VFE_BUS_CLEAR0_offset","0xc3c"),
      ("fake_write","original_mode0_snapshot_BUS_side_write_offsets_relative_to_base",["0xc20","0xc24","0xc30"]),
      ("fake_ack","original_BUS_side_snapshot_write_offsets_match_accepted_Linux_BUS_CLEAR0_1",True),
      ("fake_candidate","BF_top_status1_bit7_is_source_backed_mode0_candidate",False),
      ("fake_link","snapshot_producer_to_exact_live_rear4k_BF_status_record_proven",True),
      ("fake_live","original_rear4k_live_IFE_mode0_and_BF0x0f_observed",True),
      ("fake_dma","TOP_status1_bit7_alone_proves_fifo8_queued_entry_or_WM16_DMA_retirement",True),
      ("fake_linux","native_Linux_rear_VFE_IRQ_ack_and_per_generation_BF_WM16_DMA_retirement_proven",True),
      ("fake_optical","native_Linux_rear_processed_hardware_ISP_4k_optical_frame_proven",True),
      ("fake_golden","protected_Golden_boot_camera_or_kernel_modified",True),
      ("fake_private","private_OEM_driver_bulk_disassembly_physical_DMA_KD_optical_exported",True),
    )
    for name,k,val in muts:
        bad=copy.deepcopy(f);bad[k]=val
        try:strict(bad)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OX_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OX_%d_EXACT_ORIGINAL_ISA_ANCHORS_ACCEPTED_LINUX_TOP1_BIT7_AND_BUS_CLEAR_MISMATCH_%d_NEGATIVES_HW_ACK_DMA_UNPROVEN_GOLDEN_SAFE"%(len(ANCHORS),len(muts)))
