#!/usr/bin/env python3
"""E004pq: source-lock exact original Windows KD instruction hits, NOT DMA.

SP7 original Windows PRIVATE KD log was read and SHA-checked remotely via
Fabric; this SP11 Linux verifier reads only a minimal non-private scalar
ledger, and rechecks four same-SP11 OEM ISP instruction identities. The SP7
private log is NOT mounted here: we do not pretend to independently rehash it.
No runtime camera/IRQ/MMIO, kernel changes, KD commands or sensitive export.
"""
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
# All four disassemblies were also checked at their actual PE-image-base
# relocated locations in the SP7 original Windows KD session. Only the
# bounded source RVAs/instruction identities are archived here.
ISA={
    0x1675c:("tst","w8, #0x2"),
    0x1b67c:("ldr","w8, [x8, #0x8c]"),
    0x20c04:("ldr","w8, [x8, #0x8c]"),
    0x1f190:("mov","w15, #0xf"),
}
AUDIT={
    "schema":"E004PQ_SP7_PRIVATE_KD_LOG_SCALAR_AUDIT_V1",
    "source_location":"SP7_PRIVATE_E004PS_KD_REARBF_CONPTY_20260924_NOT_EXPORTED",
    "SP7_original_private_KD_log_SHA256":"b9bd34f68101d987b7d86cb0de3ca713f26a62fab39295ec4661157fe250ffcc",
    "source_logged_lines":354,
    "four_absolute_breakpoints_armed_after_original_PEIISA_verification":True,
    "breakpoint_commands_were_one_shot_and_gc_autocontinue":True,
    "logged_hit_count_config_bit1_instruction":1,
    "logged_hit_count_type1_zero_preparer_instruction":1,
    "logged_hit_count_type1_nonzero_preparer_instruction":0,
    "logged_hit_count_BF_event0x0f_assignment_instruction":1,
    "ordered_hit_marker_line_numbers":[341,346,351],
    "logged_config_test_w8_zero_at_instruction_before_tst":True,
    "logged_zero_preparer_x8_was_register_window_POINTER_not_status_word":True,
    "logged_BF_assignment_instruction_stack_snapshot_exists":True,
    "logged_per_hit_timestamp_session_instance_frame_FIFO8_WM16_DMA_correlation_exists":False,
    "verified_actual_original_OEM_driver_PE_relocated_instr_at_four_locations":True,
    "full_private_KD_log_available_on_SP11_linux_for_verifier_rehash":False,
}
def facts():
    return {
        "schema":"SP11_E004pq_original_Windows_KD_relocated_BF_instruction_reached_source_locked_v1",
        "parent_git_revision":"d464f5e62f2de9a891c927f5a0cf1a5caf3277a2",
        "original_OEM_ISP_sha256":SHA,
        "original_exact_ARM64_source_instruction_anchors":len(ISA),
        "private_SP7_log_provenance_and_only_safe_scalar_audit":AUDIT,
        "evidence_tier":"P_ORIGINAL_KD_REAL_INSTRUCTION_HITS_NOT_P_REAR_FRAME_BF_FIFO8_WM16_DMA",
        "source_format_config_bit1_test_instruction_reached_live":True,
        "source_format_bit1_zero_at_that_one_observed_test":True,
        "source_format_zero_preparer_instruction_reached_live":True,
        "source_format_nonzero_preparer_instruction_not_observed_during_one_shot_trace":True,
        "BF_event0x0f_id_assignment_instruction_reached_live":True,
        "BF_event0x0f_worker_instruction_reached_in_same_rear4k_FRAME_or_instance_as_prep_proven":False,
        "BF_event0x0f_queued_FIFO8_entry_or_hardware_output_observed":False,
        "type1_source_CSID1_status_bit7_current_per_hit_value_observed":False,
        "original_full_IFE_resource_count_in_same_rear4k_session_observed":False,
        "original_per_device_worker_mode_and_type1_format_pair_same_generation_proven":False,
        "original_per_frame_FIFO8_entry_matched_WM16_bus_or_buffer_identity_proven":False,
        "original_WM16_DMA_and_IOMMU_generation_retirement_proven":False,
        "native_Linux_rear_hardware_ISP_processed_4k_optical_proven":False,
        "native_rear_hardware_ISP_runtime_authorized":False,
        "source_only_no_reboot_hardware_camera_kernel_or_Golden_change":True,
        "private_original_KD_addresses_register_pointers_pixels_not_exported":True,
        "next_gate":"same_original_rear4k_instance_generation_type1_zero_preparer_status_bit7_to_BF_FIFO8_WM16_queued_buffer_and_separate_trusted_DMA_IOMMU_completion",
    }
def require(ok,reason):
    if not ok:
        raise AssertionError("E004PQ_FAIL_CLOSED "+reason)
def validate(d):
    require(d==facts(),"private evidence/scalar claims or native safety changed")
if __name__=="__main__":
    require(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,
            "same SP11 original OEM ISP changed")
    output=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-0x140000000:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(output)}
    for rva,want in ISA.items():
        require(ins.get(rva)==want,"exact original ARM64 RVA %x"%rva)
    for subdir,field,want in [
        ("e004pk-full-ife-count-vs-type1-format-mode-static",
         "original_live_rear4k_input_config_word0x8c_bit1_observed",False),
        ("e004pi-original-live-rear-csid-bf-bit7-wm16-fence-offline",
         "original_per_frame_FIFO8_group8_matching_WM16_DMA_completion_observed",False),
        ("e004pj-csid-bf-statistics-completion-bridge-offline",
         "trusted_WM16_stats_buffer_done_bridge_with_same_generation_and_IOMMU_proven_on_SP11",False),
    ]:
        prior=json.loads((ROOT/"experiments/E004-front-ir-vd55g0"/subdir/"RESULT.json").read_text())
        require(prior[field] is want,"older evidence stays historically scoped "+field)
    require(AUDIT["logged_hit_count_type1_nonzero_preparer_instruction"]==0 and
            AUDIT["logged_hit_count_type1_zero_preparer_instruction"]==1 and
            AUDIT["logged_hit_count_BF_event0x0f_assignment_instruction"]==1 and
            AUDIT["ordered_hit_marker_line_numbers"]==[341,346,351],
            "SP7 audited original log marker counts and order")
    require(AUDIT["source_logged_lines"]==354 and
            len(AUDIT["SP7_original_private_KD_log_SHA256"])==64 and
            not AUDIT["full_private_KD_log_available_on_SP11_linux_for_verifier_rehash"],
            "private original log is audit-referenced, NOT local independent rehashed")
    source=facts()
    path=HERE/"RESULT.json"
    if path.exists():
        require(json.loads(path.read_text())==source,"saved source-backed scalar result altered")
    else:
        path.write_text(json.dumps(source,indent=2,sort_keys=True)+"\n")
    mutations=[
        ("BF_not_hit","BF_event0x0f_id_assignment_instruction_reached_live",False),
        ("config_not_hit","source_format_config_bit1_test_instruction_reached_live",False),
        ("config_nonzero","source_format_bit1_zero_at_that_one_observed_test",False),
        ("zero_not_hit","source_format_zero_preparer_instruction_reached_live",False),
        ("fabricated_nonzero","source_format_nonzero_preparer_instruction_not_observed_during_one_shot_trace",False),
        ("fabricated_same_frame","BF_event0x0f_worker_instruction_reached_in_same_rear4k_FRAME_or_instance_as_prep_proven",True),
        ("fabricated_fifo","BF_event0x0f_queued_FIFO8_entry_or_hardware_output_observed",True),
        ("fabricated_hitstatus","type1_source_CSID1_status_bit7_current_per_hit_value_observed",True),
        ("fabricated_live_count","original_full_IFE_resource_count_in_same_rear4k_session_observed",True),
        ("fabricated_modepair","original_per_device_worker_mode_and_type1_format_pair_same_generation_proven",True),
        ("fabricated_buffer","original_per_frame_FIFO8_entry_matched_WM16_bus_or_buffer_identity_proven",True),
        ("fabricated_DMA","original_WM16_DMA_and_IOMMU_generation_retirement_proven",True),
        ("fabricated_optical","native_Linux_rear_hardware_ISP_processed_4k_optical_proven",True),
        ("fabricated_arm","native_rear_hardware_ISP_runtime_authorized",True),
        ("fabricated_golden","source_only_no_reboot_hardware_camera_kernel_or_Golden_change",False),
        ("fabricated_export","private_original_KD_addresses_register_pointers_pixels_not_exported",False),
        ("fake_source_SHA","original_OEM_ISP_sha256","0"*64),
        ("fake_anchor_count","original_exact_ARM64_source_instruction_anchors",3),
        ("fake_private_audit","private_SP7_log_provenance_and_only_safe_scalar_audit",{}),
        ("fake_tier","evidence_tier","P_DMA_COMPLETION"),
        ("fake_gate","next_gate","ready_to_arm"),
    ]
    for label,key,value in mutations:
        mutated=copy.deepcopy(source)
        mutated[key]=value
        try:validate(mutated)
        except AssertionError:continue
        raise AssertionError("E004PQ_NEGATIVE_FAIL_OPEN "+label)
    for key,value in [
        ("logged_hit_count_BF_event0x0f_assignment_instruction",0),
        ("logged_hit_count_type1_nonzero_preparer_instruction",1),
        ("logged_config_test_w8_zero_at_instruction_before_tst",False),
        ("logged_per_hit_timestamp_session_instance_frame_FIFO8_WM16_DMA_correlation_exists",True),
        ("full_private_KD_log_available_on_SP11_linux_for_verifier_rehash",True),
    ]:
        changed=copy.deepcopy(source)
        changed["private_SP7_log_provenance_and_only_safe_scalar_audit"][key]=value
        try:validate(changed)
        except AssertionError:continue
        raise AssertionError("E004PQ_PRIVATE_LEDGER_NEGATIVE_FAIL_OPEN "+key)
    print("PASS_E004PQ_%d_EXACT_ORIGINAL_ARM64_SOURCE_ANCHORS_%d_NEGATIVES_SP7_PRIVATE_LOG_SHA_REFERENCED_THREE_REAL_INSTRUCTION_HITS_NO_PER_FRAME_WM16_DMA_GOLDEN_PROTECTED"%(len(ISA),len(mutations)+5))
