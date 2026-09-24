#!/usr/bin/env python3
"""E004pz: verify isolated front-runner-scoped native BF observation.

No module installation, live camera, DMA/IRQ access or hardware completion.
The scope is intentionally NOT a global exclusive front/rear VFE1 owner.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SRC=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
BUILT=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004pz-front-owner-bf-observer-build")
PRE={
 "camss.h":"da2941a9d2afa6250773c682027fc70512e32daa69a9478cb372ecaa74be37c0",
 "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
 "camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
 "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
}
AUDIT={
 "header":"0af6268f6a1f5603bc1a32e098bf5590048b911ab784fbe04cdb0cc9c5f85d0a",
 "c11_test":"b4735d92fff0a7f5a26b35f39cdd3899e364951b2a4b767de6b4f25a3d3eddf2",
 "c11_runner":"4b4589015af4dcd6699e74d9c84a2d625a394943ec193aeadeededa201e3b759",
 "private_ko":"8d0a76762683edbb128a3ec1937db0a372f27f40e87d03be04ee718718419809",
 "compiled_camss_h":"3678649e216eaeb28a11dbfd22c854f7393b268ed8811476e8a3ec4cf589d143",
 "compiled_camss_c":"5664e05e4235eced35f67222e0e48f55609bc9c3e6a707adea38ea39668bea8a",
 "compiled_csid_680":"8090b51f4d7e4fd295bc665c1986e96994161352e649f1628af8ceb47e219c8d",
}
PARENT="82c52a1bdcf5330177662a6678191ce21c3be4d6"
VERMAGIC="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"

def need(v,msg):
 if not v:raise AssertionError("E004PZ_FAIL_CLOSED "+msg)
def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()
def facts():
 return {
  "schema":"E004pz-SP11-front-runner-scoped-BF-bit7-observer-native-isolated-v1",
  "parent_git_revision":PARENT,
  "evidence_tier":"S_ACCEPTED_LINUX_SOURCE_D_ISOLATED_ARM64_COMPILED_C11_TEST_NOT_NEW_P_LIVE",
  "accepted_source_sha256":PRE,
  "isolated_compiled_sha256":AUDIT,
  "private_module_vermagic":VERMAGIC,
  "historical_original_Windows_front_rear_source":"E004py_PHYSICAL_SNAPSHOTS_DIFFERENT_SESSIONS_NOT_NEW_LIVE",
  "exact_shared_kernel_C11_131072_status_route_test_cases_per_compiler":131072,
  "exact_shared_kernel_C11_assertions_per_compiler":131096,
  "offline_GCC_Clang_ASAN_UBSAN_both_pass":True,
  "front_observer_bind_to_existing_custom_runner_graph_validation_before_power":True,
  "front_runner_owner_epoch_monotonic_and_stale_replay_rejected":True,
  "front_runner_unsafe_stop_pins_observer_until_reboot":True,
  "CSID1_ISR_consumes_exact_existing_latched_BUF_DONE_and_owner_ACK":True,
  "additional_CSID_MMIO_read_or_IRQ_ACK_added":False,
  "unrelated_V4L2_paths_proven_excluded_by_this_front_runner_scope":False,
  "global_front_rear_VFE1_owner_proven_implemented":False,
  "live_sensor_owner_generation_or_BF_bit7_observation_newly_observed":False,
  "per_frame_FIFO8_NONNULL_WM16_matching_entry_or_DMA_IOMMU_fence_proven":False,
  "native_rear_hardware_ISP_runtime_authorized":False,
  "actual_front_or_rear_live_video_stream_invoked":False,
  "private_module_installed_or_loaded":False,
  "accepted_CAMSS_or_protected_Golden_modified":False,
  "next_gate":"independently_exclusive_front_rear_VFE1_owner_route_epoch_with_audit_readout_then_rear_per_buffer_FIFO8_NONNULL_WM16_and_IRQ_DMA_IOMMU_safe_stop",
 }
def main():
 for name,want in PRE.items():
  need(sha(SRC/name)==want,"accepted CAMSS file "+name)
 paths={
  "header":HERE/"camss-e004pz-front-owner-observer.inc",
  "c11_test":HERE/"test-front-owner-observer.c",
  "c11_runner":HERE/"run-offline.sh",
  "private_ko":BUILT/"qcom-camss.ko",
  "compiled_camss_h":BUILT/"camss.h",
  "compiled_camss_c":BUILT/"camss.c",
  "compiled_csid_680":BUILT/"camss-csid-680.c",
 }
 for name,want in AUDIT.items():
  need(sha(paths[name])==want,"isolated source/build "+name)
 need(sha(BUILT/"camss-e004pz-front-owner-observer.inc")==AUDIT["header"],
      "exact same tested C11 header compiled in ARM64")
 need(subprocess.check_output(["modinfo","-F","vermagic",str(paths["private_ko"])],text=True).strip()==VERMAGIC,
      "private compiled but not installed Golden-compatible ABI")
 log=(BUILT/"E004PZ-CAMSS-BUILD.log").read_text()
 need("LD [M]  qcom-camss.ko" in log and not re.search(r"(?i)(warning:|error:)",log),
      "ARM64 W1 compiled with zero warnings")
 camss=(BUILT/"camss.c").read_text()
 csid=(BUILT/"camss-csid-680.c").read_text()
 original_csid=(SRC/"camss-csid-680.c").read_text()
 native=(HERE/"camss-e004pz-front-owner-observer.inc").read_text()
 need('#include "camss-e004pz-front-owner-observer.inc"' in (BUILT/"camss.h").read_text(),
      "observer field in isolated CAMSS device")
 need(native.count("e004pz_front_runner_begin")==1 and
      native.count("e004pz_front_runner_end")==1 and
      "return -EOPNOTSUPP;" in native,"front scoped entry/exit and unconditional rear denial")
 runner=camss[camss.index("static int camss_x1e_pix_runner_frames("):
             camss.index("static int camss_x1e_pix_runner_once(")]
 require_order=("ret = camss_x1e_pix_runner_validate(camss, req);",
                "e004pz_front_runner_begin(&camss->e004pz_front_bf, true,",
                "ret = v4l2_pipeline_pm_get(video_entity);",
                "ret = csid680_x1e_front_ipp_enable(csid);")
 locations=[runner.index(x) for x in require_order]
 need(locations==sorted(locations),
      "front observer MUST begin after real graph validation and before power/start")
 need(runner.count("e004pz_front_runner_end(&camss->e004pz_front_bf,")==2,
      "both unsafe stop pin and safe unwind must end observer")
 need("e004pz_front_epoch, false" in runner and
      "e004pz_front_epoch, teardown_safe" in runner,
      "failed hardware unwind cannot clear owner pin")
 isr_beg="static irqreturn_t csid_isr(int irq, void *dev)"
 isr_end="static void csid_subdev_init(struct csid_device *csid)"
 a=csid[csid.index(isr_beg):csid.index(isr_end,csid.index(isr_beg))]
 b=original_csid[original_csid.index(isr_beg):original_csid.index(isr_end,original_csid.index(isr_beg))]
 ordered=("buf_done_val = readl(csid->base + CSID_BUF_DONE_IRQ_STATUS);",
          "writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);",
          "e004pz_observe_csid1_status(",
          "if (buf_done_val && __csid_sp11_front_ipp_mode0(csid))",
          "writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);")
 positions=[a.index(x) for x in ordered]
 need(positions==sorted(positions) and a.count("e004pz_observe_csid1_status(")==1,
      "read existing IRQ word, ACK once, observe then original front/IRQ logic")
 for term in (ordered[0],ordered[1],ordered[3],ordered[4],
              "camss_buf_done(csid->camss, csid->id, i);"):
  need(a.count(term)==b.count(term),
       "preserve original ISR MMIO / callback identity "+term)
 without_comments=re.sub(r"/\*.*?\*/","",native,flags=re.S)
 bad=r"\b(?:readl|writel|camss_buf_done|vfe_buf_done|vb2_buffer_done|dma_unmap|dma_map|iommu_unmap|request_irq|free_irq)\s*\("
 need(not re.search(bad,without_comments),
      "native observer must have no hardware/IRQ ACK/DMA/VB2 operations")
 need("unsafe_stop_pinned" in native and "last_owner_epoch++" in native and
      "exact_front_route_now" in native,
      "runner scope and independent route guard present")
 old=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004py-physical-front-rear-csid1-bf-bit7-discriminator/RESULT.json").read_text())
 need(old["native_rear_hardware_ISP_runtime_authorized"] is False and
      old["front_and_rear_snapshots_are_same_session_or_same_frame"] is False,
      "parent physical evidence cannot be promoted to DMA proof")
 test=subprocess.run(["bash",str(HERE/"run-offline.sh")],capture_output=True,text=True,check=True)
 need(test.stdout.count("PASS_E004PZ_FRONT_RUNNER_ONLY_131072_STATUS_ROUTE_CASES_131096_ASSERTIONS_NO_WM16_DMA_FENCE_REAR_DENIED")==2 and
      "E004PZ_EXACT_SHARED_HEADER_GCC_CLANG_ASAN_UBSAN_PASS" in test.stdout,
      "GCC and Clang sanitized same-header models both pass")
 saved=json.loads((HERE/"RESULT.json").read_text())
 expected=facts()
 need(saved==expected,"saved conservative evidence must exactly match verification facts")
 negative=0
 for key,value in saved.items():
  mutated=copy.deepcopy(saved)
  mutated[key]=not value if isinstance(value,bool) else (
      value+1 if isinstance(value,int) else
      "INVALID" if isinstance(value,str) else {"invalid":"mutation"})
  need(mutated!=expected,"fail closed field "+key)
  negative+=1
 print("PASS_E004PZ_CSID1_FRONT_RUNNER_SCOPED_ALREADY_LATCHED_SINGLE_ACK_ARM64_W1_ZERO_WARNINGS_GCC_CLANG_131096_ASSERTIONS_EACH_%d_FIELD_NEGATIVES_NO_GLOBAL_OWNER_NO_WM16_DMA_REAR_DENIED"%negative)
if __name__=="__main__":main()
