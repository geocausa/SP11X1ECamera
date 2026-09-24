#!/usr/bin/env python3
"""E004pj: fail-closed accepted Linux SP11 CSID RDI vs rear PIX/BF bridge.

One machine: SHA-locked READ ONLY accepted front-critical CAMSS source and
original static+live scalar milestones, GCC/Clang C11 synthetic model.
No private OEM executable/log/KD/physical/DMA/pixels exported. No real IRQ,
CAMSS edits, reboot, device call or runtime rear arm.
"""
import copy
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
KERNEL=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
HASHES={
    "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
    "camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
    "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
    "camss-vfe.c":"98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
    "camss-vfe.h":"440b03e1d2701c311cddc6beeae70bccfea5f472f75790a1879167d66395e857",
}
MODEL_HASHES={
    "bf-csid-to-wm16-offline.h":"e998010372a9e546c74b846b25475872ad82d1db6c216174ea0ac23a6133a727",
    "test-bf-csid-to-wm16-offline.c":"cc0ea02e19c1a618ff2e31e749dc90403a276541d2f38508a5b6e0363fdb7507",
}
def require(condition,why):
    if not condition:
        raise AssertionError("E004PJ_FAIL_CLOSED "+why)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def facts():
    return {
      "schema":"sp11-e004pj-CSID680-RDI-versus-rear-BF-stats-completion-bridge-and-flexible-verified-IRQ-source-offline-v1",
      "parent_git_revision":"2c95b389a0859e1e1ca7dcee6f23168513000d4a",
      "accepted_same_SP11_native_CAMSS_critical_file_hashes_unchanged":HASHES,
      "new_OFFLINE_model_file_hashes":MODEL_HASHES,
      "evidence_tier":"D_OFFLINE_C11_BF_BRIDGE_PLUS_S_ACCEPTED_SP11_CAMSS_AND_E004PI_LIVE_WINDOW_SCALARS_NOT_HARDWARE_REAR_DMA",
      "original_windows_rear4k_two_phase_CSID1_BUF_DONE_bit7_latched_and_unmasked_proven":True,
      "accepted_native_full_CSID680_RDI_BUF_DONE_bit_offset":14,
      "accepted_native_full_CSID680_RDI_done_port_count":4,
      "accepted_native_CSID680_BF_stats_candidate_bit":7,
      "accepted_native_CSID680_VIDEO_bit":0,
      "accepted_native_CSID680_already_ACKs_BUF_DONE":True,
      "accepted_native_CSID680_CSID_BF_bit7_forwarded_to_generic_vfe_buf_done":False,
      "accepted_native_CSID680_RDI_bits14_through17_forwarded_to_generic_camss_buf_done":True,
      "accepted_native_generic_camss_buf_done_maps_hw_id_to_matching_vfe_id":True,
      "accepted_native_generic_vfe_buf_done_immediately_retires_VB2_ready_buffer":True,
      "accepted_native_generic_vfe_get_output_v2_uses_single_WM_per_RDI_PIX_line":True,
      "accepted_native_generic_vfe_buf_done_has_per_frame_six_stats_group8_FIFO_WM16_owner_fence":False,
      "accepted_native_VFE680_IRQ_handler_still_noop":True,
      "original_OEM_BF_event0x0f_uses_fifo8_and_WM16_static_source_proven":True,
      "original_OEM_rear4k_live_BF_event0x0f_FIFO8_WM16_same_frame_confirmed":False,
      "separate_VFE_irq_always_required_in_all_Titan_gen3_architectures":False,
      "trusted_CSID_BF7_alone_can_authorize_WM16_DMA_retirement":False,
      "trusted_WM16_stats_buffer_done_bridge_with_same_generation_and_IOMMU_proven_on_SP11":False,
      "offline_two_possible_proven_WM16_source_domains_modelled":True,
      "offline_all_status_word_0_to_65535_routes_exhaustively_checked":True,
      "offline_c11_assertions_per_compiler":262267,
      "offline_gcc_C11_model_pass":True,
      "offline_clang_ASan_UBSan_C11_model_pass":True,
      "native_Linux_rear_hardware_ISP_4k_optical_proven":False,
      "rear_Linux_hardware_ISP_runtime_authorized":False,
      "protected_Golden_boot_kernel_camera_hardware_modified":False,
      "OEM_binary_bulk_original_disassembly_private_KD_DMA_physical_pixels_exported":False,
      "accepted_native_CSID680_BF_stats_irq_to_six_group_WM16_owner_generation_runtime_hook_implemented":False,
      "next_original_gate":"same_session_rear4k_original_mode_BF_event0x0f_FIFO8_entry_WM16_buffer_identity_and_DMA_retirement",
      "next_native_gate":"validate_whether_CSID_BF_bit7_IS_independent_WM16_bus_done_for_X1E_then_implement_trusted_per_generation_stats_bridge_and_IOMMU_stop_in_isolated_non_Golden_test",
    }
def strict(d):
    require(d==facts(),"sourced code/negative control changed")
def check_sources():
    for name,digest in HASHES.items():
        require(sha(KERNEL/name)==digest,"accepted native CAMSS source changed "+name)
    for name,digest in MODEL_HASHES.items():
        require(sha(HERE/name)==digest,"offline C11 model source changed "+name)
    csid=(KERNEL/"camss-csid-680.c").read_text()
    core=(KERNEL/"camss.c").read_text()
    vfe=(KERNEL/"camss-vfe.c").read_text()
    vfe680=(KERNEL/"camss-vfe-680.c").read_text()
    hdr=(KERNEL/"camss-vfe.h").read_text()
    for exp in (
        r"#define\s+CSID_BUF_DONE_IRQ_STATUS\s+0x8c\b",
        r"#define\s+CSID_BUF_DONE_IRQ_MASK\s+0x90\b",
        r"#define\s+CSID_BUF_DONE_IRQ_CLEAR\s+0x94\b",
        r"#define\s+BUF_DONE_IRQ_STATUS_RDI_OFFSET\s+\(csid_is_lite\(csid\)\s*\?\s*1\s*:\s*14\)",
        r"#define\s+CSID_BUF_DONE_VIDEO\s+BIT\(0\)",
    ):
        require(re.search(exp,csid),"same-SP11 CSID680 bit/offset definition mismatch "+exp)
    require("buf_done_val = readl(csid->base + CSID_BUF_DONE_IRQ_STATUS);" in csid and
            "writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);" in csid and
            "writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);" in csid,
            "CSID IRQ source read + ack owns BUF_DONE status")
    require(re.search(r"(?s)for\s*\(i\s*=\s*0;\s*i\s*<\s*MSM_CSID_MAX_SRC_STREAMS;\s*i\+\+\).*?"
                      r"if\s*\(buf_done_val\s*&\s*BIT\(BUF_DONE_IRQ_STATUS_RDI_OFFSET\s*\+\s*i\)\)"
                      r"\s*camss_buf_done\(csid->camss,\s*csid->id,\s*i\);",csid) is not None,
            "only RDI index bits forwarded through generic CAMSS buf_done")
    require("CSID_BUF_DONE_BF" not in csid and "CSID_BUF_DONE_BAF" not in csid and
            "camss_buf_done(csid->camss, csid->id, 7)" not in csid,
            "no accepted CSID BF statistics → generic video-line callback")
    require(re.search(r"(?s)void\s+camss_buf_done\(struct camss \*camss, int hw_id, int port_id\)"
                      r"\s*\{.{0,450}?vfe->res->hw_ops->vfe_buf_done\(vfe, port_id\);",core) is not None,
            "generic camss_buf_done forwards a VIDEO LINE id, not BF group8")
    require("void vfe_buf_done(struct vfe_device *vfe, int wm)" in vfe and
            "struct vfe_line *line = &vfe->line[vfe->wm_output_map[wm]];" in vfe and
            "vb2_buffer_done(&ready_buf->vb.vb2_buf, VB2_BUF_STATE_DONE);" in vfe and
            "output->wm_num = 1;" in vfe and
            "vfe->wm_output_map[line->id] = line->id;" in vfe,
            "generic VFE one-WM output maps + eager vb2 retire not stats FIFO8 WM16")
    require("VFE_LINE_RDI0 = 0" in hdr and "VFE_LINE_PIX = 3" in hdr and
            "VFE_LINE_NUM_MAX = 4" in hdr,
            "accepted VFE exposes four output lines, not WM16 group8")
    require(re.search(r"(?s)static irqreturn_t vfe_isr\(int irq, void \*dev\)"
                      r"\s*\{\s*return IRQ_HANDLED;\s*\}",vfe680) is not None,
            "accepted real VFE680 ISR must stay no-op")
    ph=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ph-original-type1-preparation-queue-status-provenance-static/RESULT.json").read_text())
    pi=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pi-original-live-rear-csid-bf-bit7-wm16-fence-offline/RESULT.json").read_text())
    nv=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/BF-RESULT.json").read_text())
    ov=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ov-rear-six-group-generation-ownership-offline/RESULT.json").read_text())
    require(ph["original_zero_mode_CSID_BUF_DONE_status_bit7_to_type1_BF0x0f_static_proven"] is True and
            ph["original_CSID_BUF_DONE_bit7_equals_independent_VFE_WM16_DMA_completion_proven"] is False,
            "type1 status bit7 source is static, buffer retire is unproven")
    require(pi["same_original_rear4k_two_live_physical_CSID1_BUF_DONE_bit7_set_and_unmasked"] is True and
            pi["original_per_frame_FIFO8_group8_matching_WM16_DMA_completion_observed"] is False,
            "two original live snapshots cannot be promoted to frame retirement")
    require(nv["BF_static_dispatch"]["driver_event_id"]=="0x0f" and
            nv["BF_static_dispatch"]["queue_group_index"]==8 and
            nv["BF_static_dispatch"]["BF_group_client_resource_port"]=="0x300d" and
            nv["BF_event_live_during_OEM_rear_recording_observed"] is False,
            "original BF event group8 distinct from RDI and still not live observed")
    require(ov["six_group_event_FIFO_WM_mask_source_matches_E004nv"] is True and
            ov["real_bus_IRQ_and_DMA_completion_proven"] is False,
            "existing six-group owner model remains OFFLINE, no DMA")
def run_c():
    results=[]
    src=HERE/"test-bf-csid-to-wm16-offline.c"
    with tempfile.TemporaryDirectory(prefix="e004pj-offline-") as tmp:
        for name,flags in (
            ("gcc",["gcc","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-O2"]),
            ("clang-asan-ubsan",["clang","-std=c11","-Wall","-Wextra","-Werror","-pedantic",
                                "-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer"]),
        ):
            exe=str(Path(tmp)/name)
            subprocess.run(flags+[str(src),"-o",exe],check=True,capture_output=True,text=True,timeout=30)
            out=subprocess.run([exe],check=True,capture_output=True,text=True,timeout=30).stdout.strip()
            require(out.startswith("PASS_E004PJ_262267_OFFLINE_C11_ASSERTIONS_") and
                    out.endswith("_NEITHER_PROVEN_ON_SP11_RUNTIME_DENIED"),
                    "exact synthetic model assertions changed "+name)
            results.append(out)
    return results
if __name__=="__main__":
    check_sources()
    compiler_results=run_c()
    d=facts()
    path=HERE/"RESULT.json"
    if path.exists():
        require(json.loads(path.read_text())==d,"saved source-backed result changed")
    else:
        path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    neg=(
      ("fake_RDI7","accepted_native_full_CSID680_RDI_BUF_DONE_bit_offset",7),
      ("fake_stats_RDI","accepted_native_CSID680_BF_stats_candidate_bit",14),
      ("fake_video","accepted_native_CSID680_VIDEO_bit",7),
      ("fake_csid_ack","accepted_native_CSID680_already_ACKs_BUF_DONE",False),
      ("fake_BF_forward","accepted_native_CSID680_CSID_BF_bit7_forwarded_to_generic_vfe_buf_done",True),
      ("fake_RDI_missing","accepted_native_CSID680_RDI_bits14_through17_forwarded_to_generic_camss_buf_done",False),
      ("fake_video_safe","accepted_native_generic_vfe_buf_done_immediately_retires_VB2_ready_buffer",False),
      ("fake_singleWM","accepted_native_generic_vfe_get_output_v2_uses_single_WM_per_RDI_PIX_line",False),
      ("fake_stats_six_group","accepted_native_generic_vfe_buf_done_has_per_frame_six_stats_group8_FIFO_WM16_owner_fence",True),
      ("fake_ISR","accepted_native_VFE680_IRQ_handler_still_noop",False),
      ("fake_original","original_OEM_BF_event0x0f_uses_fifo8_and_WM16_static_source_proven",False),
      ("fake_live","original_OEM_rear4k_live_BF_event0x0f_FIFO8_WM16_same_frame_confirmed",True),
      ("fake_sep_irq","separate_VFE_irq_always_required_in_all_Titan_gen3_architectures",True),
      ("fake_self_attest","trusted_CSID_BF7_alone_can_authorize_WM16_DMA_retirement",True),
      ("fake_realbridge","trusted_WM16_stats_buffer_done_bridge_with_same_generation_and_IOMMU_proven_on_SP11",True),
      ("fake_two_domains","offline_two_possible_proven_WM16_source_domains_modelled",False),
      ("fake_exhaustive","offline_all_status_word_0_to_65535_routes_exhaustively_checked",False),
      ("fake_assertions","offline_c11_assertions_per_compiler",262266),
      ("fake_gcc","offline_gcc_C11_model_pass",False),
      ("fake_clang","offline_clang_ASan_UBSan_C11_model_pass",False),
      ("fake_optical","native_Linux_rear_hardware_ISP_4k_optical_proven",True),
      ("fake_arm","rear_Linux_hardware_ISP_runtime_authorized",True),
      ("fake_golden","protected_Golden_boot_kernel_camera_hardware_modified",True),
      ("fake_private","OEM_binary_bulk_original_disassembly_private_KD_DMA_physical_pixels_exported",True),
      ("fake_kernel_bridge","accepted_native_CSID680_BF_stats_irq_to_six_group_WM16_owner_generation_runtime_hook_implemented",True),
    )
    for label,key,value in neg:
        changed=copy.deepcopy(d)
        changed[key]=value
        try:strict(changed)
        except AssertionError:continue
        raise AssertionError("E004PJ_NEGATIVE_FAILED_OPEN "+label)
    print("PASS_E004PJ_5_ACCEPTED_NATIVE_SOURCE_SHA_PINNED_2_OFFLINE_SOURCES_"+str(len(neg))+
          "_NEGATIVES_2_COMPILERS_262267_ASSERTIONS_EACH_GOLDEN_UNTOUCHED")
    for out in compiler_results:print(out)
