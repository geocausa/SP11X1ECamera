#!/usr/bin/env python3
"""Static archive verifier for E004ia. No models, camera or device required."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HLOS=ROOT/"src/sp11-camera-hlos-worker"
HI=ROOT/"experiments/E004-front-ir-vd55g0/e004hi-failclosed-offline-hlos-stream-transport"
HZ=ROOT/"experiments/E004-front-ir-vd55g0/e004hz-transactional-hlos-offline-gate"
def need(ok,msg):
    if not ok:raise AssertionError("E004IA_ARCHIVE_FAIL_CLOSED "+msg)
def main():
    r=json.loads((HERE/"evidence/RESULT.json").read_text())
    need(r["experiment"]=="E004ia" and r["status"]==
      "PASS_REAL_ARM64_PUBLIC_PHOTO_NATIVE_HLOS_C_TRANSACTION_THEN_YUNET_SFACE_DIAGNOSTIC"
      and r["arch"]=="aarch64" and r["opencv"]=="4.12.0"
      and r["baseline_commit"]=="34d2b6f9918058fd39b63958c797678029dd9391"
      and r["date"]=="2026-09-20","experiment identity drift")
    for k,path in (
      ("original_e004hi_result_sha256",HI/"evidence/RESULT.json"),
      ("original_e004hz_result_sha256",HZ/"evidence/RESULT.json"),
      ("original_C_stream_sha256",HLOS/"sp11-offline-nv12-stream.c"),
      ("original_transaction_source_sha256",HLOS/"sp11-offline-transaction.py"),
      ("original_bridge_source_sha256",HLOS/"sp11-offline-nv12-face-bridge.py"),
      ("original_real_face_probe_source_sha256",HLOS/"sp11-offline-face-probe.py"),
      ("new_uninstalled_public_commit_diagnostic_source_sha256",
       HLOS/"sp11-offline-public-commit-diagnostic.py"),
      ("test_source_sha256",HERE/"test_committed_model.py"),
      ("verifier_sha256",HERE/"verify_committed_model.py")):
        need(sha256(path.read_bytes()).hexdigest()==r[k],"source/evidence digest drift: "+k)
    priorhi=json.loads((HI/"evidence/RESULT.json").read_text())
    priorhz=json.loads((HZ/"evidence/RESULT.json").read_text())
    need(r["original_C_stream_sha256"]==
         priorhi["isolated_offline_stream_sidecar_source_sha256"]
         and r["original_transaction_source_sha256"]==
         priorhz["new_uninstalled_transaction_wrapper_sha256"]
         and r["original_bridge_source_sha256"]==
         priorhi["original_full_range_gray_bridge_source_sha256"]
         and r["original_real_face_probe_source_sha256"]==
         priorhi["original_actual_face_probe_source_sha256"],
         "maintained original native C/bridge/face path modified")
    need(r["original_native_C_then_real_model_committed_public_demo_frame_counts"]==[2,8]
         and r["pinned_public_photo_sha256"]==
         "ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6"
         and r["pinned_offline_public_model_sha256"]=={
          "face_detection_yunet_2023mar.onnx":"8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
          "face_recognition_sface_2021dec.onnx":"0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79"},
         "actual pinned public model/photo identity or scope drift")
    need(r["precommit_and_model_failure_negative_cases"]==11
         and r["library_cpu_threads_capped_at_one"] is True
         and r["public_fixture_roi_coarse_face_detection_occurs_before_native_C_transaction"] is True,
         "bounded negative/fixture preparation claims drift")
    for key in (
      "processed_frame_probe_instantiated_or_processed_frame_feature_extracted_before_C_commit",
      "failed_late_native_C_transaction_caused_processed_frame_model_factory_or_inference_calls",
      "raw_pixels_images_embeddings_similarity_scores_or_identity_saved_in_git",
      "real_nir_sensor_capture_darkness_or_optical_safety_tested",
      "real_user_enrolled_or_face_authenticated",
      "real_user_login_or_unlock_authorized",
      "native_linux_ir_emitter_or_spmi_pmic_firmware_kd_camera_pam_used",
      "independent_hardware_emitter_cutoff_proven",
      "protected_golden_boot_kernel_login_changed",
      "new_pipeline_installed"):
        need(r[key] is False,"unsupported hardware/auth/privacy claim: "+key)
    print("E004IA_ARCHIVED_NATIVE_C_PUBLIC_COMMITTED_MODEL_AND_SOURCE_HASHES=PASS")
    print("E004IA_PRECOMMIT_FEATURE_INFERENCE_AND_REAL_AUTH_HARDWARE_CLAIMS_BLOCKED=PASS")
if __name__=="__main__":main()
