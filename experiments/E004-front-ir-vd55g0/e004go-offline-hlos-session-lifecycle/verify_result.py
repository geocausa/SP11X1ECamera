#!/usr/bin/env python3
"""Pin E004go's offline code, repeat state/real-C-metrics tests, no auth/LED."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SRC=ROOT/"src/sp11-camera-hlos-worker/sp11-offline-session-gate.py"
TEST=ROOT/"src/sp11-camera-hlos-worker/test-offline-session-gate.py"
C=ROOT/"src/sp11-camera-hlos-worker/sp11-ir-signal-metrics.c"
RESULT=HERE/"evidence/RESULT.json"

def need(ok,msg):
    if not ok:raise AssertionError("E004GO_VERIFY_FAIL_CLOSED "+msg)

def main():
    a=json.loads(RESULT.read_text())
    need(a["status"]=="PASS_OFFLINE_HLOS_ONE_SHOT_SIGNAL_DIAGNOSTIC_SESSION_FAIL_CLOSED",
         "incorrect stage identity")
    for key,file in (("session_source_sha256",SRC),
                     ("test_source_sha256",TEST),
                     ("real_c_metrics_sha256",C)):
        need(a[key]==sha256(file.read_bytes()).hexdigest(),"changed source "+key)
    for key in ("raw_image_or_face_template_ingested",
                "face_detection_or_matching_or_liveness_proven",
                "face_authentication_or_login_authorized",
                "physical_host_crash_watchdog_or_hardware_led_cutoff_proven",
                "native_ir_emitter_activated","camera_or_pmic_hardware_accessed",
                "previous_windows_kd_or_camera_boot_repeated","golden_modified"):
        need(a[key] is False,"unverified safety/auth claim "+key)
    p=subprocess.run([sys.executable,str(TEST)],cwd=ROOT,capture_output=True,
                     text=True,timeout=140,check=False)
    need(p.returncode==0,"offline test failed: "+p.stdout[-600:]+p.stderr[-600:])
    for marker in ("E004GO_OFFLINE_STATE_AND_JSON_ADVERSARIAL=PASS SEQUENCES=1024",
                   "E004GO_REAL_C_METRICS_16FRAME_SYNTHETIC_SESSION=PASS",
                   "E004GO_CAMERA=NO EMITTER=OFF BIOMETRIC_AUTH=NOT_IMPLEMENTED"):
        need(marker in p.stdout,"missing reproducibility marker "+marker)
    print("E004GO_VERIFIED=PASS STATE_SEQUENCES=1024 REAL_C_SYNTHETIC_16FRAMES=PASS")
    print("CAMERA=NO EMITTER=OFF LOGIN_AUTH=NOT_IMPLEMENTED PHYSICAL_FAULT_OFF=NOT_PROVEN")
if __name__=="__main__":main()
