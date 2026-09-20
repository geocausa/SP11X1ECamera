#!/usr/bin/env python3
"""Audit bounded original HLOS C batch measurement, no models or camera required."""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HG=ROOT/"experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf"
SOURCE=HERE/"benchmark_batch.py"
TEST=HERE/"test_batch.py"
EXPECTED_NAMES=(
    "single_eight_new_processes_hlos_ms",
    "single_first_public_feature_ready_ms",
    "single_total_eight_public_features_ready_ms",
    "batch_one_process_eight_frames_hlos_ms",
    "batch_first_public_feature_ready_ms",
    "batch_total_eight_public_features_ready_ms",
)
def need(ok,msg):
    if not ok:raise AssertionError("E004HH_SCOPE_FAIL_CLOSED "+msg)

def prior():
    p=HG/"evidence/RESULT.json"
    r=json.loads(p.read_text())
    need(r["status"]==
         "PASS_BOUNDED_ARM64_PUBLIC_ONLY_MAINTAINED_HLOS_C_TO_YUNET_SFACE_CPU_TIMING" and
         r["identical_repeated_input_is_new_capture_or_liveness"] is False and
         r["native_ir_emitter_authorized"] is False and
         r["face_authentication_accuracy_threshold_or_liveness_proven"] is False,
         "previous original public-only ARM64 stage scope changed")
    return sha256(p.read_bytes()).hexdigest()

def validate(r):
    need(r["experiment"]=="E004hh" and
         r["status"]==
         "PASS_ORIGINAL_ARM64_HLOS_C_BATCH8_VS_EIGHT_PROCESS_PUBLIC_MODEL_CADENCE_OFFLINE" and
         r["date"]=="2026-09-20" and
         r["baseline_commit"]=="6d41d77982498c95014e49bbf6895a84b20aa56f" and
         r["arch"]=="aarch64" and r["opencv"]=="4.12.0" and
         r["cpu_threads_per_library"]==1,
         "original CPU benchmark provenance changed")
    need(r["prior_e004hg_result_sha256"]==prior() and
         r["public_visible_light_fixture_sha256"]==
         "ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6" and
         r["original_maintained_hlos_worker_sha256"]==
         sha256((HG.parent.parent.parent/"src/sp11-camera-hlos-worker/sp11-hlos-ir.c").read_bytes()).hexdigest(),
         "original public fixture / unchanged maintained C worker hashes changed")
    hlos=ROOT/"src/sp11-camera-hlos-worker"
    need(r["original_nv12_bridge_sha256"]==
         sha256((hlos/"sp11-offline-nv12-face-bridge.py").read_bytes()).hexdigest() and
         r["original_face_probe_sha256"]==
         sha256((hlos/"sp11-offline-face-probe.py").read_bytes()).hexdigest(),
         "real original model bridge/probe hashes changed")
    need(r["benchmark_source_sha256"]==sha256(SOURCE.read_bytes()).hexdigest() and
         r["negative_test_sha256"]==sha256(TEST.read_bytes()).hexdigest(),
         "benchmark/negative test measurement code drift")
    need(r["original_maintained_hlos_c_batch_frame_limit"]==16 and
         r["benchmark_batch_frames"]==8 and r["warmup_pairs"]==1 and
         r["measured_pairs_alternated_order"]==4 and
         r["total_measured_public_frame_model_extractions"]==64,
         "original original C batch/paired order/count changed")
    for key in (
        "original_single_vs_batch_hlos_output_byte_equal",
        "original_C_batch_rejects_truncated_or_overlong_input_without_partial_output",
        "original_C_batch_writes_nothing_until_all_input_read_and_validated",
        "original_C_batch_withholds_all_output_until_all_frames_processed",
        "repeated_fixture_is_not_new_capture_freshness_or_liveness",
    ):
        need(r[key] is True,"original validated batch restriction changed: "+key)
    for key in (
        "measured_real_camera_or_dark_nir_frame_rate",
        "real_biometric_authentication_or_enrollment_proven",
        "actual_optical_electrical_fault_off_proven",
        "raw_nv12_bgr_public_crop_embedding_or_scores_persisted",
        "native_linux_emitter_or_login_modified",
        "windows_kd_camera_pmic_led_or_golden_modified",
    ):
        need(r[key] is False,"unsupported new camera/biometric/physical claim: "+key)
    timing=r["timing_ms"]
    need(set(timing)==set(EXPECTED_NAMES),"unexpected/missing bounded timing groups")
    for name in EXPECTED_NAMES:
        entry=timing[name]
        need(set(entry)=={"samples","min_ms","median_ms",
                          "p95_nearest_rank_ms","max_ms"} and
             type(entry["samples"]) is int and entry["samples"]==4,
             "four-trial timing sample metadata wrong: "+name)
        ms=[entry[key] for key in
            ("min_ms","median_ms","p95_nearest_rank_ms","max_ms")]
        need(all(type(value) is float and math.isfinite(value) and value>=0
                 for value in ms) and ms==sorted(ms) and ms[-1]==ms[-2],
             "invalid four-pair time distribution: "+name)
    need(timing["single_first_public_feature_ready_ms"]["median_ms"]<
         timing["single_total_eight_public_features_ready_ms"]["median_ms"] and
         timing["batch_one_process_eight_frames_hlos_ms"]["median_ms"]<
         timing["batch_first_public_feature_ready_ms"]["median_ms"]<
         timing["batch_total_eight_public_features_ready_ms"]["median_ms"],
         "batch output barrier or latency order changed")
    before,after=r["testing_python_process_ru_maxrss_kib_before_after"]
    need(type(before) is int and type(after) is int and 0<before<=after,
         "whole-test CPU process RSS metadata invalid")

def main():
    validate(json.loads((HERE/"evidence/RESULT.json").read_text()))
    print("E004HH_ORIGINAL_ARM64_C_BATCH8_VS_EIGHT_PROCESSES_AND_64_REAL_MODEL_TRIALS=PASS")
    print("E004HH_EIGHT_INPUT_BEFORE_FIRST_OUTPUT_AND_NO_PARTIAL_INVALID_BATCH=PASS")
    print("E004HH_PUBLIC_REPEATS_NEVER_NIR_CAMERA_LIVENESS_LOGIN_OR_EMITTER=PASS")

if __name__=="__main__":main()
