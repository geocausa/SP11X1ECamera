#!/usr/bin/env python3
"""Offline audit of E004hg ARM64 CPU performance without models or a camera."""
from pathlib import Path
from hashlib import sha256
import json
import math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HLOS=ROOT/"src/sp11-camera-hlos-worker"
CORE=ROOT/"src/sp11-camera-protected-worker"
GR=ROOT/"experiments/E004-front-ir-vd55g0/e004gr-offline-hlos-to-face-model"
FILES=(HLOS/"sp11-hlos-ir.c",
       *(CORE/name for name in
         ("sp11-parity-worker.c","sp11-swabf-reference.c",
          "sp11-swasf-reference.c","sp11-swasf-windows-tuning.c",
          "sp11-swasf-helpers.c","sp11-swasf-c230.c",
          "sp11-swasf-c3e8.c","sp11-swasf-cd90.c")))
BRIDGE=HLOS/"sp11-offline-nv12-face-bridge.py"
PROBE=HLOS/"sp11-offline-face-probe.py"
ASSET_SHA="ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6"
EXPECTED_FIELDS=("hlos_c_process_including_subprocess_start",
                 "strict_nv12_gray_bgr_bridge",
                 "real_yunet_detect_sface_align_extract",
                 "full_sequential_single_frame")

def check(ok,why):
    if not ok:raise AssertionError("E004HG_RESULT_FAIL_CLOSED "+why)

def original_prior():
    p=GR/"evidence/RESULT.json"
    r=json.loads(p.read_text())
    check(r["status"]=="PASS_REAL_ARM64_HLOS_C_FULL_RANGE_NV12_TO_PINNED_YUNET_SFACE_OFFLINE" and
          r["native_sp11_darkness_or_near_ir_real_face_tested"] is False and
          r["face_recognition_accuracy_or_liveness_proven"] is False and
          r["native_emitter_enabled"] is False,
          "previous actual HLOS C/model test was not strictly offline")
    return sha256(p.read_bytes()).hexdigest()

def validate(r):
    check(r["experiment"]=="E004hg" and
          r["status"]=="PASS_BOUNDED_ARM64_PUBLIC_ONLY_MAINTAINED_HLOS_C_TO_YUNET_SFACE_CPU_TIMING" and
          r["date"]=="2026-09-20" and
          r["baseline_commit"]=="e703c2b82840b465ef9c831a7541664a947317f4" and
          r["arch"]=="aarch64" and r["opencv"]=="4.12.0",
          "original bounded ARM64 runtime identity changed")
    check(r["cpu_thread_configuration"]==
          {"OMP_NUM_THREADS":1,"OPENBLAS_NUM_THREADS":1,"opencv_threads":1},
          "original CPU thread bound changed")
    check(r["fixture_kind"]==
          "original_opencv_zoo_public_visible_light_group_photo_one_gray_roi_repeated" and
          r["public_fixture_sha256"]==ASSET_SHA and
          r["warmup_runs"]==2 and
          r["measured_identical_public_fixture_runs"]==8 and
          r["sequential_frame_sample_count"]==8 and
          r["measured_frames_repeated_identical_public_input"] is True,
          "public-only identical frame benchmark scope changed")
    check(r["original_maintained_hlos_c_source_sha256"]==
          {p.name:sha256(p.read_bytes()).hexdigest() for p in FILES} and
          r["original_bridge_source_sha256"]==sha256(BRIDGE.read_bytes()).hexdigest() and
          r["original_real_face_probe_source_sha256"]==sha256(PROBE.read_bytes()).hexdigest() and
          r["previous_e004gr_result_sha256"]==original_prior(),
          "original maintained HLOS/model/bridge provenance changed")
    check(r["script_sha256"]==sha256((HERE/"benchmark_offline.py").read_bytes()).hexdigest() and
          r["negative_test_sha256"]==sha256((HERE/"test_benchmark.py").read_bytes()).hexdigest(),
          "original measurement/checking implementation changed")
    check(type(r["model_initialize_once_ms"]) is float and
          math.isfinite(r["model_initialize_once_ms"]) and
          r["model_initialize_once_ms"]>=0,
          "original one-time model init duration missing")
    check(set(r["measured_ms"])==set(EXPECTED_FIELDS),
          "timing stage fields missing, duplicated or unknown")
    for kind in EXPECTED_FIELDS:
        d=r["measured_ms"][kind]
        check(set(d)=={"samples","minimum_ms","median_ms",
                       "p95_nearest_rank_ms","maximum_ms"} and
              d["samples"]==8,"wrong timing sample count/field for "+kind)
        a=[d[key] for key in ("minimum_ms","median_ms",
                              "p95_nearest_rank_ms","maximum_ms")]
        check(all(type(v) is float and math.isfinite(v) and v>=0 for v in a) and
              a==sorted(a),"nonfinite or unsorted timestamp summary "+kind)
    check(type(r["process_ru_maxrss_kib_before_measured_frames"]) is int and
          type(r["process_ru_maxrss_kib_after_measured_frames"]) is int and
          0<r["process_ru_maxrss_kib_before_measured_frames"]<=
          r["process_ru_maxrss_kib_after_measured_frames"],
          "invalid native process RSS peak")
    for name in ("identical_repeated_input_is_new_capture_or_liveness",
                 "model_weights_or_raw_public_photo_repacked_in_repo",
                 "raw_nv12_bgr_model_features_match_scores_or_identity_logged",
                 "face_authentication_accuracy_threshold_or_liveness_proven",
                 "consented_real_user_enrolled_or_authenticated",
                 "physical_led_current_irradiance_fault_off_proven",
                 "new_windows_kd_camera_pmic_led_or_login_activity",
                 "native_ir_emitter_authorized","golden_modified"):
        check(r[name] is False,"repeated public photo wrongly promoted to biometric/hardware evidence: "+name)

def main():
    result=json.loads((HERE/"evidence/RESULT.json").read_text())
    validate(result)
    print("E004HG_PINNED_REAL_ARM64_8_FRAME_PUBLIC_FIXTURE_CPU_BENCHMARK=PASS")
    print("E004HG_MODEL_ONCE_AND_SEQUENTIAL_TIMINGS_FINITE_BOUNDED=PASS")
    print("E004HG_REPLAYED_PUBLIC_INPUT_NEVER_FRESHNESS_LIVENESS_OR_LOGIN=PASS")

if __name__=="__main__":main()
