#!/usr/bin/env python3
"""Audit the E004hi ORIGINAL ARM64 offline stream result without running a device."""
from pathlib import Path
from hashlib import sha256
import json,math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HLOS=ROOT/"src/sp11-camera-hlos-worker"
CORE=ROOT/"src/sp11-camera-protected-worker"
HH=ROOT/"experiments/E004-front-ir-vd55g0/e004hh-bounded-actual-hlos-batch-throughput"
GR=ROOT/"experiments/E004-front-ir-vd55g0/e004gr-offline-hlos-to-face-model"
MAIN=HLOS/"sp11-hlos-ir.c"
STREAM=HLOS/"sp11-offline-nv12-stream.c"
CLIENT=HLOS/"sp11-offline-stream-client.py"
SOURCE=HERE/"verify_stream.py"
TEST=HERE/"test_stream.py"
CORE_FILES=[CORE/name for name in (
    "sp11-parity-worker.c","sp11-swabf-reference.c",
    "sp11-swasf-reference.c","sp11-swasf-windows-tuning.c",
    "sp11-swasf-helpers.c","sp11-swasf-c230.c",
    "sp11-swasf-c3e8.c","sp11-swasf-cd90.c",
)]

def need(condition,message):
    if not condition:raise AssertionError("E004HI_RESULT_FAIL_CLOSED "+message)

def prior():
    p=HH/"evidence/RESULT.json"
    result=json.loads(p.read_text())
    need(result["status"]==
         "PASS_ORIGINAL_ARM64_HLOS_C_BATCH8_VS_EIGHT_PROCESS_PUBLIC_MODEL_CADENCE_OFFLINE" and
         result["measured_real_camera_or_dark_nir_frame_rate"] is False and
         result["real_biometric_authentication_or_enrollment_proven"] is False and
         result["native_linux_emitter_or_login_modified"] is False,
         "original preceding no-auth batch evidence changed")
    return sha256(p.read_bytes()).hexdigest()

def validate(r):
    need(r["experiment"]=="E004hi" and
         r["status"]==
         "PASS_BOUNDED_PROVISIONAL_HLOS_C_FRAME_STREAM_FINAL_COMMIT_AND_REAL_MODEL_OFFLINE" and
         r["baseline_commit"]=="30128962a778d6f41c8f472408d800004134af72" and
         r["date"]=="2026-09-20" and
         r["arch"]=="aarch64" and r["opencv"]=="4.12.0" and
         r["cpu_threads_per_library"]==1 and
         r["frames_per_stream"]==8,
         "original ARM64 CPU stream runtime/scope changed")
    need(r["original_public_image_sha256"]==
         "ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6" and
         r["prior_e004hh_result_sha256"]==prior() and
         r["original_maintained_hlos_core_source_sha256"]==
         {file.name:sha256(file.read_bytes()).hexdigest() for file in CORE_FILES} and
         r["original_unchanged_single_frame_worker_sha256"]==
         sha256(MAIN.read_bytes()).hexdigest(),
         "original maintained pixel core/source provenance changed")
    need(r["isolated_offline_stream_sidecar_source_sha256"]==
         sha256(STREAM.read_bytes()).hexdigest() and
         r["isolated_offline_stream_client_source_sha256"]==
         sha256(CLIENT.read_bytes()).hexdigest() and
         r["original_full_range_gray_bridge_source_sha256"]==
         sha256((HLOS/"sp11-offline-nv12-face-bridge.py").read_bytes()).hexdigest() and
         r["original_actual_face_probe_source_sha256"]==
         sha256((HLOS/"sp11-offline-face-probe.py").read_bytes()).hexdigest() and
         r["verifier_sha256"]==sha256(SOURCE.read_bytes()).hexdigest() and
         r["negative_test_sha256"]==sha256(TEST.read_bytes()).hexdigest(),
         "original offline stream source/real model/test code changed")
    need(r["original_C_input_first_frame_or_count_negative_cases"]==9 and
         r["stream_client_terminal_fault_negative_cases"]==8 and
         r["stream_c_output_exact_original_maintained_one_frame_bytes"] is True and
         r["actual_yunet_sface_all_provisional_public_stream_frames_128d"] is True,
         "actual original native C parity and fault suite changed")
    for key in (
        "malformed_late_session_can_deliver_prior_provisional_frame",
        "late_session_failure_invalidates_all_previous_provisional_frames",
        "deadline_requires_caller_to_invoke_a_client_method",
        "single_stream_timings_are_bounded_diagnostic_not_camera_fps",
    ):
        need(r[key] is True,"stream provisional failure/host-clock scope changed: "+key)
    for key in (
        "provisional_output_committed_before_exact_DONE_and_child_exit_zero",
        "independent_host_failure_watchdog_proven",
        "real_camera_frame_freshness_near_ir_darkness_or_liveness_proven",
        "real_user_enrollment_match_or_login_authorized",
        "raw_image_nv12_bgr_embedding_match_scores_saved",
        "native_linux_emitter_or_pam_modified",
        "windows_kd_camera_pmic_led_or_golden_modified",
        "actual_optical_current_pulse_autonomous_fault_off_proven",
    ):
        need(r[key] is False,"unsupported authentication/physical claim: "+key)
    ns=[r[k] for k in (
        "one_stream_first_provisional_public_feature_ready_ms",
        "one_stream_last_provisional_public_feature_ready_ms",
        "one_stream_terminal_commit_ready_ms")]
    need(all(type(v) is float and math.isfinite(v) and v>=0 for v in ns)
         and ns==sorted(ns),
         "single diagnostic stream first/last/terminal order changed")

def main():
    validate(json.loads((HERE/"evidence/RESULT.json").read_text()))
    print("E004HI_ORIGINAL_NATIVE_HLOS_C_PROVISIONAL_SESSION_AND_REAL_MODEL=PASS")
    print("E004HI_LATE_FAILURE_NO_DONE_EARLIER_FRAMES_NOT_COMMITTED=PASS")
    print("E004HI_HOST_CLOCK_IS_NOT_AUTONOMOUS_HARDWARE_WATCHDOG=PASS")

if __name__=="__main__":main()
