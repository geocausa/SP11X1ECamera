#!/usr/bin/env python3
"""E004ow acceptance: real Linux VFE680 IRQ handler is an unwired stub.

Read-only, SHA-locked same-SP11 accepted CAMSS source and prior E004ov
standalone source. Does not touch kernel/module/camera/Golden.
"""
import copy,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CAMSS=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
SHA={
 "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
 "camss-vfe.c":"98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
 "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
 "camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
}
PARENT="0a5b3325b91368f139889d7099570a16a67bd61e"
def need(ok,reason):
    if not ok:raise AssertionError("E004OW_FAIL_CLOSED "+reason)
def facts():
    return {
      "schema":"sp11-e004ow-accepted-native-VFE680-ISR-stub-and-rear-BF-hardware-status-provider-missing-source-v1",
      "parent_git_revision":PARENT,
      "accepted_same_SP11_Linux_CAMSS_original_source_SHA256":SHA,
      "vfe680_real_kernel_IRQ_handler_name":"vfe_isr",
      "vfe680_registered_hw_ops_ISR_is_vfe_isr":True,
      "camss_vfe_common_requests_real_hardware_irq_through_hw_ops_isr":True,
      "vfe680_ISR_body_only_returns_IRQ_HANDLED":True,
      "vfe680_ISR_reads_ACKs_or_dispatches_VFE_BF_WM16_buffer_completion":False,
      "existing_raw_E003h_epoch0_bus_status1_bit":21,
      "existing_raw_E003h_VIDEO_top_status1_bit":0,
      "existing_raw_E003h_snapshot_poll_static_recipe_is_not_VFE_ISR":True,
      "existing_raw_poll_recipe_hw_ops_or_ISR_caller_verified":False,
      "separate_RT_CDM1_ISR_is_not_VFE_WM16_IRQ_dispatch":True,
      "new_E004ov_generation_guard_included_in_CAMSS_or_current_ISR":False,
      "original_Windows_rear4k_selected_BF_0x0f_active_mode_proven":False,
      "native_Linux_rear_BF_FIFO8_hardware_status_irq_ack_DMA_retirement_proven":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_proven":False,
      "protected_Golden_boot_camera_or_kernel_modified":False,
    }
def strict(x):need(x==facts(),"saved scalar source gate changed")
if __name__=="__main__":
    src={}
    for k,v in SHA.items():
        f=CAMSS/k
        need(hashlib.sha256(f.read_bytes()).hexdigest()==v,"accepted kernel source SHA "+k)
        src[k]=f.read_text()
    v=src["camss-vfe-680.c"];common=src["camss-vfe.c"];c=src["camss.c"]
    # Exact no-op handler is physically the callback selected by vfe_ops_680,
    # and the platform common VFE code requests that function as its IRQ.
    m=re.findall(r"static irqreturn_t vfe_isr\(int irq, void \*dev\)\s*\{([^{}]*)\}",v)
    need(len(m)==1 and m[0].strip()=="return IRQ_HANDLED;","VFE680 registered ISR original exact no-op body")
    need(re.search(r"const struct vfe_hw_ops vfe_ops_680\s*=\s*\{[^}]*\.isr\s*=\s*vfe_isr,",v,re.S) is not None,
         "real VFE680 hardware ops bind stub as ISR")
    need("devm_request_irq(dev, vfe->irq, vfe->res->hw_ops->isr," in common,
         "real kernel VFE IRQ request binding")
    need("vfe680_x1e_raw_irq_recipe __used" in v and
         "Private retention only: no ISR, VFE ops or stream path references it" in v and
         "vfe680_x1e_poll_raw_status1" in v and
         "#define VFE680_X1E_RAW_EPOCH0\tBIT(21)" in v and
         "#define VFE680_X1E_RAW_VIDEO\tBIT(0)" in v,
         "front-only raw polling retained, not ISR")
    need("vfe680_x1e_raw_irq_recipe" not in common and
         "vfe680_x1e_raw_irq_recipe" not in c and
         "vfe680_x1e_raw_irq_recipe" not in src["camss-csid-680.c"],
         "no real VFE ISR or common-code caller of retained recipe")
    need("camss_rtcdm1_isr(int irq, void *data)" in c and
         "devm_request_irq(camss->dev, irq, camss_rtcdm1_isr," in c,
         "separate RTCDM IRQ source distinct from VFE")
    need("rear-stop-ownership.h" not in v and
         "rear-stop-ownership.h" not in common and
         "rear-stop-ownership.h" not in c,
         "E004ov never included by live camera")
    old=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ov-rear-six-group-generation-ownership-offline/RESULT.json").read_text())
    need(old["real_hardware_ISR_generator_or_FIFO_identity_producer_implemented"] is False and
         old["rear_hardware_ISP_runtime_authorized"] is False,
         "prior offline L3 contract still runtime denied")
    j=facts();saved=HERE/"RESULT.json"
    if saved.exists():need(json.loads(saved.read_text())==j,"saved source evidence")
    else:saved.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    muts=(
      ("fake_sha","accepted_same_SP11_Linux_CAMSS_original_source_SHA256",{}),
      ("fake_stub","vfe680_ISR_body_only_returns_IRQ_HANDLED",False),
      ("fake_binding","vfe680_registered_hw_ops_ISR_is_vfe_isr",False),
      ("fake_common","camss_vfe_common_requests_real_hardware_irq_through_hw_ops_isr",False),
      ("fake_hw","vfe680_ISR_reads_ACKs_or_dispatches_VFE_BF_WM16_buffer_completion",True),
      ("fake_poll","existing_raw_E003h_snapshot_poll_static_recipe_is_not_VFE_ISR",False),
      ("fake_epoch","existing_raw_E003h_epoch0_bus_status1_bit",7),
      ("fake_video","existing_raw_E003h_VIDEO_top_status1_bit",7),
      ("fake_active_poll","existing_raw_poll_recipe_hw_ops_or_ISR_caller_verified",True),
      ("fake_RTCDM","separate_RT_CDM1_ISR_is_not_VFE_WM16_IRQ_dispatch",False),
      ("fake_guard","new_E004ov_generation_guard_included_in_CAMSS_or_current_ISR",True),
      ("fake_windows_BF","original_Windows_rear4k_selected_BF_0x0f_active_mode_proven",True),
      ("fake_DMA","native_Linux_rear_BF_FIFO8_hardware_status_irq_ack_DMA_retirement_proven",True),
      ("fake_Linux","native_Linux_rear_processed_hardware_ISP_4k_optical_proven",True),
      ("fake_Golden","protected_Golden_boot_camera_or_kernel_modified",True),
    )
    for name,key,val in muts:
        m=copy.deepcopy(j);m[key]=val
        try:strict(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OW_NEGATIVE_FAILED_OPEN "+name)
    print("PASS_E004OW_4_ACCEPTED_CAMSS_SHA_VFE680_ISR_REGISTERED_STUB_FRONT_POLL_DISTINCT_RTCDM_DISTINCT_%d_NEGATIVES_REAR_BF_RUNTIME_DENIED_GOLDEN_SAFE"%len(muts))
