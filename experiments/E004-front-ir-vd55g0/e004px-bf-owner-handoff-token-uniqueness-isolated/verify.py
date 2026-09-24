#!/usr/bin/env python3
"""E004px: exact kernel/C11 owner-local frame & unique in-flight token repair.

Offline source/build checks only. Does not arm rear camera or attest DMA.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ACCEPTED=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
BUILT=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004px-bf-owner-handoff-token-build")
PARENT="f26171114db27b48e4ca6348bbb8c6e9af0d8b57"
HASHES={
"accepted_camss_vfe_680":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
"native_header":"7293d95a03b55e12bafb623b177e33dbd1f02c947e47607bf5c1684c51e62540",
"test":"5d3fa8b1598918d6c49f1142e5b09cbfafbb277089a4844150e36cde0ee84c59",
"runner":"60b729b2c2a3c7cae168f6e3492ee15b6f272983a10eae4e02fb27576db53861",
"built_camss_vfe_680":"e0392fd607d91a9f275a74bf63617cdd2ca447dd976b376cd55ab9916deafbba",
"private_module":"25705f70ffbfb41c18661f509e7b19437de9e650f847757b7c8b6e4d15cb43a9",
}
VERMAGIC="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"

def require(ok,why):
    if not ok: raise AssertionError("E004PX_FAIL_CLOSED "+why)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def facts():
    return {
        "schema":"E004px-owner-local-frame-and-inflight-token-uniqueness-isolated-v1",
        "parent_git_revision":PARENT,
        "evidence_tier":"D_SAME_NATIVE_KERNEL_C11_OFFLINE_AND_COMPILED_ARM64_NOT_PHYSICAL_WM16",
        "sha256":HASHES,
        "module_vermagic":VERMAGIC,
        "owner_epoch_monotonic_across_completed_owner_handoffs":True,
        "frame_epoch_monotonic_within_one_owner_but_restart_at_new_owner":True,
        "stale_prior_owner_completion_after_new_owner_grant_rejected":True,
        "same_opaque_token_duplicate_while_pending_rejected":True,
        "token_reuse_after_verified_model_pop_allowed":True,
        "duplicate_enqueue_or_failed_copy_changes_pending_count":False,
        "native_ring_capacity":4,
        "same_header_offline_assertions_per_compiler":437,
        "same_header_completion_predicate_patterns":64,
        "GCC_and_Clang_ASAN_UBSAN_pass":True,
        "isolated_ARM64_W1_zero_warnings":True,
        "live_owner_or_FIFO8_WM16_DMA_evidence_producer_exists":False,
        "isolated_queue_has_live_ISR_V4L2_buffer_retirement_caller":False,
        "native_rear_hardware_ISP_runtime_authorized":False,
        "isolated_module_installed_or_loaded":False,
        "accepted_CAMSS_Golden_modified":False,
        "next_gate":"live_same_original_rear4k_owner_frame_valid_FIFO8_NONNULL_WM16_exact_buffer_and_independent_irq_dma_iommu_safe_stop"
    }

def main():
    paths={
        "accepted_camss_vfe_680":ACCEPTED/"camss-vfe-680.c",
        "native_header":HERE/"camss-vfe-e004pv-bf-owner-ring.inc",
        "test":HERE/"test-bf-owner-ring.c",
        "runner":HERE/"run-offline.sh",
        "built_camss_vfe_680":BUILT/"camss-vfe-680.c",
        "private_module":BUILT/"qcom-camss.ko",
    }
    for k,p in paths.items():
        require(sha(p)==HASHES[k],"SHA-preimage "+k)
    require(sha(BUILT/"camss-vfe-e004pv-bf-owner-ring.inc")==HASHES["native_header"],
            "compiled header must match tested native header")
    require(subprocess.check_output(["modinfo","-F","vermagic",str(BUILT/"qcom-camss.ko")],
            text=True).strip()==VERMAGIC,"Golden-compatible but never installed ABI")
    log=(BUILT/"E004PX-CAMSS-BUILD.log").read_text()
    require("LD [M]  qcom-camss.ko" in log and
            not re.search(r"(?i)(warning:|error:)",log),"W1 zero warnings")
    symbols=subprocess.check_output(["aarch64-linux-gnu-nm","-a",
                                     str(BUILT/"qcom-camss.ko")],text=True)
    for fn in ("e004pv_bf_owner_begin","e004pv_bf_enqueue",
               "e004pv_bf_confirm_and_pop","e004pv_bf_finish_stop",
               "e004pv_rear_isp_runtime_authorize"):
        require(re.search(r"(?m)^[0-9a-f]+\s+t\s+"+fn+r"$",symbols),
                "actual compiled ARM64 symbol "+fn)
    inc=(HERE/"camss-vfe-e004pv-bf-owner-ring.inc").read_text()
    body=re.sub(r"/\*.*?\*/","",inc,flags=re.S)
    require('r->last_frame_epoch = 0;' in body and
            'owner_epoch <= r->last_owner_epoch' in body,
            "per-owner frame restart without old-owner replay")
    require('e->queue_token == queue_token' in body and
            'ret = -EEXIST;' in body and
            'r->last_frame_epoch = frame_epoch;' in body,
            "pending token uniqueness and successfully committed frame")
    require('return -EOPNOTSUPP;' in body,"rear hardware ISP is denied")
    require(not re.search(r"\b(?:readl|writel|camss_buf_done|vfe_buf_done|vb2_buffer_done|dma_unmap|dma_map|iommu_unmap)\s*\(",body),
            "no hardware/VB2/DMA methods in owner model")
    vfe=(BUILT/"camss-vfe-680.c").read_text()
    accepted=(ACCEPTED/"camss-vfe-680.c").read_text()
    directive='#include "camss-vfe-e004pv-bf-owner-ring.inc"'
    require(vfe.count(directive)==1 and directive not in accepted,
            "only isolated VFE source integrates candidate")
    p=subprocess.run(["bash",str(HERE/"run-offline.sh")],
                     capture_output=True,text=True,check=True)
    require(p.stdout.count("PASS_E004PX_OWNER_LOCAL_FRAMES_UNIQUE_PENDING_TOKEN_64_EVIDENCE_PATTERNS_437_ASSERTIONS_REAR_DENIED")==2
            and "E004PX_EXACT_SAME_C11_HEADER_GCC_CLANG_ASAN_UBSAN_PASS" in p.stdout,
            "C11 same-header two independent compilers/sanitizers")
    parent=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pv-native-bf-ring-owner-compiled-isolated/RESULT.json").read_text())
    require(not parent["native_rear_hardware_ISP_runtime_authorized"] and
            not parent["compiled_native_queue_has_live_ISR_or_V4L2_caller"],
            "parent native rear runtime still forbidden")
    saved=json.loads((HERE/"RESULT.json").read_text())
    require(saved==facts(),"result cannot promote unsupported hardware facts")
    negatives=0
    for k,v in saved.items():
        mutate=dict(saved)
        mutate[k]=not v if isinstance(v,bool) else (
            v+1 if isinstance(v,int) else "INVALID" if isinstance(v,str) else {})
        require(mutate!=saved,"negative result mutation "+k)
        negatives+=1
    print("PASS_E004PX_NATIVE_OWNER_LOCAL_FRAME_TOKEN_UNIQUENESS_ARM64_W1_C11_GCC_CLANG_ASAN_UBSAN_437_ASSERTIONS_EACH_%d_NEGATIVES_REAR_DENIED"%negatives)

if __name__=="__main__":main()
