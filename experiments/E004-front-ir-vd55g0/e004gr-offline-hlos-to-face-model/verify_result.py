#!/usr/bin/env python3
"""Fail-closed pinned original HLOS C -> YuNet/SFace offline integration verifier."""
from pathlib import Path
from hashlib import sha256
import json
import platform
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RESULT=HERE/"evidence/RESULT.json"
TEST=HERE/"verify_pipeline.py"
BRIDGE=ROOT/"src/sp11-camera-hlos-worker/sp11-offline-nv12-face-bridge.py"
PROBE=ROOT/"src/sp11-camera-hlos-worker/sp11-offline-face-probe.py"

def need(test,why):
    if not test:raise AssertionError("E004GR_VERIFY_FAIL_CLOSED "+why)

def inspect():
    a=json.loads(RESULT.read_text())
    need(a["experiment"]=="E004gr" and
         a["status"]=="PASS_REAL_ARM64_HLOS_C_FULL_RANGE_NV12_TO_PINNED_YUNET_SFACE_OFFLINE",
         "stage identity")
    need(a["arch"]=="aarch64" and a["opencv"]=="4.12.0" and
         platform.machine()=="aarch64","arch and runtime drift")
    for key,path in (("bridge_source_sha256",BRIDGE),
                     ("face_probe_source_sha256",PROBE),
                     ("test_sha256",TEST)):
        need(sha256(path.read_bytes()).hexdigest()==a[key],
             "source code changed "+key)
    c=ROOT/"src/sp11-camera-protected-worker"
    h=ROOT/"src/sp11-camera-hlos-worker"
    required=[h/"sp11-hlos-ir.c",
              *(c/f for f in ("sp11-parity-worker.c","sp11-swabf-reference.c",
                              "sp11-swasf-reference.c","sp11-swasf-windows-tuning.c",
                              "sp11-swasf-helpers.c","sp11-swasf-c230.c",
                              "sp11-swasf-c3e8.c","sp11-swasf-cd90.c"))]
    need(set(a["actual_hlos_c_source_sha256"])==
         {p.name for p in required},"original HLOS worker source set changed")
    for file in required:
        need(sha256(file.read_bytes()).hexdigest()==
             a["actual_hlos_c_source_sha256"][file.name],
             "maintained original HLOS C drift "+file.name)
    for key in (
        "raw_images_or_embeddings_committed_or_logged",
        "native_sp11_darkness_or_near_ir_real_face_tested",
        "face_recognition_accuracy_or_liveness_proven",
        "real_user_enrolled_or_auth_granted",
        "native_emitter_enabled",
        "camera_pmic_windows_kd_or_golden_changed",
        "physical_emitter_current_irradiance_cutoff_proven",
    ):
        need(a[key] is False,"unverified hardware/identity assertion "+key)
    return a

def main():
    inspect()
    p=subprocess.run([sys.executable,str(TEST)],cwd=ROOT,
                     capture_output=True,text=True,timeout=170)
    need(p.returncode==0,"offline real HLOS->model regression failed "+
         p.stdout[-500:]+p.stderr[-800:])
    for token in ("E004GR_REAL_MAINTAINED_HLOS_C_TO_MODEL=PASS",
                  "E004GR_FULLRANGE_NV12_Y_EXACT=PASS",
                  "E004GR_REAL_NATIVE_IR_FACE=NOT_TESTED"):
        need(token in p.stdout,"required integration test assertion absent "+token)
    inspect()
    print("E004GR_VERIFIED=PASS MAINTAINED_HLOS_C_NEUTRAL_NV12_REAL_MODEL_ARM64=PASS")
    print("NATIVE_SP11_IR_FACE=NOT_TESTED LIVENESS=NOT_TESTED AUTH=OFF LED=OFF")
if __name__=="__main__":main()
