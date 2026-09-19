#!/usr/bin/env python3
"""E004gr: REAL maintained HLOS C worker -> strict full-range gray -> real YuNet/SFace.

Public visible-light photo or archived generated sensor pattern ONLY. No real
user image, camera, PMIC, LED, biometric authorization, enrollment, or PAM.
"""
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HLOS=ROOT/"src/sp11-camera-hlos-worker"
CORE=ROOT/"src/sp11-camera-protected-worker"
GQ=ROOT/"experiments/E004-front-ir-vd55g0/e004gq-arm64-offline-yunet-sface-probe"
ASSETS=Path(os.getenv("SP11_FACE_TEST_ASSETS","/tmp/sp11-camera-face-20260919"))
GROUP_SHA="ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6"
W,H=644,604
YLEN=W*H
NVLEN=YLEN*3//2
SOURCE=(HLOS/"sp11-hlos-ir.c",
        *(CORE/f for f in ("sp11-parity-worker.c","sp11-swabf-reference.c",
                          "sp11-swasf-reference.c","sp11-swasf-windows-tuning.c",
                          "sp11-swasf-helpers.c","sp11-swasf-c230.c",
                          "sp11-swasf-c3e8.c","sp11-swasf-cd90.c")))
BRIDGE=HLOS/"sp11-offline-nv12-face-bridge.py"
PROBE=HLOS/"sp11-offline-face-probe.py"

def need(test,msg):
    if not test:raise AssertionError("E004GR_FAIL_CLOSED "+msg)

def load(path,label):
    spec=importlib.util.spec_from_file_location(label,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def check_reject(mod,op,why):
    try:op()
    except mod.FrameRejected:pass
    else:raise AssertionError("bad neutral-NV12 frame accepted "+why)

def check_model_reject(mod,op,why):
    try:op()
    except mod.ProbeRejected:pass
    else:raise AssertionError("face probe accepted "+why)

def run_c(binary,bytes_in,good=True):
    p=subprocess.run([str(binary)],input=bytes_in,capture_output=True,timeout=100)
    if good:
        need(p.returncode==0 and len(p.stdout)==NVLEN,
             "real maintained HLOS C pipeline failed or wrong output")
        return p.stdout
    need(p.returncode!=0 and p.stdout==b"",
         "invalid C NV12 produced output")
    return b""

def main():
    import platform
    import cv2
    import numpy as np
    need(platform.machine()=="aarch64" and cv2.__version__=="4.12.0",
         "wrong SP11 ARM64 offline inference runtime")
    full=ASSETS/"largest_selfie.jpg"
    need(full.is_file() and not full.is_symlink() and
         sha256(full.read_bytes()).hexdigest()==GROUP_SHA,
         "public OpenCV Zoo fixture missing or changed")
    bridge=load(BRIDGE,"sp11_fullrange_nv12_bridge")
    probe_module=load(PROBE,"sp11_pinned_yn_sface_probe")
    model=probe_module.OfflineFaceProbe(ASSETS)
    need(bridge.NV12LEN==NVLEN and bridge.W==W and bridge.H==H,
         "neutral NV12 geometry changed")
    # Fail closed on malformed/corrupted frame types and chroma. Strict
    # neutral UV is intrinsic to the existing HLOS pipeline contract.
    blank=bytes([0])*YLEN+bytes([128])*(YLEN//2)
    for val,why in (
        (blank[:-1],"truncated frame"),(blank+b"0","overlong frame"),
        (bytearray(blank),"mutable frame"),(memoryview(blank),"memory view"),
        (None,"no frame"),
        (blank[:YLEN]+bytes([129])+blank[YLEN+1:],"nonneutral chroma"),
    ):
        check_reject(bridge,lambda v=val:bridge.nv12_full_range_gray_to_bgr(v),why)
    # Exact full-range parity: no implicit conversion of Y=16 into black or
    # Y=235 into white, as cv2.COLOR_YUV2BGR_NV12 video-range conversion does.
    ramp=np.arange(YLEN,dtype=np.uint32).astype(np.uint8).tobytes()
    ramp_bgr=bridge.nv12_full_range_gray_to_bgr(
        ramp+bytes([128])*(YLEN//2))
    need(np.array_equal(ramp_bgr[:,:,0],np.frombuffer(ramp,dtype=np.uint8).reshape((H,W))) and
         np.array_equal(ramp_bgr[:,:,0],ramp_bgr[:,:,1]) and
         np.array_equal(ramp_bgr[:,:,1],ramp_bgr[:,:,2]),
         "full-range luma not preserved exactly in all BGR channels")

    group=cv2.imread(str(full),cv2.IMREAD_COLOR)
    need(group is not None and group.shape==(1150,2048,3),"public image changed")
    small=cv2.resize(group,(640,359),interpolation=cv2.INTER_LINEAR)
    # Derive the same exact public-only isolated ROI as E004gq. Do not
    # retain pixels, templates, identity labels or diagnostic match scores.
    coarse=cv2.FaceDetectorYN.create(
        str(ASSETS/"face_detection_yunet_2023mar.onnx"),"",(640,359),
        0.87,0.3,5000)
    _,faces=coarse.detect(small)
    need(faces is not None and len(faces)==6,"public sample detector fixture drift")
    x,y,w,h=(float(z) for z in faces[5,:4])
    cx,cy=x+w/2,y+h/2
    roi=small[max(0,round(cy-1.5*h)):min(359,round(cy+1.5*h)),
              max(0,round(cx-1.5*w)):min(640,round(cx+1.5*w))]
    roi=cv2.resize(roi,(W,H))
    gray=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    public_nv12=gray.tobytes()+bytes([128])*(YLEN//2)
    all_group=cv2.cvtColor(cv2.resize(small,(W,H)),cv2.COLOR_BGR2GRAY)
    group_nv12=all_group.tobytes()+bytes([128])*(YLEN//2)

    with TemporaryDirectory(prefix="e004gr-actual-hlos-c-") as folder:
        exe=Path(folder)/"maintained-hlos"
        build=subprocess.run(
            ["clang","-std=c11","-O2","-Wall","-Wextra","-Werror",
             *(str(p) for p in SOURCE),"-o",str(exe)],
            capture_output=True,text=True,timeout=65)
        need(build.returncode==0,"maintained HLOS C compilation failed "+
             build.stderr[-500:])
        worker_public=run_c(exe,public_nv12)
        need(worker_public!=public_nv12 and
             worker_public[YLEN:]==bytes([128])*(YLEN//2),
             "real HLOS pixel worker did not process neutral public fixture")
        bgr=bridge.nv12_full_range_gray_to_bgr(worker_public)
        need(np.array_equal(bgr[:,:,0],np.frombuffer(
            worker_public[:YLEN],np.uint8).reshape((H,W))),
             "HLOS output luma distorted in model input bridge")
        feature=model.extract_one_face(bgr)
        need(feature.shape==(1,128) and np.isfinite(feature).all(),
             "REAL original HLOS C->real YuNet/SFace feature failed")
        another=model.extract_one_face(
            bridge.nv12_full_range_gray_to_bgr(worker_public))
        need(model.similarity_diagnostic_only(feature,another)>0.999,
             "public same-frame model deterministic test failed")

        out_group=run_c(exe,group_nv12)
        check_model_reject(probe_module,lambda:model.extract_one_face(
            bridge.nv12_full_range_gray_to_bgr(out_group)),
            "full public group image through actual HLOS pipeline")
        out_blank=run_c(exe,blank)
        check_model_reject(probe_module,lambda:model.extract_one_face(
            bridge.nv12_full_range_gray_to_bgr(out_blank)),
            "uniform synthetic no-face image through HLOS")
        run_c(exe,public_nv12[:-1],good=False)
        run_c(exe,public_nv12+b"0",good=False)

    diag=model.diagnostic_result()
    need(all(diag[k] is False for k in (
        "native_ir_emitter_activated","real_sp11_nir_face_capture_validated",
        "face_recognition_accuracy_or_liveness_proven","consented_user_enrolled",
        "login_or_unlock_authorized","autonomous_hardware_cutoff_proven")),
        "face probe granted unauthorized access or IR activation")

    result={
        "experiment":"E004gr",
        "status":"PASS_REAL_ARM64_HLOS_C_FULL_RANGE_NV12_TO_PINNED_YUNET_SFACE_OFFLINE",
        "baseline_commit":"111b1ee409b1b1947796cb2eeb3086d48a636743",
        "arch":"aarch64","opencv":"4.12.0",
        "public_fixture_sha256":GROUP_SHA,
        "bridge_source_sha256":sha256(BRIDGE.read_bytes()).hexdigest(),
        "face_probe_source_sha256":sha256(PROBE.read_bytes()).hexdigest(),
        "test_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "actual_hlos_c_source_sha256":{
            path.name:sha256(path.read_bytes()).hexdigest() for path in SOURCE},
        "neutral_nv12_full_range_luma_equal_in_three_bgr_channels":True,
        "original_hlos_c_processes_public_gray_visible_fixture":True,
        "original_hlos_c_public_single_face_to_real_yunet_sface_128d":True,
        "hardened_no_face_and_multiple_face_after_real_hlos_rejected":True,
        "short_and_long_nv12_worker_inputs_rejected_without_output":True,
        "raw_images_or_embeddings_committed_or_logged":False,
        "native_sp11_darkness_or_near_ir_real_face_tested":False,
        "face_recognition_accuracy_or_liveness_proven":False,
        "real_user_enrolled_or_auth_granted":False,
        "native_emitter_enabled":False,
        "camera_pmic_windows_kd_or_golden_changed":False,
        "physical_emitter_current_irradiance_cutoff_proven":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GR_REAL_MAINTAINED_HLOS_C_TO_MODEL=PASS ARM64=YES SINGLE_PUBLIC_FACE_128D=PASS")
    print("E004GR_FULLRANGE_NV12_Y_EXACT=PASS MULTIFACE_ZERO_FACE_REJECT=PASS")
    print("E004GR_REAL_NATIVE_IR_FACE=NOT_TESTED LIVENESS=NONE LOGIN=OFF EMITTER=OFF")

if __name__=="__main__":
    main()
