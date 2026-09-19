#!/usr/bin/env python3
"""E004gq: run actual OpenCV Zoo detector and embedding network on SP11 ARM64.

The only real-human image is an openly distributed OpenCV Zoo demo group
photo kept in /tmp; no identity labels, authentication, persisted face pixels
or enrollment. Gray-BGR is a *visual* approximation, not native IR imagery.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import os
import platform
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SRC=ROOT/"src/sp11-camera-hlos-worker/sp11-offline-face-probe.py"
ASSETS=Path(os.environ.get("SP11_FACE_TEST_ASSETS","/tmp/sp11-camera-face-20260919"))
PUBLIC_SAMPLE="largest_selfie.jpg"
SAMPLE_SHA="ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6"

def need(ok,why):
    if not ok:raise AssertionError("E004GQ_FAIL_CLOSED "+why)

def load_probe():
    spec=importlib.util.spec_from_file_location("sp11_offline_face_probe",SRC)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def rejects(fn,mod,why):
    try:fn()
    except mod.ProbeRejected:pass
    else:raise AssertionError("unsafe offline input was accepted: "+why)

def main():
    mod=load_probe()
    import cv2
    import numpy as np
    need(cv2.__version__=="4.12.0","unvalidated OpenCV runtime")
    need(platform.machine()=="aarch64","this experiment requires original ARM64 SP11")
    sample=ASSETS/PUBLIC_SAMPLE
    need(sample.is_file() and not sample.is_symlink() and
         mod._sha(sample)==SAMPLE_SHA,"public OpenCV Zoo sample changed")
    # No substitute/random/changed model bytes or linked model asset is accepted.
    with TemporaryDirectory(prefix="e004gq-negative-asset-") as folder:
        wrong=Path(folder)
        (wrong/mod.DETECTOR_FILE).write_bytes(b"not an onnx model")
        (wrong/mod.RECOGNIZER_FILE).write_bytes(b"not an onnx model")
        rejects(lambda:mod.OfflineFaceProbe(wrong),mod,"tampered offline model")
        (wrong/mod.DETECTOR_FILE).unlink()
        (wrong/mod.DETECTOR_FILE).symlink_to(ASSETS/mod.DETECTOR_FILE)
        rejects(lambda:mod.OfflineFaceProbe(wrong),mod,"symlinked offline model")
    detector=mod.OfflineFaceProbe(ASSETS)
    group=cv2.imread(str(sample),cv2.IMREAD_COLOR)
    need(group is not None and group.shape==(1150,2048,3),
         "public group photo dimensions changed")
    group=cv2.resize(group,(640,359),interpolation=cv2.INTER_LINEAR)
    # The full sample must NEVER pass a one-person inference attempt.
    rejects(lambda:detector.extract_one_face(group),mod,"group photo")
    none=np.zeros((604,644,3),np.uint8)
    rejects(lambda:detector.extract_one_face(none),mod,"zero-face neutral sensor-size frame")
    for candidate,why in (
        (none[:,:,0],"mono 2D image"),
        (none.astype(np.float32),"wrong dtype"),
        (np.zeros((2,2,3),np.uint8),"undersized frame"),
        (np.zeros((2049,2049,3),np.uint8),"oversized frame"),
        (np.zeros((160,160,4),np.uint8),"four-channel frame"),
        (None,"missing frame"),
    ):
        rejects(lambda item=candidate:detector.extract_one_face(item),mod,why)
    # Pin a small, isolated face ROI inside the official public group fixture.
    # This is not an identity claim and never represents the actual user.
    detector._detector.setInputSize((640,359))
    _,faces=detector._detector.detect(group)
    need(faces is not None and len(faces)==6,"public multi-face fixture drift")
    x,y,w,h=(float(v) for v in faces[3,:4])
    cx,cy=x+w/2,y+h/2
    left=max(0,round(cx-1.5*w))
    top=max(0,round(cy-1.5*h))
    right=min(group.shape[1],round(cx+1.5*w))
    bottom=min(group.shape[0],round(cy+1.5*h))
    crop=cv2.resize(group[top:bottom,left:right],(320,320))
    need(crop.shape==(320,320,3),"public single-face crop drift")
    # Align and extract the *actual* 128D SFace embedding in memory twice;
    # a self-consistency check is NOT face-recognition accuracy validation.
    feature=detector.extract_one_face(crop)
    again=detector.extract_one_face(crop.copy())
    score=detector.similarity_diagnostic_only(feature,again)
    need(score>0.999,"offline duplicate self-feature inconsistency")
    gray=cv2.cvtColor(cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY),
                      cv2.COLOR_GRAY2BGR)
    # Gray-BGR is still reflected visible light from the public sample,
    # not a real near-IR sensor capture or darkness/liveness evidence.
    grey_feature=detector.extract_one_face(gray)
    need(grey_feature.shape==(1,128) and np.isfinite(grey_feature).all(),
         "neutral visible-light diagnostic feature invalid")
    rejects(lambda:detector.similarity_diagnostic_only(
        np.zeros((1,127),np.float32),feature),mod,"wrong feature shape")
    rejects(lambda:detector.similarity_diagnostic_only(
        np.full((1,128),np.nan,np.float32),feature),mod,"NaN feature")
    diagnostic=detector.diagnostic_result()
    need(all(diagnostic[k] is False for k in (
        "native_ir_emitter_activated","real_sp11_nir_face_capture_validated",
        "face_recognition_accuracy_or_liveness_proven","consented_user_enrolled",
        "login_or_unlock_authorized","autonomous_hardware_cutoff_proven")),
        "prototype falsely authorizes biometric authentication or emitter")
    # Publish only static hashes / sanitized pass counts. No raw image,
    # extracted face region or features/similarity numbers are persisted.
    out={
        "experiment":"E004gq",
        "status":"PASS_REAL_OFFLINE_ARM64_OPENCV_YUNET_SFACE_MODEL_INFERENCE",
        "baseline_commit":"3c43e34b31c7a09ccfae4365bc3d30dc88eb07b5",
        "python_opencv_version":cv2.__version__,
        "cpu_architecture":platform.machine(),
        "yunet_sha256":mod.MODEL_SHA256[mod.DETECTOR_FILE],
        "sface_sha256":mod.MODEL_SHA256[mod.RECOGNIZER_FILE],
        "public_demo_fixture_sha256":SAMPLE_SHA,
        "source_sha256":sha256(SRC.read_bytes()).hexdigest(),
        "test_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "bootstrap_script_sha256":sha256((HERE/"prepare_offline_assets.sh").read_bytes()).hexdigest(),
        "public_group_fixture_multiple_faces_rejected":True,
        "uniform_gray_644x604_zero_faces_rejected":True,
        "public_face_isolated_in_memory_and_128d_features_extracted":True,
        "identical_public_fixture_feature_self_consistency":"PASS_NOT_IDENTITY_VALIDATION",
        "public_visible_gray_bgr_feature_extracted":True,
        "raw_sample_images_or_embeddings_written_in_repo":False,
        "real_sp11_ir_optical_or_darkness_face_image_used":False,
        "actual_user_face_enrolled":False,
        "face_recognition_accuracy_or_liveness_proven":False,
        "login_or_unlock_authorized":False,
        "native_ir_emitter_activated":False,
        "independent_hardware_fault_cutoff_proven":False,
        "golden_modified":False,
        "model_and_public_fixture_cache":"/tmp/sp11-camera-face-20260919 (not tracked)",
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(out,indent=2)+"\n")
    print("E004GQ_ACTUAL_ARM64_YUNET=PASS MULTI_FACE_REJECT=PASS ZERO_FACE_REJECT=PASS")
    print("E004GQ_ACTUAL_ARM64_SFACE_128D=PASS VISIBLE_GRAY_TEST=PASS SELF_CHECK=PASS")
    print("E004GQ_REAL_USER_IR_MATCHING=NOT_TESTED LIVENESS=NOT_TESTED LOGIN=OFF EMITTER=OFF")
if __name__=="__main__":main()
