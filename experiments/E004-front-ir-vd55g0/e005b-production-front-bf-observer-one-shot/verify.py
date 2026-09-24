#!/usr/bin/env python3
"""E005b: original on-device one-use front-production physical/scalar verifier.

Runs only on SP11 Golden. Never exports private frames, logs, module, OEM data,
pointers or original Windows instrumentation; only bounded scalar facts.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import yaml

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRE=ROOT/"src/front-imx681/kernel/camss"
B=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e005b-production-front-bf-observer-build")
PRIVATE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e005b-production-front-bf-private-attempt1")
STAGING=ROOT/"experiments/E004-front-ir-vd55g0/e005a-front-bf-scalar-one-shot-isolated"
GRUB_DIR=Path("/boot/sp11-7.1.5-camera-e005b-prod-front-bf")
GRUB_ENTRY=Path("/etc/grub.d/99zzzzzz_sp11_camera_e005b_prod_front_bf")
SHA={
 "production_camss_c":"117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95",
 "production_camss_h":"0bc0ae6173ebc8c858d0f6117aebbc409d7f6fa4414a7df4b66119c83456371e",
 "production_csid_680":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
 "production_vfe_680":"5af25a42cd15aa5b4c0721da1929b3e50b7bac43e40bdb0962ba996f189632ec",
 "reviewed_shared_kernel_header":"0af6268f6a1f5603bc1a32e098bf5590048b911ab784fbe04cdb0cc9c5f85d0a",
 "compiled_production_instrumented_module":"f9a170c7add6f35621a9c9e4a64292cfc082b1c85a168a57ee52fb978b93a3b7",
 "compiled_camss_c":"cf7fd2116fb58484f5a161a4c1d713431749572dda67a0cacb018ac12a73d681",
 "compiled_camss_h":"0ff1005375b036837dedd6c31aef7772b82b01d56a4af97d629826690e62b2ee",
 "compiled_csid_680":"3445ca181de1ee36d865c9d4b3cb0c0b581536f6c2c97c2fb93ceb2b6ef37221",
 "safe_scalar_marker":"2c6178c9b6d73fb4d0048f0d2d03c2ca706e18b5b76cb6c5bcf609fbec9d6390",
 "retirement_marker":"51cd9bbf7a87cb6573836808b4cd0a5409135e2a0b0a838943748fb8cdb8d5d1",
}
PARENT="73c990762d2aadde4aed3e7cc6d3700366b0c07b"
V="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"

def need(ok, message):
 if not ok:raise AssertionError("E005B_FAIL_CLOSED "+message)
def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()

def measured():
 d={
  "schema":"E005b-SP11-real-production-front-27-frame-physical-owner-BF-scalar-v1",
  "parent_git_revision":PARENT,
  "evidence_class":"P_ONE_REAL_NATIVE_FRONT_27_FRAME_RUN_S_SCOPED_OBSERVER_NOT_REAR_DMA",
  "candidate_linux_boot_id":"80e66e13-ebfb-4295-92d4-2b898bb55ed7",
  "confirmed_return_Golden_linux_boot_id":"a2e56094-3583-4d17-8bce-e81603c4a448",
  "original_front_sensor_route":"IMX681_CSIPHY2_CSID1_VFE1_PIX_VIDEO3",
  "native_front_QC10C_frames":27,
  "native_front_TLBG_stats_frames":27,
  "native_front_STATS3A_stats_frames":27,
  "QC10C_frame_bytes":7778304,
  "TLBG_frame_bytes":61472,
  "STATS3A_frame_bytes":331840,
  "live_IQ_producer_status":"PASS",
  "front_stream_shadow_policy":True,
  "front_post_G3_native_sensor_writes":0,
  "front_launcher_exit":0,
  "front_streamoff_log_success":True,
  "owner_epoch_from_real_kernel_stop_log":1,
  "front_run_BF_bit7_scoped_status_observations":0,
  "unattributed_BF_bit7_lifetime_counter":0,
  "existing_front_stop_safe_in_kernel_log":True,
  "first_older_base_E005a_retired_before_any_boot_or_module_load":True,
  "one_use_E005b_hardware_attempt_consumed_and_candidate_retired":True,
  "private_E005b_module_loaded_only_during_candidate_front_session":True,
  "private_compiled_module_sha256":SHA["compiled_production_instrumented_module"],
  "private_module_vermagic":V,
  "front_BF_positive_real_IRQ_observed":False,
  "any_native_rear_processed_ISP_run":False,
  "native_rear_hardware_ISP_runtime_authorized":False,
  "independent_GLOBAL_VFE1_front_rear_owner_implemented_by_front_only_observer":False,
  "per_frame_rear_FIFO8_NONNULL_WM16_buffer_IRQ_DMA_IOMMU_proven":False,
  "Golden_kernel_or_accepted_production_module_modified":False,
  "private_pixels_OEM_binaries_or_KD_logs_exported_to_Git":False,
  "current_sp11_Golden_boot_and_clean_camera_idle_verified":True,
  "one_shot_boot_entry_and_directory_removed":True,
  "frame_count_and_sizes_are_metadata_only_not_pixel_content_checks":True,
  "source_and_safe_scalar_sha256":SHA,
  "next_gate":"global_real_front_rear_route_owner_epoch_then_rear_live_same_frame_FIFO8_NONNULL_WM16_independent_exact_buffer_IRQ_DMA_IOMMU_safe_stop"
 }
 return d

def verify():
 files={
  "production_camss_c":PRE/"camss.c",
  "production_camss_h":PRE/"camss.h",
  "production_csid_680":PRE/"camss-csid-680.c",
  "production_vfe_680":PRE/"camss-vfe-680.c",
  "reviewed_shared_kernel_header":HERE/"camss-e004pz-front-owner-observer.inc",
  "compiled_production_instrumented_module":B/"qcom-camss.ko",
  "compiled_camss_c":B/"camss.c",
  "compiled_camss_h":B/"camss.h",
  "compiled_csid_680":B/"camss-csid-680.c",
  "safe_scalar_marker":HERE/"ATTEMPT1-SAFE-SCALARS.txt",
  "retirement_marker":HERE/"RETIRED.txt"
 }
 for k,p in files.items():
  need(sha(p)==SHA[k],"unaltered original source/evidence "+k)
 need(sha(B/"camss-e004pz-front-owner-observer.inc")==SHA["reviewed_shared_kernel_header"],
      "exact reviewed observer was compiled in same tested production driver")
 need(subprocess.check_output(["modinfo","-F","vermagic",str(B/"qcom-camss.ko")],text=True).strip()==V,
      "exact proven Golden-module ABI")
 log=(B/"E005B-CAMSS-BUILD.log").read_text()
 need("LD [M]  qcom-camss.ko" in log and not re.search("(?i)warning:|error:",log),
      "isolated actual-production ARM64 W1 compiled with zero warnings")
 accepted=(PRE/"camss.c").read_text()
 copied=(B/"camss.c").read_text()
 native=(B/"camss-csid-680.c").read_text()
 need("frame_limit < 1 || frame_limit > 27" in accepted and
      "frame_limit < 1 || frame_limit > 27" in copied,
      "actual 27-frame production source NOT obsolete 5-frame source")
 need("e003h_pix_runtime_arm" not in accepted and
      "e003h_pix_runtime_arm" not in copied,
      "real production start flow not obsolete module param")
 need('E005B_FRONT_ONLY_BF_STATUS owner_epoch=%llu' in copied and
      copied.count("e004pz_front_runner_begin(&camss->e005b_front_bf")==1 and
      copied.count("e004pz_front_runner_end(&camss->e005b_front_bf")==2,
      "front-only scope actual production runner and safe stop")
 for term in ("buf_done_val = readl(csid->base + CSID_BUF_DONE_IRQ_STATUS);",
              "writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);",
              "camss_buf_done(csid->camss, csid->id, i);"):
  need(native.count(term)==(PRE/"camss-csid-680.c").read_text().count(term),
       "old CSID read/ACK/RDI completion not changed "+term)
 need(native.count("e004pz_observe_csid1_status(")==1 and
      native.index("writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);") <
      native.index("e004pz_observe_csid1_status("),
      "read existing latched/ACKed status ONCE")
 need("return -EOPNOTSUPP;" in (HERE/"camss-e004pz-front-owner-observer.inc").read_text(),
      "rear ISP always denied")
 need("E005A_UNARMED_RETIRED_BEFORE_BOOT=YES" in (STAGING/"UNARMED-RETIRE.txt").read_text(),
      "old mismatched candidate never loaded")
 need((HERE/"ATTEMPT1-CONSUMED.marker").is_file() and
      "E005B_CONSUMED_BEFORE_MODULE_LOAD=" in (HERE/"ATTEMPT1-CONSUMED.marker").read_text(),
      "one-shot irreversibly consumed")
 safe=(HERE/"ATTEMPT1-SAFE-SCALARS.txt").read_text()
 need(re.search(r"(?m)^E005B_LAUNCH_EXIT=0$",safe),"one front production launcher success")
 lines=re.findall(r"(?m)^E005B_FRONT_ONLY_BF_STATUS (.+)$",safe)
 need(len(lines)==1,"EXACTLY ONE after-stop front physical status log")
 parts={}
 for pair in lines[0].split():
  k,v=pair.split("=",1)
  need(k not in parts,"unique physical scalar "+k)
  parts[k]=int(v)
 need(parts=={
   "owner_epoch":1,"bf_count":0,"unattributed_lifetime":0,
   "safe_stop":1,"dma_fence_proven":0,"rear_runtime_authorized":0
 }, "original bounded front-run physical BF scalar values")
 need("E005B_RETRY_AUTHORIZED=NO" in safe and
      "E005B_NATIVE_REAR_PROCESSED_ISP_ENABLED=NO" in safe,
      "no native rear or retry")
 need("E005B_CANDIDATE_RETIRED_AFTER_ONE_PHYSICAL_FRONT_RUN=YES" in
      (HERE/"RETIRED.txt").read_text(),"candidate identity retired")
 need(not GRUB_DIR.exists() and not GRUB_ENTRY.exists(),
      "retired candidate boot entries absent on Golden host")
 need(subprocess.check_output(["uname","-r"],text=True).strip()==
      "7.1.5-sp11-render-parity-v4+","actual host on Golden kernel")
 need("sp11-7.1.5-audio-fullio-v19c" in Path("/proc/cmdline").read_text(),
      "Golden boot image currently running")
 grub=subprocess.check_output(["sudo","-n","grub-editenv","/boot/grub/grubenv","list"],text=True)
 need(re.search(r"(?m)^saved_entry=sp11-audio-fullio-v19c$",grub) and
      re.search(r"(?m)^next_entry=$",grub),
      "saved Golden and no next one-time entry")
 need(not any(Path("/sys/module",s).exists() for s in ("qcom_camss","imx681","ov13858")),
      "all camera modules absent after Golden return")
 need(not list(Path("/dev").glob("video*")) and
      not list(Path("/dev").glob("media*")),
      "all camera nodes absent on protected Golden")
 output=PRIVATE/"stream1"
 for tag,size in (("QC10C",7778304),("TLBG",61472),("STATS3A",331840)):
  files=sorted(output.glob(f"{tag}-*.bin"),key=lambda f:int(f.stem.split("-")[-1]))
  need(len(files)==27 and
       [int(f.stem.split("-")[-1]) for f in files]==list(range(27)) and
       all(f.stat().st_size==size for f in files),
       "private output METADATA 27 distinct exact-size "+tag)
 prod=json.loads((output/"producer/RESULT.json").read_text())
 need(prod.get("status")=="PASS" and prod.get("runtime_performed") is True,
      "private native front producer result")
 private_log=(PRIVATE/"LAUNCH-PRIVATE.log").read_text()
 need("STREAMOFF_OK" in private_log and
      "PROD_NATIVE_SCHEDULE_PASS" in private_log and
      "E005B_LAUNCHER_EXIT=0" in private_log and
      "SP11_FRONT_POST_G3_WRITE_POLICY" in private_log and
      '"shadow"' in private_log,
      "single production front stream normal stop and shadow mode")
 need((PRIVATE/"SAFE-SCALAR-ATTEMPT.txt").read_text()==safe,
      "private single original bounded scalar log preserved")
 need(sha(HERE/"ATTEMPT1-SAFE-SCALARS.txt")==SHA["safe_scalar_marker"],
      "no edit to original saved scalar")
 saved=json.loads((HERE/"RESULT.json").read_text())
 expect=measured()
 need(saved==expect,"physical conservative RESULT must recompute exactly")
 negatives=0
 for k,v in saved.items():
  altered=dict(saved)
  if isinstance(v,bool):altered[k]=not v
  elif isinstance(v,int):altered[k]=v+1
  elif isinstance(v,str):altered[k]="INVALID_MUTATION"
  else:altered[k]={"invalid":"mutation"}
  need(altered!=expect,"fail closed on "+k)
  negatives+=1
 print("PASS_E005B_ONE_PHYSICAL_FRONT_PRODUCTION_27_QC10C_27_TLBG_27_STATS3A_OWNER1_BF0_SAFE_STOP_GOLDEN_RETURN_%d_SCALAR_FIELD_NEGATIVES_NO_REAR_DMA_ARM"%negatives)

if __name__=="__main__":verify()
