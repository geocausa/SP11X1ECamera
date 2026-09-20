#!/usr/bin/env python3
"""E004ia: actual SP11 ARM64 public-image HLOS transaction -> real models.

Original HLOS C + public OpenCV Zoo image/weights ONLY, temporary /tmp venv.
No camera, emitter, PMIC, SPMI, Windows, firmware, PAM, enrollment, or login.
No raw pixels, embeddings, similarity scores or identified person persisted.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import importlib.util
import json
import os
import platform
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HLOS=ROOT/"src/sp11-camera-hlos-worker"
HI=ROOT/"experiments/E004-front-ir-vd55g0/e004hi-failclosed-offline-hlos-stream-transport"
HZ=ROOT/"experiments/E004-front-ir-vd55g0/e004hz-transactional-hlos-offline-gate"
HG=ROOT/"experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf"
STAGE=HLOS/"sp11-offline-public-commit-diagnostic.py"
ASSETS=Path("/tmp/sp11-camera-face-20260919")
def need(ok,why):
    if not ok:raise AssertionError("E004IA_FAIL_CLOSED "+why)
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p)
    need(bool(s and s.loader),"original source missing")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    return m
def main():
    need(platform.machine()=="aarch64" and os.geteuid()!=0,
         "original SP11 ARM64 non-root only")
    need(os.environ.get("OMP_NUM_THREADS")=="1" and
         os.environ.get("OPENBLAS_NUM_THREADS")=="1",
         "bounded 1-thread model runtime required")
    ia=load(STAGE,"e004ia_pinned_public_demo")
    hi=load(HI/"verify_stream.py","e004ia_original_worker_compile")
    hzr=json.loads((HZ/"evidence/RESULT.json").read_text())
    hir=json.loads((HI/"evidence/RESULT.json").read_text())
    need(hzr["status"]==
      "PASS_ARM64_UNINSTALLED_HLOS_C_TRANSACTIONAL_OFFLINE_NO_PROVISIONAL_OUTPUT"
      and hir["status"]==
      "PASS_BOUNDED_PROVISIONAL_HLOS_C_FRAME_STREAM_FINAL_COMMIT_AND_REAL_MODEL_OFFLINE",
      "prior exact stream/transaction evidence not present")
    need(sha256((HLOS/"sp11-offline-transaction.py").read_bytes()).hexdigest()==
         hzr["new_uninstalled_transaction_wrapper_sha256"]
         and sha256((HLOS/"sp11-offline-nv12-stream.c").read_bytes()).hexdigest()==
         hir["isolated_offline_stream_sidecar_source_sha256"],
         "original native C stream/transaction changed")
    need(sha256((HLOS/"sp11-offline-stream-client.py").read_bytes()).hexdigest()==
         hir["isolated_offline_stream_client_source_sha256"]
         and sha256((HLOS/"sp11-offline-nv12-face-bridge.py").read_bytes()).hexdigest()==
         hir["original_full_range_gray_bridge_source_sha256"]
         and sha256((HLOS/"sp11-offline-face-probe.py").read_bytes()).hexdigest()==
         hir["original_actual_face_probe_source_sha256"],
         "original stream/bridge/real model probe changed")
    for name,digest in ia.face.MODEL_SHA256.items():
        model=ASSETS/name
        need(model.is_file() and not model.is_symlink()
             and sha256(model.read_bytes()).hexdigest()==digest,
             "original pinned public test model missing/changed")
    photo=ASSETS/"largest_selfie.jpg"
    need(photo.is_file() and not photo.is_symlink() and
         sha256(photo.read_bytes()).hexdigest()==ia.hg.GROUP_SHA,
         "original public visible-light demonstration photo changed")
    import cv2
    need(cv2.__version__=="4.12.0","original OpenCV ARM64 runtime drift")
    # E004ia public fixture preparation uses a coarse detector before C;
    # only the *processed frame* model construction and extraction are
    # held until AFTER native C terminal transaction commit.
    with TemporaryDirectory(prefix="e004ia-public-native-") as temp:
        native=hi.compile_stream(Path(temp)/"uninstalled-offline-HLOS-C",ia.hg)
        complete=[]
        for count in (2,8):
            result=ia.run_pinned_public_demo(native,ASSETS,count=count,
                                             max_seconds=70.0)
            need(result["frames_checked"]==count and result["status"]=="complete"
                 and result["processed_frame_feature_inference_only_after_native_C_transaction_commit"] is True,
                 "actual real model did not consume committed C output")
            for key in (
                "temporary_model_features_or_frame_pixels_returned_or_persisted",
                "native_live_camera_frames_validated",
                "near_ir_illuminated_or_darkness_face_tested",
                "face_identity_or_anti_spoofing_proven",
                "real_user_enrolled_or_authenticated",
                "login_or_unlock_authorized",
                "native_ir_emitter_activated",
                "autonomous_hardware_emitter_cutoff_proven"):
                need(result[key] is False,"actual public demo falsely claims "+key)
            complete.append(count)
    test=load(HERE/"test_committed_model.py","e004ia_negative_gate")
    negative=test.run()
    need(negative==11,"negative cases missing")
    result={
      "experiment":"E004ia",
      "status":"PASS_REAL_ARM64_PUBLIC_PHOTO_NATIVE_HLOS_C_TRANSACTION_THEN_YUNET_SFACE_DIAGNOSTIC",
      "date":"2026-09-20",
      "baseline_commit":"34d2b6f9918058fd39b63958c797678029dd9391",
      "original_e004hi_result_sha256":sha256((HI/"evidence/RESULT.json").read_bytes()).hexdigest(),
      "original_e004hz_result_sha256":sha256((HZ/"evidence/RESULT.json").read_bytes()).hexdigest(),
      "original_C_stream_sha256":sha256((HLOS/"sp11-offline-nv12-stream.c").read_bytes()).hexdigest(),
      "original_transaction_source_sha256":sha256((HLOS/"sp11-offline-transaction.py").read_bytes()).hexdigest(),
      "original_bridge_source_sha256":sha256((HLOS/"sp11-offline-nv12-face-bridge.py").read_bytes()).hexdigest(),
      "original_real_face_probe_source_sha256":sha256((HLOS/"sp11-offline-face-probe.py").read_bytes()).hexdigest(),
      "new_uninstalled_public_commit_diagnostic_source_sha256":sha256(STAGE.read_bytes()).hexdigest(),
      "test_source_sha256":sha256((HERE/"test_committed_model.py").read_bytes()).hexdigest(),
      "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
      "pinned_public_photo_sha256":ia.hg.GROUP_SHA,
      "pinned_offline_public_model_sha256":ia.face.MODEL_SHA256,
      "arch":"aarch64","opencv":"4.12.0",
      "library_cpu_threads_capped_at_one":True,
      "original_native_C_then_real_model_committed_public_demo_frame_counts":complete,
      "public_fixture_roi_coarse_face_detection_occurs_before_native_C_transaction":True,
      "processed_frame_probe_instantiated_or_processed_frame_feature_extracted_before_C_commit":False,
      "precommit_and_model_failure_negative_cases":negative,
      "failed_late_native_C_transaction_caused_processed_frame_model_factory_or_inference_calls":False,
      "raw_pixels_images_embeddings_similarity_scores_or_identity_saved_in_git":False,
      "real_nir_sensor_capture_darkness_or_optical_safety_tested":False,
      "real_user_enrolled_or_face_authenticated":False,
      "real_user_login_or_unlock_authorized":False,
      "native_linux_ir_emitter_or_spmi_pmic_firmware_kd_camera_pam_used":False,
      "independent_hardware_emitter_cutoff_proven":False,
      "protected_golden_boot_kernel_login_changed":False,
      "new_pipeline_installed":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004IA_REAL_ARM64_PUBLIC_HLOS_C_TRANSACTION_THEN_YUNET_SFACE=PASS COUNTS=2,8")
    print("E004IA_11_FAILCLOSED_NEGATIVES_ZERO_PRECOMMIT_PROCESSED_FACE_INFERENCE=PASS")
    print("E004IA_NO_REAL_NIR_FACE_AUTH_IR_EMITTER_HARDWARE_FAILSAFE_OR_LOGIN=PASS")
if __name__=="__main__":main()
