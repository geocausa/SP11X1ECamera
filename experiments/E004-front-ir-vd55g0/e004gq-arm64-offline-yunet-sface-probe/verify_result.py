#!/usr/bin/env python3
"""Reproduce E004gq's actual offline OpenCV inference, check no auth/safety claim."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SRC=ROOT/"src/sp11-camera-hlos-worker/sp11-offline-face-probe.py"
TEST=HERE/"verify_models.py"
RESULT=HERE/"evidence/RESULT.json"
EXPECTED_STATUS="PASS_REAL_OFFLINE_ARM64_OPENCV_YUNET_SFACE_MODEL_INFERENCE"

def need(ok,why):
    if not ok:raise AssertionError("E004GQ_VERIFY_FAIL_CLOSED "+why)

def check_result():
    need(RESULT.is_file(),"E004gq result not written")
    data=json.loads(RESULT.read_text())
    need(data.get("experiment")=="E004gq" and data.get("status")==EXPECTED_STATUS,
         "experiment identity/status")
    need(data.get("cpu_architecture")=="aarch64" and data.get("python_opencv_version")=="4.12.0",
         "unvalidated CPU / OpenCV version")
    for key,path in (("source_sha256",SRC),("test_sha256",TEST),
                     ("bootstrap_script_sha256",HERE/"prepare_offline_assets.sh")):
        need(data[key]==sha256(path.read_bytes()).hexdigest(),
             "prototype code drift "+key)
    for key in ("raw_sample_images_or_embeddings_written_in_repo",
                "real_sp11_ir_optical_or_darkness_face_image_used",
                "actual_user_face_enrolled",
                "face_recognition_accuracy_or_liveness_proven",
                "login_or_unlock_authorized",
                "native_ir_emitter_activated",
                "independent_hardware_fault_cutoff_proven",
                "golden_modified"):
        need(data[key] is False,"unauthorized claim "+key)
    need(data["public_group_fixture_multiple_faces_rejected"] is True and
         data["uniform_gray_644x604_zero_faces_rejected"] is True and
         data["public_face_isolated_in_memory_and_128d_features_extracted"] is True,
         "actual local ARM64 network execution evidence absent")
    return data

def main():
    check_result()
    run=subprocess.run([sys.executable,str(TEST)],cwd=ROOT,capture_output=True,
                       text=True,timeout=120,check=False)
    need(run.returncode==0,"model inference regression failed: "+
         run.stdout[-500:]+run.stderr[-1200:])
    for token in ("E004GQ_ACTUAL_ARM64_YUNET=PASS",
                  "E004GQ_ACTUAL_ARM64_SFACE_128D=PASS",
                  "E004GQ_REAL_USER_IR_MATCHING=NOT_TESTED"):
        need(token in run.stdout,"expected source inference marker "+token)
    check_result()
    print("E004GQ_VERIFIED=PASS ARM64_REAL_YUNET_SFACE_MODELS=PASS")
    print("NO_USER_FACE=YES NO_IR_CAPTURE=YES NO_LIVENESS=YES NO_LOGIN=YES EMITTER=OFF")

if __name__=="__main__":main()
