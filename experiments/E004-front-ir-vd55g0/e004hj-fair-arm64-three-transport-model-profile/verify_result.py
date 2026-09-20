#!/usr/bin/env python3
"""Audit E004hj same-session three-mode public-only original HLOS/model trial."""
from pathlib import Path
from hashlib import sha256
import json,math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STAGES=ROOT/"experiments/E004-front-ir-vd55g0"
HLOS=ROOT/"src/sp11-camera-hlos-worker"
HG=STAGES/"e004hg-arm64-hlos-yunet-sface-bounded-perf"
HI=STAGES/"e004hi-failclosed-offline-hlos-stream-transport"
EXPECTED_PRIORS={
  "hg":("e004hg-arm64-hlos-yunet-sface-bounded-perf",
        "PASS_BOUNDED_ARM64_PUBLIC_ONLY_MAINTAINED_HLOS_C_TO_YUNET_SFACE_CPU_TIMING"),
  "hh":("e004hh-bounded-actual-hlos-batch-throughput",
        "PASS_ORIGINAL_ARM64_HLOS_C_BATCH8_VS_EIGHT_PROCESS_PUBLIC_MODEL_CADENCE_OFFLINE"),
  "hi":("e004hi-failclosed-offline-hlos-stream-transport",
        "PASS_BOUNDED_PROVISIONAL_HLOS_C_FRAME_STREAM_FINAL_COMMIT_AND_REAL_MODEL_OFFLINE"),
}
MODES=("single","batch","stream")

def need(ok,msg):
    if not ok:raise AssertionError("E004HJ_RESULT_FAIL_CLOSED "+msg)

def prior_hashes():
    hashes={}
    for name,(directory,status) in EXPECTED_PRIORS.items():
        file=STAGES/directory/"evidence/RESULT.json"
        d=json.loads(file.read_text())
        need(d["status"]==status,"original public model/stream prior proof drift "+name)
        hashes[name]=sha256(file.read_bytes()).hexdigest()
    return hashes

def validate(r):
    need(r["experiment"]=="E004hj" and
         r["status"]==
         "PASS_THREE_MODE_SAME_SESSION_REAL_ARM64_HLOS_C_REAL_YUNET_SFACE_LATENCY_ROTATION" and
         r["date"]=="2026-09-20" and
         r["baseline_commit"]=="228d9b882173d55109b1c00acc5fbb6fa90b5468" and
         r["arch"]=="aarch64" and r["opencv"]=="4.12.0" and
         r["OMP_OPENBLAS_OPENCV_THREADS_EACH"]==1,
         "original ARM64 single-thread measurement identity drift")
    need(r["pinned_prior_original_stage_result_sha256"]==prior_hashes() and
         r["original_public_visible_light_fixture_sha256"]==
         "ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6",
         "original public fixture and previous stage results drift")
    hg_src=ROOT/"src/sp11-camera-protected-worker"
    original=[
        hg_src/name for name in (
            "sp11-parity-worker.c","sp11-swabf-reference.c",
            "sp11-swasf-reference.c","sp11-swasf-windows-tuning.c",
            "sp11-swasf-helpers.c","sp11-swasf-c230.c",
            "sp11-swasf-c3e8.c","sp11-swasf-cd90.c",
        )
    ]
    need(r["original_hlos_one_shot_c_source_sha256"]==
         sha256((HLOS/"sp11-hlos-ir.c").read_bytes()).hexdigest() and
         r["original_core_source_sha256"]==
         {f.name:sha256(f.read_bytes()).hexdigest() for f in original} and
         r["uninstalled_offline_stream_c_source_sha256"]==
         sha256((HLOS/"sp11-offline-nv12-stream.c").read_bytes()).hexdigest() and
         r["uninstalled_offline_stream_client_source_sha256"]==
         sha256((HLOS/"sp11-offline-stream-client.py").read_bytes()).hexdigest() and
         r["original_face_probe_source_sha256"]==
         sha256((HLOS/"sp11-offline-face-probe.py").read_bytes()).hexdigest() and
         r["original_nv12_bridge_source_sha256"]==
         sha256((HLOS/"sp11-offline-nv12-face-bridge.py").read_bytes()).hexdigest(),
         "original pixel engine/stream/face model source identity changed")
    need(r["benchmark_source_sha256"]==
         sha256((HERE/"benchmark_three.py").read_bytes()).hexdigest() and
         r["negative_test_sha256"]==
         sha256((HERE/"test_modes.py").read_bytes()).hexdigest(),
         "actual measurement source/protocol checks changed")
    rotation=[[MODES[(cycle+delta)%3] for delta in range(3)] for cycle in range(6)]
    need(r["exact_three_mode_rotation_order"]==rotation and
         r["mode_rotation_measured_rounds"]==6 and
         r["mode_rotation_warmups"]==1 and
         r["original_identical_public_frame_bytes_per_trial"]==8 and
         r["total_measured_original_yunet_sface_public_feature_extractions"]==144,
         "six rotation-balanced actual real model/worker trials drift")
    for key in (
        "all_three_modes_c_output_equal_original_single_frame_bytes",
        "each_stream_session_successful_DONE_and_exit0",
        "stream_earlier_output_was_provisional_until_DONE",
        "n6_nearest_rank_p95_is_observed_max_not_statistical_tail",
        "repeated_same_public_visible_light_frame_is_not_a_fresh_camera_stream",
    ):
        need(r[key] is True,"original provisional/limited session scope drift: "+key)
    for key in (
        "real_sp11_illuminated_nir_or_dark_room_recognition_proven",
        "biometric_accuracy_replay_resistance_liveness_enrollment_login_proven",
        "autonomous_host_or_pmic_fault_off_proven",
        "actual_optical_irradiance_or_emitter_current_proven",
        "native_ir_emitter_or_pam_modified",
        "windows_kd_camera_pmic_led_or_golden_modified",
        "raw_image_nv12_bgr_face_feature_match_score_or_identity_saved",
    ):
        need(r[key] is False,"false native IR/biometric/physical claim: "+key)
    timings=r["timing_ms"]
    need(set(timings)==set(MODES),"timing comparison modes changed")
    for mode in MODES:
        entry=timings[mode]
        need(set(entry)=={"first_feature",
                          "all_eight_features_and_successful_child_exit"},
             "missing first/total paired measurement "+mode)
        for kind,rec in entry.items():
            need(set(rec)=={"samples","min_ms","median_ms",
                            "p95_nearest_rank_ms","max_ms"} and
                 rec["samples"]==6,"wrong n6 CPU measurement "+mode+kind)
            v=[rec[k] for k in ("min_ms","median_ms",
                                "p95_nearest_rank_ms","max_ms")]
            need(all(type(x) is float and math.isfinite(x) and x>=0 for x in v) and
                 v==sorted(v) and v[-1]==v[-2],
                 "invalid four timing aggregates "+mode+kind)
        need(entry["first_feature"]["median_ms"]<=
             entry["all_eight_features_and_successful_child_exit"]["median_ms"],
             "completion measured before first feature "+mode)
    a,b=r["testing_python_process_peak_rss_kib_before_after"]
    need(type(a) is int and type(b) is int and 0<a<=b,
         "wrong total test process RSS")

def main():
    validate(json.loads((HERE/"evidence/RESULT.json").read_text()))
    print("E004HJ_SIX_ROTATION_BALANCED_REAL_ARM64_THREE_MODE_PUBLIC_MODEL_TRIALS=PASS")
    print("E004HJ_ORIGINAL_HLOS_PIXEL_PARITY_STREAM_DONE_ALL_MODES=PASS")
    print("E004HJ_NO_CAMERA_NIR_LIVENESS_AUTH_OR_HARDWARE_WATCHDOG=PASS")

if __name__=="__main__":main()
