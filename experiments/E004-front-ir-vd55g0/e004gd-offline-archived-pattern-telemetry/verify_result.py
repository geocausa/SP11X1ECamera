#!/usr/bin/env python3
"""Verify E004gd offline image-pattern chain; no camera, PMIC or Windows calls."""
from pathlib import Path
from hashlib import sha256
import json
import os
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT = HERE / "evidence/RESULT.json"
SRC = ROOT / "src/sp11-camera-hlos-worker/test-telemetry-integration.py"

def require(value, why):
    if not value:
        raise ValueError("E004GD_VERIFY_FAIL_CLOSED " + why)

def check_output(extra_env=None):
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    run = subprocess.run(["python3", str(SRC)], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=180)
    require(run.returncode == 0, "integration test failed: " +
            run.stderr[-700:] + run.stdout[-700:])
    for text in ("E004GD_ARCHIVED_GENERATED_PATTERN=PASS FRAMES=16",
                 "E004GD_FULL_CHAIN_METRICS=PASS INDEPENDENT_PYTHON_REFERENCE=PASS",
                 "E004GD_LAST_FRAME_CORRUPTION_NO_PARTIAL_OUTPUT=PASS",
                 "E004GD_CAMERA=NO EMITTER=OFF REAL_FACE_IMAGES=NO"):
        require(text in run.stdout, "missing gate " + text)
    return run.stdout

def main():
    result = json.loads(RESULT.read_text())
    require(result["status"] ==
            "PASS_OFFLINE_ARCHIVED_PATTERN_RGB888_TO_HLOS_TO_SIGNAL_METRICS",
            "stage identity")
    require(sha256(SRC.read_bytes()).hexdigest() ==
            result["offline_integration_test_sha256"], "source hash changed")
    for key in ("real_optical_face_image_used",
                "real_face_quality_threshold_validated",
                "face_detection_matching_liveness_or_login_proven",
                "camera_or_pmic_used", "windows_or_kdnet_repeated",
                "native_ir_emitter_activated", "golden_modified",
                "e004fs_independent_optical_cutoff_current_gate_closed"):
        require(result[key] is False, "unverified safety/biometric claim: " + key)
    ordinary = check_output()
    sanitized = check_output({"HLOS_SANITIZE": "1",
                              "ASAN_OPTIONS": "detect_leaks=1:halt_on_error=1",
                              "UBSAN_OPTIONS": "halt_on_error=1"})
    require("E004GD_PATTERN_METRICS=" in ordinary and
            "E004GD_PATTERN_METRICS=" in sanitized, "metrics missing")
    print("E004GD_VERIFIED=PASS NORMAL=PASS ASAN_UBSAN=PASS")
    print("EMITTER=OFF GOLDEN=UNCHANGED REAL_FACE_AUTH=NOT_PROVEN")

if __name__ == "__main__":
    main()
