#!/usr/bin/env python3
"""E004ov offline-only rear stop generation contract acceptance.

Pins the prior compiled-but-runtime-denied six-group candidate and verifies
the proposed standalone source, no integration with production CAMSS.
"""
import hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PARENT="dd37658148802a938e5499b1fb5bf249a154208b"
SOURCES={
 "rear-stop-ownership.h":"065eeac72c2c79ce354ae4e68d48c2c9d792d3718ae675f968262136b1532fbc",
 "test-rear-stop-ownership.c":"6ca9e773c3214e7913d5dab79a924bfbbb76f24d238da03d30c4b4510b21c93b",
 "run-offline.sh":"6f4cafcd2daf50f25da6a3b281c89647d8c9c363aeb0e68c85be53e5c53de4c1",
}
PRIOR=ROOT/"experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/camss-vfe-e004nv-rear-six-group.inc"
PRIOR_SHA="8271758a4aac09532f2e75ce4b46e49261650075f204440f7f051e9ba2f24efb"
KERNEL=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
KERNEL_SOURCES={
 "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
 "camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
 "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
}
EXPECTED=((0x03,0,0x000f),(0x0d,5,0x0030),(0x0e,6,0x0040),(0x10,7,0x0080),(0x0f,8,0x0100),(0x12,9,0x0200))
def need(ok,why):
    if not ok:raise AssertionError("E004OV_FAIL_CLOSED "+why)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def original_groups(old):
    masks={k:int(v,16) for k,v in re.findall(r"#define\s+(VFE680_E004NV_[A-Z0-9_]+_MASK)\s+(0x[0-9a-f]+)U",old)}
    rows=re.findall(r"\{\s*\.event_id\s*=\s*(0x[0-9a-f]+)U,\s*\.fifo_index\s*=\s*(\d+)U,\s*\.wm_mask\s*=\s*(VFE680_E004NV_[A-Z0-9_]+_MASK)\s*\}",old)
    return tuple((int(a,16),int(b),masks[c]) for a,b,c in rows)
def result():
    return {
     "schema":"sp11-e004ov-offline-C11-rear-generation-tagged-six-group-stop-ownership-design-v1",
     "parent_git_revision":PARENT,
     "original_e004nv_compiled_but_unwired_rear_six_group_source_sha256":PRIOR_SHA,
     "original_CAMSS_front_critical_sources_sha256_unchanged":KERNEL_SOURCES,
     "new_offline_source_sha256":SOURCES,
     "six_group_event_FIFO_WM_mask_source_matches_E004nv":True,
     "new_design_evidence_tier":"D_DESIGN_NOT_PHYSICAL_ORIGINAL_WINDOWS_ISA_OR_NATIVE_LINUX_CAMERA_RUNTIME",
     "normal_C11_six_group_completion_permutations":720,
     "normal_C11_test_assertions":62655,
     "ASan_UBSan_C11_six_group_completion_permutations":720,
     "ASan_UBSan_C11_test_assertions":62655,
     "test_rejects_stale_owner_and_frame_generation_queue_identity":True,
     "test_rejects_duplicate_wrong_FIFO_and_unverified_group_evidence":True,
     "stop_retire_requires_all_six_groups_and_six_independent_hardware_predicates":True,
     "e004nv_existing_logical_ACK_has_per_generation_queue_identity":False,
     "real_hardware_ISR_generator_or_FIFO_identity_producer_implemented":False,
     "real_bus_IRQ_and_DMA_completion_proven":False,
     "rear_hardware_ISP_runtime_authorized":False,
     "native_Linux_rear_processed_optical_4k_proven":False,
     "CAMSS_source_module_boot_camera_or_Golden_modified":False,
    }
if __name__=="__main__":
    for name,digest in SOURCES.items():need(sha(HERE/name)==digest,"new source hash "+name)
    need(sha(PRIOR)==PRIOR_SHA,"original E004nv isolated candidate unchanged")
    for name,digest in KERNEL_SOURCES.items():
        need(sha(KERNEL/name)==digest,"existing CAMSS Golden-support source unchanged "+name)
    source=(HERE/"rear-stop-ownership.h").read_text()
    old=PRIOR.read_text()
    need(original_groups(old)==EXPECTED,"E004nv independent original six group mapping")
    now=tuple((int(a,16),int(b),int(c,16)) for a,b,c in re.findall(r"\{\s*(0x[0-9a-f]+),\s*(\d+),\s*(0x[0-9a-f]+)\s*\}",source))
    need(now==EXPECTED,"offline 6 group map identical")
    need(old.count("return -EOPNOTSUPP;")==1 and
         "vfe680_e004nv_rear_runtime_authorization" in old and
         "vfe680_e004nv_rear_frame_ack_group(struct vfe680_e004nu_rear_frame *frame," in old and
         "frame->pending &= ~group->wm_mask;" in old,
         "prior E004nv DENIED and no per-generation identity in existing ACK")
    need(source.count("return -EOPNOTSUPP;")==0,"offline API not false runtime authorization")
    for p in KERNEL.iterdir():
        if p.suffix in (".c",".h"):
            need("rear-stop-ownership.h" not in p.read_text(errors="replace"),"no new CAMSS include")
    old_result=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ou-ife-event-record-type2-not-bf-wm16-retirement-static/RESULT.json").read_text())
    need(old_result["original_IFE_hardware_IRQ_ack_and_per_WM_DMA_retirement_gate_fully_traced"] is False and
         old_result["type_two_software_counter_zero_proves_BF_FIFO8_issued_or_WM16_IRQ_DMA_retired"] is False,
         "do not promote prior original static counter to hardware proof")
    proc=subprocess.run([str(HERE/"run-offline.sh")],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    expected_line="PASS_E004OV_OFFLINE_C11_720_PERMUTATIONS_62655_ASSERTIONS_NO_CAMERA_HARDWARE_NO_RUNTIME_ARM"
    need(proc.stdout.count(expected_line)==2 and
         "PASS_E004OV_NO_SOURCE_HOOK_MODULE_INSTALL_BOOT_CAMERA_OR_GOLDEN_MUTATION" in proc.stdout,
         "native and sanitized test coverage")
    data=result();saved=HERE/"RESULT.json"
    if saved.exists():need(json.loads(saved.read_text())==data,"scalar acceptance changed")
    else:saved.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("PASS_E004OV_6_ORIGINAL_GROUPS_720_ALL_GROUP_PERMUTATIONS_62655_ASSERTIONS_EACH_NORMAL_AND_SANITIZED_GOLDEN_SAFE_RUNTIME_DENIED")
