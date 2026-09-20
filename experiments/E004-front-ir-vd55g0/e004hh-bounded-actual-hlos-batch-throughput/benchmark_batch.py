#!/usr/bin/env python3
"""E004hh: compare actual maintained HLOS C --frames 8 batch against eight starts.

No new worker, no devices, no facial enrollment, no user or IR imagery.
The same public visible-light sample repeats; eight-frame batch waits until
ALL eight inputs are validated/processed before ANY image output is returned.
All original model/image pixels/features are RAM-only; timing metadata only.
"""
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import platform
import resource
import subprocess
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HG=ROOT/"experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf"
GR=ROOT/"experiments/E004-front-ir-vd55g0/e004gr-offline-hlos-to-face-model"
N=8
TRIALS=4
WARM=1

def need(ok,reason):
    if not ok:raise AssertionError("E004HH_FAIL_CLOSED "+reason)

def import_file(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    need(spec is not None and spec.loader is not None,"original code unavailable")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def timer_summary(values):
    need(len(values)==TRIALS and all(type(v) is int and v>=0 for v in values),
         "invalid bounded original per-trial timings")
    sorted_values=sorted(values)
    return {
        "samples":len(values),
        "min_ms":round(sorted_values[0]/1e6,3),
        "median_ms":round((sorted_values[1]+sorted_values[2])/2e6,3),
        "p95_nearest_rank_ms":round(sorted_values[-1]/1e6,3),
        "max_ms":round(sorted_values[-1]/1e6,3),
    }

def run_batch(worker,payload,frame_len,frame_y):
    """One unmodified original C program --frames 8; reject any partial output."""
    expected=len(payload)*N
    inp=payload*N
    p=subprocess.run([str(worker),"--frames",str(N)],input=inp,
                     capture_output=True,timeout=70)
    need(p.returncode==0 and len(p.stdout)==expected,
         "original maintained C --frames 8 failed or truncated")
    parts=tuple(p.stdout[i*frame_len:(i+1)*frame_len] for i in range(N))
    need(len(parts)==N and
         all(len(p)==frame_len and p[frame_y:]==bytes([128])*(frame_len-frame_y)
             for p in parts),"original C batch output format invalid")
    need(all(p==parts[0] for p in parts),
         "eight identical public inputs produced different C frame outputs")
    return parts

def run_one(worker,payload,hg):
    result=hg.real_hlos_once(worker,payload)
    need(len(result)==len(payload),"wrong original C single-frame output")
    return result

def model_frame(frame,bridge,probe,np,expected):
    need(frame==expected,"single/batch original C frame parity failed")
    bgr=bridge.nv12_full_range_gray_to_bgr(frame)
    need(bgr.shape==(604,644,3) and
         np.array_equal(bgr[:,:,0],np.frombuffer(
             frame[:604*644],dtype=np.uint8).reshape((604,644))),
         "original grayscale Y not exactly preserved")
    feature=probe.extract_one_face(bgr)
    need(feature.shape==(1,128) and np.isfinite(feature).all(),
         "actual pinned YuNet/SFace not yielding finite 128d public feature")

def malformed_batch_reject(worker,payload):
    """Original C checks all bounded bytes before writing any stdout."""
    for wrong in (payload*N+b"\x00",(payload*N)[:-1]):
        p=subprocess.run([str(worker),"--frames",str(N)],input=wrong,
                         capture_output=True,timeout=70)
        need(p.returncode!=0 and p.stdout==b"",
             "malformed original C batch emitted partial frame(s)")
    return True

def main():
    need(platform.machine()=="aarch64" and os.geteuid()!=0 and
         os.environ.get("OMP_NUM_THREADS")=="1" and
         os.environ.get("OPENBLAS_NUM_THREADS")=="1",
         "require unprivileged bounded ARM64 CPU-only test")
    import cv2
    import numpy as np
    need(cv2.__version__=="4.12.0","actual ARM64 model runtime changed")
    cv2.setNumThreads(1)
    need(cv2.getNumThreads()==1,"OpenCV thread cap not applied")
    hg=import_file(HG/"benchmark_offline.py","e004hh_original_hg_worker")
    bridge=import_file(hg.BRIDGE,"e004hh_strict_bridge")
    face=import_file(hg.PROBE,"e004hh_model")
    prior=json.loads((HG/"evidence/RESULT.json").read_text())
    need(prior["status"]==
         "PASS_BOUNDED_ARM64_PUBLIC_ONLY_MAINTAINED_HLOS_C_TO_YUNET_SFACE_CPU_TIMING" and
         prior["identical_repeated_input_is_new_capture_or_liveness"] is False and
         prior["native_ir_emitter_authorized"] is False,
         "previous single-frame real C/model provenance invalid")
    model=face.OfflineFaceProbe(hg.ASSETS)
    public=hg.public_only_nv12(cv2,np)
    expected=None
    with TemporaryDirectory(prefix="e004hh-original-c-batch-") as folder:
        binary=hg.compile_worker(Path(folder))
        frame_len=hg.NVLEN
        # Original maintained C whole-batch input validation and no-output-on-error.
        need(malformed_batch_reject(binary,public),"batch malformed input checks")
        # Test true model parity for all eight frames, not only eight C outputs.
        one=run_one(binary,public,hg)
        batches=run_batch(binary,public,frame_len,hg.YLEN)
        need(all(f==one for f in batches),
             "original --frames 8 diverged from original single-frame mode")
        expected=one
        for _ in range(WARM):
            model_frame(run_one(binary,public,hg),bridge,model,np,expected)
            for item in run_batch(binary,public,frame_len,hg.YLEN):
                model_frame(item,bridge,model,np,expected)
        before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        records={
          "single_eight_new_processes_hlos_ms":[],
          "single_first_public_feature_ready_ms":[],
          "single_total_eight_public_features_ready_ms":[],
          "batch_one_process_eight_frames_hlos_ms":[],
          "batch_first_public_feature_ready_ms":[],
          "batch_total_eight_public_features_ready_ms":[],
        }
        for pair in range(TRIALS):
            modes=("single","batch") if pair%2==0 else ("batch","single")
            for mode in modes:
                start=time.perf_counter_ns()
                if mode=="batch":
                    processed=run_batch(binary,public,frame_len,hg.YLEN)
                    hlos_done=time.perf_counter_ns()
                    first_ready=None
                    for item in processed:
                        model_frame(item,bridge,model,np,expected)
                        if first_ready is None:first_ready=time.perf_counter_ns()
                    end=time.perf_counter_ns()
                    records["batch_one_process_eight_frames_hlos_ms"].append(hlos_done-start)
                    records["batch_first_public_feature_ready_ms"].append(first_ready-start)
                    records["batch_total_eight_public_features_ready_ms"].append(end-start)
                else:
                    hlos_ns=0
                    first_ready=None
                    for _ in range(N):
                        a=time.perf_counter_ns()
                        item=run_one(binary,public,hg)
                        hlos_ns+=time.perf_counter_ns()-a
                        model_frame(item,bridge,model,np,expected)
                        if first_ready is None:first_ready=time.perf_counter_ns()
                    end=time.perf_counter_ns()
                    records["single_eight_new_processes_hlos_ms"].append(hlos_ns)
                    records["single_first_public_feature_ready_ms"].append(first_ready-start)
                    records["single_total_eight_public_features_ready_ms"].append(end-start)
        after=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result={
        "experiment":"E004hh",
        "status":"PASS_ORIGINAL_ARM64_HLOS_C_BATCH8_VS_EIGHT_PROCESS_PUBLIC_MODEL_CADENCE_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"6d41d77982498c95014e49bbf6895a84b20aa56f",
        "arch":"aarch64","opencv":"4.12.0","cpu_threads_per_library":1,
        "public_visible_light_fixture_sha256":hg.GROUP_SHA,
        "prior_e004hg_result_sha256":sha256((HG/"evidence/RESULT.json").read_bytes()).hexdigest(),
        "original_maintained_hlos_worker_sha256":sha256(
            (hg.HLOS/"sp11-hlos-ir.c").read_bytes()).hexdigest(),
        "original_nv12_bridge_sha256":sha256(hg.BRIDGE.read_bytes()).hexdigest(),
        "original_face_probe_sha256":sha256(hg.PROBE.read_bytes()).hexdigest(),
        "original_maintained_hlos_c_batch_frame_limit":16,
        "benchmark_batch_frames":N,
        "warmup_pairs":WARM,
        "measured_pairs_alternated_order":TRIALS,
        "total_measured_public_frame_model_extractions":TRIALS*2*N,
        "original_single_vs_batch_hlos_output_byte_equal":True,
        "original_C_batch_rejects_truncated_or_overlong_input_without_partial_output":True,
        "original_C_batch_writes_nothing_until_all_input_read_and_validated":True,
        "original_C_batch_withholds_all_output_until_all_frames_processed":True,
        "timing_ms":{name:timer_summary(vals) for name,vals in records.items()},
        "testing_python_process_ru_maxrss_kib_before_after":[before,after],
        "repeated_fixture_is_not_new_capture_freshness_or_liveness":True,
        "measured_real_camera_or_dark_nir_frame_rate":False,
        "real_biometric_authentication_or_enrollment_proven":False,
        "actual_optical_electrical_fault_off_proven":False,
        "raw_nv12_bgr_public_crop_embedding_or_scores_persisted":False,
        "native_linux_emitter_or_login_modified":False,
        "windows_kd_camera_pmic_led_or_golden_modified":False,
        "benchmark_source_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_batch.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HH_REAL_MAINTAINED_C_BATCH8_AND_8_NEW_PROCESSES_C_TO_YUNET_SFACE=PASS")
    for name,timing in result["timing_ms"].items():
        print("E004HH_BOUNDED_CPU_MEDIAN_MS",name,timing["median_ms"])
    print("E004HH_MALFORMED_BATCH_NO_PARTIAL_OUTPUT=PASS HLOS_PIXEL_PARITY=PASS")
    print("E004HH_BATCH_IS_NOT_STREAMING_OR_LIVENESS=YES NATIVE_IR=OFF GOLDEN=UNCHANGED")

if __name__=="__main__":main()
