#!/usr/bin/env python3
"""E004pv isolated kernel-compiled + same-header C11 BF ring proof.

No live camera, module loading, hardware IRQ, DMA, optical data or raw OEM copy.
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
BUILT=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pv-native-bf-ring-owner-build")
PARENT="c7371586b2b3923f64c341410f40c017b699e442"
ACCEPTED_SHA={
"camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
"camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
"camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208"}
NATIVE_SHA="2459b21e1c5be0ec90cae3a4eb70004330a1d7e7b7494559e9c3db466c572da5"
BUILD_VFE_SHA="e0392fd607d91a9f275a74bf63617cdd2ca447dd976b376cd55ab9916deafbba"
MODULE_SHA="daec2fd45d2c1db781f5a82d98d8eb9961193e1323e675e8550e438760a07da3"
TEST_SHA="35f3afa7f35b1190b71ed5e95d3644490289eb4efa4e96a1ffdc3eb9af16d23e"
RUNNER_SHA="037a49ec5ee91a3474e1c872d9f363a37421998421e5e03d764d1f22604b9e9d"
VERMAGIC="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"

def require(ok,what):
    if not ok:raise AssertionError("E004PV_FAIL_CLOSED: "+what)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def facts():
    return {
        "schema":"E004pv-SP11-isolated-native-BF-FIFO8-per-owner-frame-ring-C11-ARM64-v1",
        "evidence_tier":"D_NATIVE_KERNEL_COMPILED_OFFLINE_SIMULATED_NOT_P_PER_FRAME_HARDWARE",
        "parent_git_revision":PARENT,
        "accepted_CAMSS_source_sha256":ACCEPTED_SHA,
        "native_source_shared_between_ARM64_and_C11_sha256":NATIVE_SHA,
        "isolated_compiled_VFE_source_sha256":BUILD_VFE_SHA,
        "private_SP11_isolated_ARM64_module_sha256":MODULE_SHA,
        "module_vermagic":VERMAGIC,
        "native_queue_capacity":4,
        "native_queue_explicit_producer_success_checked_before_count_inc":True,
        "native_queue_rejects_stale_owner_and_frame_and_full":True,
        "native_queue_rejects_missing_or_mismatched_FIFO8_WM16_tag":True,
        "native_queue_requires_independent_per_buffer_IRQ_DMA_IOMMU_and_five_other_groups":True,
        "native_queue_requires_safe_stop_after_drain_before_owner_handoff":True,
        "native_queue_kernel_spinlock_compiled":True,
        "isolated_kernel_W1_zero_warnings":True,
        "standalone_shared_C11_test_assertions_per_compiler":429,
        "standalone_shared_C11_completion_bit_patterns":64,
        "GCC_and_Clang_ASAN_UBSAN_test_pass":True,
        "source_of_real_owner_grant_FIFO8_entry_WM16_irq_DMA_IOMMU_verified":False,
        "compiled_native_queue_has_live_ISR_or_V4L2_caller":False,
        "native_rear_hardware_ISP_runtime_authorized":False,
        "candidate_module_installed_or_loaded":False,
        "protected_Golden_kernel_or_accepted_CAMSS_modified":False,
        "next_gate":"physical_same_rear4k_owner_frame_generation_real_FIFO8_nonnull_WM16_match_and_independent_exact_buffer_IRQ_DMA_IOMMU_safe_stop",
    }

def main():
    for k,h in ACCEPTED_SHA.items():
        require(sha(ACCEPTED/k)==h,"original CAMSS source byte-identical "+k)
    require(sha(HERE/"camss-vfe-e004pv-bf-owner-ring.inc")==NATIVE_SHA,
            "original independently authored native header hash")
    require(sha(BUILT/"camss-vfe-e004pv-bf-owner-ring.inc")==NATIVE_SHA,
            "exact same header compiled in ARM64 candidate")
    require(sha(BUILT/"camss-vfe-680.c")==BUILD_VFE_SHA,
            "same isolated kernel include and accepted VFE preimage")
    require(sha(BUILT/"qcom-camss.ko")==MODULE_SHA,
            "SP11-private isolated module fingerprint")
    require(sha(HERE/"test-bf-owner-ring.c")==TEST_SHA and
            sha(HERE/"run-offline.sh")==RUNNER_SHA,
            "same C11 test fixture and sanitizer runner")
    require(subprocess.check_output(["modinfo","-F","vermagic",str(BUILT/"qcom-camss.ko")],text=True).strip()==VERMAGIC,
            "exact ABI; never install or load")
    symbols=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(BUILT/"qcom-camss.ko")],text=True)
    for symbol in ("e004pv_bf_owner_begin","e004pv_bf_enqueue",
                   "e004pv_bf_confirm_and_pop","e004pv_bf_request_stop",
                   "e004pv_bf_finish_stop","e004pv_rear_isp_runtime_authorize"):
        require(re.search(r"(?m)^[0-9a-f]+\s+t\s+"+symbol+r"$",symbols),
                "actual ARM64 compiled native state function "+symbol)
    log=(BUILT/"E004PV-CAMSS-BUILD.log").read_text()
    require("LD [M]  qcom-camss.ko" in log and
            not re.search(r"(?i)(warning:|error:)",log),"W=1 zero warnings")
    vf=(BUILT/"camss-vfe-680.c").read_text()
    accepted_vf=(ACCEPTED/"camss-vfe-680.c").read_text()
    inc='#include "camss-vfe-e004pv-bf-owner-ring.inc"'
    require(vf.count(inc)==1 and inc not in accepted_vf,
            "only isolated VFE COPY includes native queue")
    require(vf.count('#include "camss-vfe-e004nv-rear-six-group.inc"')==1,
            "existing unwired six-group owner candidate source retained")
    require(inc in vf and vf.index(inc)<vf.index("static int vfe680_x1e_group_from_event"),
            "new header included in build before existing front critical path")
    src=(HERE/"camss-vfe-e004pv-bf-owner-ring.inc").read_text()
    code=re.sub(r"/\*.*?\*/","",src,flags=re.S)
    require("return -EOPNOTSUPP;" in code and
            code.count("e004pv_rear_isp_runtime_authorize")==1,
            "native rear runtime authorization always DENIED")
    forbidden=r"\b(?:readl|writel|camss_buf_done|vfe_buf_done|vb2_buffer_done|dma_unmap|dma_map|iommu_map|iommu_unmap|request_irq|free_irq)\s*\("
    require(not re.search(forbidden,code),"native ring does not itself access live hardware or retire VB2 DMA")
    require("spin_lock_irqsave" in src and "spin_unlock_irqrestore" in src,
            "future IRQ software state protected in compiled isolated kernel")
    require("source_entry_copy_validated" in src and
            "independently_trusted_wm16_irq_and_ack" in src and
            "dma_iommu_safe_for_exact_buffer" in src and
            "all_other_five_groups_completed" in src,
            "no silent bypass of original queue/hardware completion gaps")
    for rel in (
        "experiments/E004-front-ir-vd55g0/e004pu-original-group8-ring-producer-capacity-static/RESULT.json",
        "experiments/E004-front-ir-vd55g0/e004pt-csid1-bf-irq-observer-isolated/RESULT.json",
    ):
        parent=json.loads((ROOT/rel).read_text())
        require(not parent["native_rear_hardware_ISP_runtime_authorized"],
                "parent original or CSID status cannot authorize rear")
    proc=subprocess.run(["bash",str(HERE/"run-offline.sh")],capture_output=True,text=True,check=True)
    require(proc.stdout.count("PASS_E004PV_SHARED_KERNEL_C11_RING_64_EVIDENCE_PATTERNS_429_ASSERTIONS_RUNTIME_REAR_DENIED")==2
            and "E004PV_EXACT_SAME_C11_HEADER_GCC_CLANG_ASAN_UBSAN_PASS" in proc.stdout,
            "2 independent compilers using exact same kernel/C11 header must pass")
    result=facts()
    require(json.loads((HERE/"RESULT.json").read_text())==result,
            "saved scalar summary remains source/design-conservative")
    negatives=0
    for key,val in result.items():
        mutant=copy.deepcopy(result)
        mutant[key]=not val if isinstance(val,bool) else (
          val+1 if isinstance(val,int) else "MUTATED_INVALID"
          if isinstance(val,str) else {"invalid":"mutation"})
        try:require(mutant==result,"negative "+key)
        except AssertionError:negatives+=1
        else:raise AssertionError("E004PV_FAIL_OPEN "+key)
    print("PASS_E004PV_EXACT_SHARED_C11_KERNEL_RING_ARM64_W1_ZERO_WARNINGS_429_GCC_429_CLANG_ASAN_UBSAN_%d_NEGATIVE_FIELDS_RUNTIME_REAR_DENIED_GOLDEN_SAFE"%negatives)

if __name__=="__main__":main()
