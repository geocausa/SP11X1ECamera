#!/usr/bin/env python3
"""E004hg: bounded repeat-public-fixture ARM64 HLOS C -> actual YuNet/SFace costs.

The fixture is a PUBLIC visible-light image; repeated input is NOT new camera
frames, liveness, a user face, an independent identity, or an authentication.
No device/kernel/PMIC/LED/Windows/KD/PAM accesses. Only timing summaries and
source hashes may enter RESULT.json; never save source pixels/features/scores.
"""
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
from statistics import median
import importlib.util
import json
import os
import platform
import resource
import subprocess
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HLOS=ROOT/"src/sp11-camera-hlos-worker"
CORE=ROOT/"src/sp11-camera-protected-worker"
GR=ROOT/"experiments/E004-front-ir-vd55g0/e004gr-offline-hlos-to-face-model"
ASSETS=Path(os.getenv("SP11_FACE_TEST_ASSETS","/tmp/sp11-camera-face-20260919"))
GROUP_SHA="ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6"
W,H=644,604
YLEN=W*H
NVLEN=YLEN*3//2
FRAME_COUNT=8
WARM_COUNT=2
SOURCES=(HLOS/"sp11-hlos-ir.c",
         *(CORE/name for name in
           ("sp11-parity-worker.c","sp11-swabf-reference.c",
            "sp11-swasf-reference.c","sp11-swasf-windows-tuning.c",
            "sp11-swasf-helpers.c","sp11-swasf-c230.c",
            "sp11-swasf-c3e8.c","sp11-swasf-cd90.c")))
BRIDGE=HLOS/"sp11-offline-nv12-face-bridge.py"
PROBE=HLOS/"sp11-offline-face-probe.py"

def need(ok,msg):
    if not ok:raise AssertionError("E004HG_FAIL_CLOSED "+msg)

def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    need(spec is not None and spec.loader is not None,"offline source missing")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def ns_to_ms(ns):
    return round(ns/1000000,3)

def stats(numbers):
    """Include all measured trials, nearest-rank p95; no estimated throughput."""
    need(len(numbers)==FRAME_COUNT and all(type(n) is int and n>=0 for n in numbers),
         "wrong timing sample count")
    ascending=sorted(numbers)
    p95=ascending[(95*len(ascending)+99)//100-1]
    return {"samples":len(numbers),
            "minimum_ms":ns_to_ms(ascending[0]),
            "median_ms":ns_to_ms(median(ascending)),
            "p95_nearest_rank_ms":ns_to_ms(p95),
            "maximum_ms":ns_to_ms(ascending[-1])}

def public_only_nv12(cv2, np):
    image=ASSETS/"largest_selfie.jpg"
    need(image.is_file() and not image.is_symlink() and
         sha256(image.read_bytes()).hexdigest()==GROUP_SHA,
         "official public visible-light demo asset hash changed")
    group=cv2.imread(str(image),cv2.IMREAD_COLOR)
    need(group is not None and group.shape==(1150,2048,3),
         "public demo dimensions changed")
    reduced=cv2.resize(group,(640,359),interpolation=cv2.INTER_LINEAR)
    coarse=cv2.FaceDetectorYN.create(
        str(ASSETS/"face_detection_yunet_2023mar.onnx"),"",
        (640,359),0.87,0.3,5000)
    _,faces=coarse.detect(reduced)
    need(faces is not None and len(faces)==6,
         "public fixture multi-person detector count drift")
    x,y,w,h=(float(v) for v in faces[5,:4])
    cx,cy=x+w/2,y+h/2
    roi=reduced[max(0,round(cy-1.5*h)):min(359,round(cy+1.5*h)),
                max(0,round(cx-1.5*w)):min(640,round(cx+1.5*w))]
    gray=cv2.cvtColor(cv2.resize(roi,(W,H)),cv2.COLOR_BGR2GRAY)
    need(gray.shape==(H,W) and gray.dtype==np.uint8,
         "public fixture grayscale frame is invalid")
    payload=gray.tobytes()+bytes([128])*(YLEN//2)
    need(len(payload)==NVLEN,"wrong public-only NV12 payload size")
    return payload

def compile_worker(folder):
    worker=folder/"original-maintained-hlos-c"
    cmd=["clang","-std=c11","-O2","-Wall","-Wextra","-Werror",
         *(str(source) for source in SOURCES),"-o",str(worker)]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=75)
    need(p.returncode==0 and worker.is_file(),
         "maintained HLOS C compile rejected "+p.stderr[-350:])
    return worker

def real_hlos_once(worker,payload):
    process=subprocess.run([str(worker)],input=payload,capture_output=True,timeout=15)
    need(process.returncode==0 and len(process.stdout)==NVLEN and
         not process.stderr and process.stdout[YLEN:]==bytes([128])*(YLEN//2),
         "actual maintained HLOS C failed or changed its neutral NV12 contract")
    return process.stdout

def main():
    need(platform.machine()=="aarch64" and os.geteuid()!=0,
         "only non-root offline native ARM64 test permitted")
    need(os.getenv("OMP_NUM_THREADS")=="1" and
         os.getenv("OPENBLAS_NUM_THREADS")=="1",
         "explicit bounded CPU thread environment required")
    import cv2
    import numpy as np
    need(cv2.__version__=="4.12.0","pinned ARM64 OpenCV runtime changed")
    cv2.setNumThreads(1)
    need(cv2.getNumThreads()==1,"OpenCV CPU threads not bounded")
    bridge=dynamic(BRIDGE,"e004hg_strict_bridge")
    face=dynamic(PROBE,"e004hg_actual_face_probe")
    need(bridge.W==W and bridge.H==H and bridge.NV12LEN==NVLEN,
         "maintained full-range NV12 input shape changed")
    original_gr=json.loads((GR/"evidence/RESULT.json").read_text())
    need(original_gr["status"]==
         "PASS_REAL_ARM64_HLOS_C_FULL_RANGE_NV12_TO_PINNED_YUNET_SFACE_OFFLINE" and
         original_gr["native_sp11_darkness_or_near_ir_real_face_tested"] is False,
         "prior public-only actual-C integration proof not pinned")
    tload=time.perf_counter_ns()
    model=face.OfflineFaceProbe(ASSETS)
    model_init_ns=time.perf_counter_ns()-tload
    payload=public_only_nv12(cv2,np)
    need(face.OfflineFaceProbe.diagnostic_result()["login_or_unlock_authorized"] is False,
         "face diagnostic suddenly claims authentication")
    with TemporaryDirectory(prefix="e004hg-maintained-hlos-c-") as scratch:
        worker=compile_worker(Path(scratch))
        # Perform distinct warmup outside measured 8 trials.
        for _ in range(WARM_COUNT):
            fresh=real_hlos_once(worker,payload)
            bgr=bridge.nv12_full_range_gray_to_bgr(fresh)
            feature=model.extract_one_face(bgr)
            need(feature.shape==(1,128) and np.isfinite(feature).all(),
                 "real model feature warmup failed")
        memory_before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        samples={"hlos_c_process_including_subprocess_start_ns":[],
                 "strict_nv12_gray_bgr_bridge_ns":[],
                 "real_yunet_detect_sface_align_extract_ns":[],
                 "full_sequential_single_frame_ns":[]}
        original_processed_digest=None
        for _ in range(FRAME_COUNT):
            start=time.perf_counter_ns()
            actual=real_hlos_once(worker,payload)
            split1=time.perf_counter_ns()
            need(actual!=payload,"HLOS C unexpectedly returned input unchanged")
            current=sha256(actual).digest()
            if original_processed_digest is None:original_processed_digest=current
            else:
                need(current==original_processed_digest,
                     "identical public fixture produced nonidentical HLOS output")
            bgr=bridge.nv12_full_range_gray_to_bgr(actual)
            split2=time.perf_counter_ns()
            need(bgr.shape==(H,W,3) and
                 np.array_equal(bgr[:,:,0],np.frombuffer(
                    actual[:YLEN],np.uint8).reshape(H,W)) and
                 np.array_equal(bgr[:,:,0],bgr[:,:,1]) and
                 np.array_equal(bgr[:,:,1],bgr[:,:,2]),
                 "strict full-range HLOS luma not copied into three model channels")
            feature=model.extract_one_face(bgr)
            end=time.perf_counter_ns()
            need(feature.shape==(1,128) and np.isfinite(feature).all(),
                 "actual public-only face model output invalid")
            samples["hlos_c_process_including_subprocess_start_ns"].append(split1-start)
            samples["strict_nv12_gray_bgr_bridge_ns"].append(split2-split1)
            samples["real_yunet_detect_sface_align_extract_ns"].append(end-split2)
            samples["full_sequential_single_frame_ns"].append(end-start)
        memory_after=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result={
        "experiment":"E004hg",
        "status":"PASS_BOUNDED_ARM64_PUBLIC_ONLY_MAINTAINED_HLOS_C_TO_YUNET_SFACE_CPU_TIMING",
        "date":"2026-09-20",
        "baseline_commit":"e703c2b82840b465ef9c831a7541664a947317f4",
        "arch":"aarch64","opencv":"4.12.0",
        "cpu_thread_configuration":{"OMP_NUM_THREADS":1,
                                     "OPENBLAS_NUM_THREADS":1,
                                     "opencv_threads":1},
        "fixture_kind":"original_opencv_zoo_public_visible_light_group_photo_one_gray_roi_repeated",
        "public_fixture_sha256":GROUP_SHA,
        "original_maintained_hlos_c_source_sha256":{
             file.name:sha256(file.read_bytes()).hexdigest() for file in SOURCES},
        "original_bridge_source_sha256":sha256(BRIDGE.read_bytes()).hexdigest(),
        "original_real_face_probe_source_sha256":sha256(PROBE.read_bytes()).hexdigest(),
        "previous_e004gr_result_sha256":sha256((GR/"evidence/RESULT.json").read_bytes()).hexdigest(),
        "warmup_runs":WARM_COUNT,"measured_identical_public_fixture_runs":FRAME_COUNT,
        "model_initialize_once_ms":ns_to_ms(model_init_ns),
        "measured_ms":{name.replace("_ns",""):stats(values) for name,values in samples.items()},
        "process_ru_maxrss_kib_before_measured_frames":memory_before,
        "process_ru_maxrss_kib_after_measured_frames":memory_after,
        "sequential_frame_sample_count":FRAME_COUNT,
        "measured_frames_repeated_identical_public_input":True,
        "identical_repeated_input_is_new_capture_or_liveness":False,
        "model_weights_or_raw_public_photo_repacked_in_repo":False,
        "raw_nv12_bgr_model_features_match_scores_or_identity_logged":False,
        "face_authentication_accuracy_threshold_or_liveness_proven":False,
        "consented_real_user_enrolled_or_authenticated":False,
        "physical_led_current_irradiance_fault_off_proven":False,
        "new_windows_kd_camera_pmic_led_or_login_activity":False,
        "native_ir_emitter_authorized":False,
        "golden_modified":False,
        "script_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_benchmark.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HG_MAINTAINED_HLOS_C_REAL_YUNET_SFACE_PUBLIC_ONLY_8_FRAMES=PASS")
    print("E004HG_MODEL_INIT_MS",result["model_initialize_once_ms"])
    for key,value in result["measured_ms"].items():
        print("E004HG_TIMING",key,"median_ms",value["median_ms"],
              "p95_ms",value["p95_nearest_rank_ms"])
    print("E004HG_NO_FRESHNESS_OR_LIVENESS FROM_REPEATED_PUBLIC_IMAGE=YES")
    print("E004HG_REAL_NIR=NOT_TESTED LOGIN=OFF EMITTER=OFF GOLDEN=UNCHANGED")

if __name__=="__main__":main()
