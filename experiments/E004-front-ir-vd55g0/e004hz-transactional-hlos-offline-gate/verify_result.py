#!/usr/bin/env python3
"""E004hz static source/results validator, no devices or ephemeral fixture needed."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HI=ROOT/"experiments/E004-front-ir-vd55g0/e004hi-failclosed-offline-hlos-stream-transport"
HLOS=ROOT/"src/sp11-camera-hlos-worker"
def check(ok,why):
    if not ok:raise AssertionError("E004HZ_ARCHIVE_FAIL_CLOSED "+why)
def main():
    r=json.loads((HERE/"evidence/RESULT.json").read_text())
    check(r["experiment"]=="E004hz" and r["status"]==
          "PASS_ARM64_UNINSTALLED_HLOS_C_TRANSACTIONAL_OFFLINE_NO_PROVISIONAL_OUTPUT",
          "experiment identity")
    prior=(HI/"evidence/RESULT.json").read_bytes()
    check(sha256(prior).hexdigest()==r["original_e004hi_result_sha256"],
          "prior actual C stream evidence drift")
    for key,path in (
        ("original_C_stream_sha256",HLOS/"sp11-offline-nv12-stream.c"),
        ("original_Python_stream_client_sha256",HLOS/"sp11-offline-stream-client.py"),
        ("new_uninstalled_transaction_wrapper_sha256",HLOS/"sp11-offline-transaction.py"),
        ("transaction_test_sha256",HERE/"test_transaction.py"),
        ("verifier_sha256",HERE/"verify_transaction.py")):
        check(sha256(path.read_bytes()).hexdigest()==r[key],key+" source hash drift")
    p=json.loads(prior)
    check(r["original_C_stream_sha256"]==p["isolated_offline_stream_sidecar_source_sha256"]
          and r["original_Python_stream_client_sha256"]==
          p["isolated_offline_stream_client_source_sha256"],
          "original native C and streaming client changed")
    check(r["supported_original_C_synthetic_frame_counts"]==[1,2,8,16]
          and r["prevalidation_and_late_child_failure_negative_cases"]==14
          and r["synthetic_distinct_luma_frames_pixel_exact_vs_unchanged_C_one_shot"] is True
          and r["all_provisional_outputs_private_until_exact_DONE_EOF_exit_zero"] is True
          and r["malformed_late_child_failure_returns_any_provisional_pixels"] is False,
          "transactional test scope/results drift")
    check(r["no_camera_pmic_spmi_led_firmware_windows_kd_or_pam_activity"] is True
          and r["protected_golden_boot_kernel_or_login_modified"] is False
          and r["new_transaction_worker_installed"] is False,
          "hardware/installation scope drift")
    for key in ("native_live_camera_frame_provenance",
                "real_IR_illuminated_optical_or_liveness_test",
                "consented_user_biometric_enrollment_or_authentication",
                "login_or_unlock_authorized",
                "autonomous_hardware_emitter_cutoff_proven"):
        check(r[key] is False,key+" unsupported claim")
    print("E004HZ_TRANSACTIONAL_ORIGINAL_C_PIXEL_PARITY_AND_LATE_FAULT=PASS")
    print("E004HZ_ORIGINAL_SOURCE_HASHES_SAFE_STATE_NO_AUTH=PASS")
if __name__=="__main__":main()
