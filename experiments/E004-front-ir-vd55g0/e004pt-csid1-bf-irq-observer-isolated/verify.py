#!/usr/bin/env python3
"""E004pt: verify isolated ARM64 CSID1 BF observation, not DMA completion.

SP11-only private build hashes; never installs/loads a kernel module or
accesses camera MMIO. Exact accepted CAMSS source remains untouched.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ACCEPTED=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
OLD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pt-csid1-bf-irq-observer-build")
BUILT=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pt-csid1-bf-irq-observer-build-fix1")
ACCEPTED_SHA={
    "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
    "camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
    "camss-csid.h":"bd8f68b623f2e8e5a2c624fdd8ce7a901c7fc11fa35a2efbd04f8273fca3aee2",
    "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
    "camss-vfe.c":"98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
}
CANDIDATE_SHA={
    "camss-csid-680.c":"c9dd4be2262e2999b64b79f8a63ca251e7eab3e0f124a86347f97fa650b21d35",
    "camss-csid.h":"6e6c5232886095a4995e3b5c2638d39e9dc97666c0cc5f2d75161a6e58ed2d70",
    "camss-csid-e004pt-bf-observer.inc":"0d110b0e81f02b606d2692a1555f09caef1aa0bd81b6c5d2518cc5999b5efb78",
}
MODEL_SHA={
    "e004pt-observer-model.h":"edd9f83f826ffd8acf90ede37c2e0b6b02522aac859e339be772753582861490",
    "test-e004pt-observer.c":"403ac5a88b80c07d729545571fb41a976f2d4a0113654ed9a111169d969e0909",
    "run-offline.sh":"cd738cee917ab4a74cf1a9c532234a36a86f155cf72b9fc1df8a99c2a18203c0",
}
PARENT="376c172430783b07300d4af780a1fe870982d154"
OLD_MODULE_SHA="63124689b729bb805f1a57c21f1439cf3b49ebc0b9a7c5bc5bf69aeb908c5f86"
MODULE_SHA="e492063f4e950aab50f3cfddd8e8a3db53f784fc0a8b724e3d76acf59961bdec"
VERMAGIC="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"

def require(ok,why):
    if not ok:
        raise AssertionError("E004PT_FAIL_CLOSED "+why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def facts():
    return {
        "schema":"E004pt-isolated-SP11-CSID1-BF-status-only-ARM64-observer-v1",
        "parent_git_revision":PARENT,
        "evidence_class":"S_ACCEPTED_CAMSS_SOURCE_D_ISOLATED_SOURCE_COMPILED_AND_OFFLINE_SIMULATION_NOT_P_HW",
        "accepted_CAMSS_file_sha256":ACCEPTED_SHA,
        "isolated_candidate_modified_source_sha256":CANDIDATE_SHA,
        "isolated_source_observer_header_sha256":CANDIDATE_SHA["camss-csid-e004pt-bf-observer.inc"],
        "isolated_module_path_is_private_on_SP11":True,
        "original_first_compile_module_sha256":OLD_MODULE_SHA,
        "original_first_compile_warning_missing_prototype":True,
        "original_first_builder_exit141_due_nm_grep_q_SIGPIPE_after_successful_compile":True,
        "corrected_distinct_compile_module_sha256":MODULE_SHA,
        "corrected_compile_zero_W1_warnings":True,
        "module_vermagic":VERMAGIC,
        "observes_only_existing_CSID1_full_BF_bit7_status":True,
        "additional_hardware_status_read_or_irq_ack_added":False,
        "generic_RDI_PIX_VB2_buffer_done_added":False,
        "hardware_IRQ_DMA_IOMMU_retirement_inferred_from_BF_observation":False,
        "per_frame_FIFO8_WM16_matched_buffer_identity_proven":False,
        "CSID1_observation_is_known_to_be_rear_not_front":False,
        "offline_C11_status_domain_input_combinations_per_compiler":262144,
        "offline_C11_BF_observation_hits_per_compiler":32768,
        "offline_compilers":"GCC_O2_and_Clang_ASAN_UBSAN",
        "native_rear_hardware_ISP_runtime_authorized":False,
        "candidate_module_installed_or_loaded":False,
        "accepted_Golden_kernel_or_camss_files_modified":False,
        "next_gate":"isolated_provenance_safe_CSID1_BF_live_status_per_frame_owner_FIFO8_nonnull_WM16_match_and_independent_DMA_IOMMU_IRQ_stop",
    }

def main():
    for k,want in ACCEPTED_SHA.items():
        require(sha(ACCEPTED/k)==want,"accepted CAMSS must remain byte-identical: "+k)
    for k,want in CANDIDATE_SHA.items():
        require(sha(BUILT/k)==want,"isolated ARM64 candidate source changed: "+k)
    for k,want in MODEL_SHA.items():
        require(sha(HERE/k)==want,"offline model source changed: "+k)
    require(sha(HERE/"camss-csid-e004pt-bf-observer.inc")==CANDIDATE_SHA["camss-csid-e004pt-bf-observer.inc"],
            "compiled inc not exact reviewed Git inc")
    require(sha(BUILT/"qcom-camss.ko")==MODULE_SHA and
            sha(OLD/"qcom-camss.ko")==OLD_MODULE_SHA,
            "preserve BOTH one-use builds, corrected and warning-bearing")
    require(subprocess.check_output(["modinfo","-F","vermagic",str(BUILT/"qcom-camss.ko")],text=True).strip()==VERMAGIC,
            "exact Golden module ABI")
    symbols=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(BUILT/"qcom-camss.ko")],text=True)
    require(re.search(r"(?m)^[0-9a-f]+\s+T\s+csid680_e004pt_bf_status_observations$",symbols),
            "actual ARM64 observer symbol")
    log=(BUILT/"E004PT-CAMSS-BUILD.log").read_text()
    require("LD [M]  qcom-camss.ko" in log and
            not re.search(r"(?i)(warning:|error:)",log),"corrected W=1 build clean")
    oldlog=(OLD/"E004PT-CAMSS-BUILD.log").read_text()
    require("warning: no previous prototype" in oldlog and
            "LD [M]  qcom-camss.ko" in oldlog,"honest preserved first-attempt evidence")
    original=(ACCEPTED/"camss-csid-680.c").read_text()
    candidate=(BUILT/"camss-csid-680.c").read_text()
    header=(BUILT/"camss-csid.h").read_text()
    inc=(HERE/"camss-csid-e004pt-bf-observer.inc").read_text()
    order=[
        "buf_done_val = readl(csid->base + CSID_BUF_DONE_IRQ_STATUS);",
        "writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);",
        "e004pt_observe_csid1_bf_irq(csid, buf_done_val);",
        "if (buf_done_val && __csid_sp11_front_ipp_mode0(csid))",
        "if (!csid_is_lite(csid))",
        "camss_buf_done(csid->camss, csid->id, i);",
        "writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);",
    ]
    isr=candidate[candidate.index("static irqreturn_t csid_isr"):candidate.index("static void csid_subdev_init",candidate.index("static irqreturn_t csid_isr"))]
    pos=[isr.index(k) for k in order]
    require(pos==sorted(pos),"observer must consume single existing latched/ACKed CSID status")
    original_isr=original[original.index("static irqreturn_t csid_isr"):original.index("static void csid_subdev_init",original.index("static irqreturn_t csid_isr"))]
    for k in (order[0],order[1],order[3],order[5],order[6]):
        require(original_isr.count(k)==isr.count(k)==1,"no original ISR hardware reads ACKs or callbacks altered: "+k)
    require(candidate.count("e004pt_observe_csid1_bf_irq(csid, buf_done_val);")==1,
            "single nonretiring call site")
    require(candidate.count('#include "camss-csid-e004pt-bf-observer.inc"')==1,
            "one isolated source include")
    require("atomic64_set(&csid->x1e_e004pt_bf_observations, 0);" in candidate,
            "observer counter initialized in corrected CSID source")
    require("u64 csid680_e004pt_bf_status_observations(struct csid_device *csid);" in header,
            "missing-prototype warning fixed in separate build")
    # C function body only: no extra ISR hardware reads, IRQ ACK, buffer done,
    # IO mapping, or self-attested DMA predicates. Comments are not code.
    without_comments=re.sub(r"/\*.*?\*/","",inc,flags=re.S)
    forbidden=r"\b(?:readl|writel|camss_buf_done|vfe_buf_done|vb2_buffer_done|dma_unmap|dma_map|complete|free_irq|request_irq)\s*\("
    require(not re.search(forbidden,without_comments),"observer must only record status")
    require("csid->id != 1" in without_comments and
            "csid_is_lite(csid)" in without_comments and
            "(already_latched_buf_done & BIT(7))" in without_comments,
            "exact CSID1 full bit7 only; no frame claim")
    parent=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ps-original-bf-null-matcher-callback-gate-static/RESULT.json").read_text())
    require(not parent["native_rear_ISP_runtime_authorized"] and
            not parent["original_outstanding_matched_pointer_return_has_explicit_nonnull_guard_before_software_callback"],
            "original OEM matcher-null outstanding gate still unresolved")
    proc=subprocess.run(["bash",str(HERE/"run-offline.sh")],capture_output=True,text=True,check=True)
    require(proc.stdout.count("PASS_E004PT_OFFLINE_262144_STATUS_DOMAIN_CASES_32768_BF_OBSERVATIONS_NO_DMA_RETIRE")==2 and
            "E004PT_OFFLINE_GCC_CLANG_ASAN_UBSAN_PASS" in proc.stdout,
            "exact two offline compiler/sanitizer test passes")
    saved=json.loads((HERE/"RESULT.json").read_text())
    require(saved==facts(),"saved source facts may not promote observational status")
    negative=0
    for key in saved:
        mutant=copy.deepcopy(saved)
        val=mutant[key]
        mutant[key]=not val if isinstance(val,bool) else (
           val+1 if isinstance(val,int) else ("INVALID" if isinstance(val,str) else {"invalid":"mutation"}))
        try:
            require(mutant==facts(),"negative "+key)
        except AssertionError:
            negative+=1
        else:
            raise AssertionError("E004PT_NEGATIVE_FAIL_OPEN "+key)
    print("PASS_E004PT_SOURCE_PINNED_ARM64_CAMSS_W1_ZERO_WARNINGS_GCC_CLANG_ASAN_UBSAN_262144_STATUS_CASES_EACH_%d_NEGATIVES_OBSERVER_ONLY_REAR_DENIED_GOLDEN_SAFE"%negative)

if __name__=="__main__":
    main()
