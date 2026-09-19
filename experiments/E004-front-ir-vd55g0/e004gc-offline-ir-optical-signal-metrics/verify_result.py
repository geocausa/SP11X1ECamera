#!/usr/bin/env python3
"""Recheck E004gc's exact source + offline tests without any hardware access."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = HERE / "evidence" / "RESULT.json"

def require(ok, what):
    if not ok:
        raise ValueError("E004GC_OFFLINE_CHECK_FAILED " + what)

def run(args, env=None):
    proc = subprocess.run(args, cwd=ROOT, env=env, capture_output=True,
                          text=True, timeout=130, check=False)
    require(proc.returncode == 0, "offline regression failed: " + " ".join(args) +
            "\n" + proc.stderr[-1200:] + proc.stdout[-500:])
    return proc.stdout

def main():
    data = json.loads(E.read_text())
    require(data["experiment"] == "E004gc" and
            data["status"] == "PASS_OFFLINE_IR_SIGNAL_METRICS_SYNTHETIC_AND_REGRESSION",
            "result identity/status")
    for key, file in [
        ("source_sha256", ROOT / "src/sp11-camera-hlos-worker/sp11-ir-signal-metrics.c"),
        ("test_sha256", ROOT / "src/sp11-camera-hlos-worker/test-signal-metrics-offline.py"),
    ]:
        require(hashlib.sha256(file.read_bytes()).hexdigest() == data[key],
                "source/test drift " + key)
    for key in ["camera_boot_or_stream_performed", "pmic_read_or_write_performed",
                "ir_emitter_activated", "real_face_matching_tested",
                "authentication_or_login_modified", "golden_modified",
                "independent_electrical_and_optical_emitter_safety_proven"]:
        require(data[key] is False, "unverified unsafe claim " + key)
    test = "src/sp11-camera-hlos-worker/test-signal-metrics-offline.py"
    ordinary = run(["python3", test])
    require("E004GC_INVALID_LENGTH_CHROMA_COUNT_NO_PARTIAL_OUTPUT=PASS" in ordinary,
            "negative test marker")
    env = dict(os.environ, HLOS_SANITIZE="1")
    sanitized = run(["python3", test], env)
    require("E004GC_SYNTHETIC_NV12_METRICS=PASS" in sanitized,
            "sanitizer regression marker")
    hlos = run(["bash", "src/sp11-camera-hlos-worker/test-offline.sh"])
    require("HLOS_FULL_FRAME=PASS" in hlos, "Windows pixel oracle regression")
    bridge = run(["bash", "src/sp11-camera-hlos-worker/test-bridge16-offline.sh"])
    require("HLOS_RGB888_TO_WORKER_16=PASS" in bridge,
            "existing 16-frame archived-pattern regression")
    print("E004GC_VERIFIED=PASS NORMAL=PASS ASAN_UBSAN=PASS HLOS_REGRESSIONS=PASS")
    print("CAMERA=NO PMIC=NO EMITTER=OFF FACE_UNLOCK=NOT_PROVEN")

if __name__ == "__main__":
    main()
