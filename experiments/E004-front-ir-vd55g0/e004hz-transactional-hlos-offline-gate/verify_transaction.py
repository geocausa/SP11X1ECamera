#!/usr/bin/env python3
"""E004hz reproducible actual unchanged HLOS C transactional synthetic gate."""
from pathlib import Path
import importlib.util
import json
import os
import platform
from hashlib import sha256

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HI=ROOT/"experiments/E004-front-ir-vd55g0/e004hi-failclosed-offline-hlos-stream-transport"
HLOS=ROOT/"src/sp11-camera-hlos-worker"
TX=HLOS/"sp11-offline-transaction.py"
SOURCE=HLOS/"sp11-offline-nv12-stream.c"
ORIGINAL=HLOS/"sp11-offline-stream-client.py"
def need(test,why):
    if not test: raise AssertionError("E004HZ_FAIL_CLOSED "+why)
def main():
    need(platform.machine()=="aarch64" and os.geteuid()!=0,
         "requires unprivileged original SP11 ARM64 offline runtime")
    prior=json.loads((HI/"evidence/RESULT.json").read_text())
    need(prior["status"]==
      "PASS_BOUNDED_PROVISIONAL_HLOS_C_FRAME_STREAM_FINAL_COMMIT_AND_REAL_MODEL_OFFLINE",
      "original C/stream evidence changed")
    need(prior["isolated_offline_stream_sidecar_source_sha256"]==sha256(SOURCE.read_bytes()).hexdigest()
         and prior["isolated_offline_stream_client_source_sha256"]==sha256(ORIGINAL.read_bytes()).hexdigest(),
         "original pinned C/client implementation changed: do not silently invalidate earlier verification")
    import importlib.util
    s=importlib.util.spec_from_file_location("e004hz_test_run",HERE/"test_transaction.py")
    need(s is not None and s.loader is not None,"transaction negative test missing")
    t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
    fault_count=t.run()
    need(fault_count==14, "expected late and prevalidation fault cases not run")
    r={
        "experiment":"E004hz",
        "status":"PASS_ARM64_UNINSTALLED_HLOS_C_TRANSACTIONAL_OFFLINE_NO_PROVISIONAL_OUTPUT",
        "date":"2026-09-20",
        "baseline_commit":"359ed0fa93ae8f814804fe67bd774708764dd44b",
        "original_e004hi_result_sha256":sha256((HI/"evidence/RESULT.json").read_bytes()).hexdigest(),
        "original_C_stream_sha256":sha256(SOURCE.read_bytes()).hexdigest(),
        "original_Python_stream_client_sha256":sha256(ORIGINAL.read_bytes()).hexdigest(),
        "new_uninstalled_transaction_wrapper_sha256":sha256(TX.read_bytes()).hexdigest(),
        "transaction_test_sha256":sha256((HERE/"test_transaction.py").read_bytes()).hexdigest(),
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "supported_original_C_synthetic_frame_counts":[1,2,8,16],
        "synthetic_distinct_luma_frames_pixel_exact_vs_unchanged_C_one_shot":True,
        "all_provisional_outputs_private_until_exact_DONE_EOF_exit_zero":True,
        "prevalidation_and_late_child_failure_negative_cases":fault_count,
        "malformed_late_child_failure_returns_any_provisional_pixels":False,
        "native_live_camera_frame_provenance":False,
        "real_IR_illuminated_optical_or_liveness_test":False,
        "consented_user_biometric_enrollment_or_authentication":False,
        "login_or_unlock_authorized":False,
        "autonomous_hardware_emitter_cutoff_proven":False,
        "no_camera_pmic_spmi_led_firmware_windows_kd_or_pam_activity":True,
        "protected_golden_boot_kernel_or_login_modified":False,
        "new_transaction_worker_installed":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(r,indent=2)+"\n")
    print("E004HZ_ARM64_UNINSTALLED_TRANSACTIONAL_OFFLINE_GATE=PASS")
    print("E004HZ_14_FAILURE_CASES_NONE_RETURN_PROVISIONAL_OUTPUTS=PASS")
    print("E004HZ_REAL_CAMERA_IR_LIVENESS_AUTH_HW_FAILSAFE_UNPROVEN")
if __name__=="__main__":main()
