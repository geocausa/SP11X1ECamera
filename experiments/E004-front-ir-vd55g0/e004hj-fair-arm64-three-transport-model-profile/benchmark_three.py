#!/usr/bin/env python3
"""E004hj: original HLOS single/batch and uninstalled C stream, one ARM64 session.

Six rotation-balanced cycles of three modes, same single-thread CPU, same
PUBLIC visible-light ROI, same real original YuNet/SFace objects. This is
NOT real camera cadence, native NIR quality, liveness or identity acceptance.
"""
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
import importlib.util
import json
import math
import os
import platform
import resource
import statistics
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STAGES=ROOT/"experiments/E004-front-ir-vd55g0"
HG=STAGES/"e004hg-arm64-hlos-yunet-sface-bounded-perf"
HH=STAGES/"e004hh-bounded-actual-hlos-batch-throughput"
HI=STAGES/"e004hi-failclosed-offline-hlos-stream-transport"
HLOS=ROOT/"src/sp11-camera-hlos-worker"
MODES=("single","batch","stream")
N=8
ROUNDS=6
WARM_ROUNDS=1

def need(ok,reason):
    if not ok:raise AssertionError("E004HJ_FAIL_CLOSED "+reason)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    need(spec is not None and spec.loader is not None,"original source missing")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def summary(values):
    need(len(values)==ROUNDS and all(type(x) is int and x>=0 for x in values),
         "wrong/nonfinite original bounded paired samples")
    order=sorted(values)
    return {"samples":ROUNDS,
            "min_ms":round(order[0]/1e6,3),
            "median_ms":round(statistics.median(order)/1e6,3),
            "p95_nearest_rank_ms":round(order[-1]/1e6,3),
            "max_ms":round(order[-1]/1e6,3)}

def main():
    need(platform.machine()=="aarch64" and os.geteuid()!=0 and
         os.environ.get("OMP_NUM_THREADS")=="1" and
         os.environ.get("OPENBLAS_NUM_THREADS")=="1",
         "only unprivileged single-thread ARM64 offline benchmark allowed")
    import cv2
    import numpy as np
    need(cv2.__version__=="4.12.0","original ARM64 OpenCV version changed")
    cv2.setNumThreads(1)
    need(cv2.getNumThreads()==1,"OpenCV CPU threading not restricted")
    hg=load(HG/"benchmark_offline.py","e004hj_original_maintained_hlos")
    hh=load(HH/"benchmark_batch.py","e004hj_original_c_batch")
    hi=load(HI/"verify_stream.py","e004hj_original_stream_wrapper")
    client=load(HLOS/"sp11-offline-stream-client.py","e004hj_original_stream_client")
    bridge=load(hg.BRIDGE,"e004hj_original_luma_bridge")
    face=load(hg.PROBE,"e004hj_original_yunet_sface")
    earlier={}
    for key,stage,want in (
        ("hg",HG,"PASS_BOUNDED_ARM64_PUBLIC_ONLY_MAINTAINED_HLOS_C_TO_YUNET_SFACE_CPU_TIMING"),
        ("hh",HH,"PASS_ORIGINAL_ARM64_HLOS_C_BATCH8_VS_EIGHT_PROCESS_PUBLIC_MODEL_CADENCE_OFFLINE"),
        ("hi",HI,"PASS_BOUNDED_PROVISIONAL_HLOS_C_FRAME_STREAM_FINAL_COMMIT_AND_REAL_MODEL_OFFLINE"),
    ):
        source=stage/"evidence/RESULT.json"
        proof=json.loads(source.read_text())
        need(proof["status"]==want,"prior original actual model/stream provenance changed")
        earlier[key]=sha256(source.read_bytes()).hexdigest()
    need(not json.loads((HI/"evidence/RESULT.json").read_text())[
        "real_user_enrollment_match_or_login_authorized"],
        "previous original streaming path falsely authenticated")
    public=hg.public_only_nv12(cv2,np)
    model=face.OfflineFaceProbe(hg.ASSETS)
    measurements={mode:{"first_feature_ns":[],"all_eight_features_and_successful_child_exit_ns":[]}
                  for mode in MODES}
    rotations=[]
    with TemporaryDirectory(prefix="e004hj-three-original-modes-") as scratch:
        folder=Path(scratch)
        original=hg.compile_worker(folder)
        stream_binary=hi.compile_stream(folder/"stream-sidecar",hg)
        expected=hg.real_hlos_once(original,public)
        need(expected!=public and expected[hg.YLEN:]==bytes([128])*(hg.NVLEN-hg.YLEN),
             "original maintained HLOS C pixel output not neutral/processed")
        proof=face.OfflineFaceProbe.diagnostic_result()
        need(proof["login_or_unlock_authorized"] is False and
             proof["face_recognition_accuracy_or_liveness_proven"] is False,
             "actual offline model probe improperly authorizes an identity")

        def public_model(frame):
            need(frame==expected,"original maintained single/batch/stream HLOS C pixel divergence")
            bgr=bridge.nv12_full_range_gray_to_bgr(frame)
            need(bgr.shape==(hg.H,hg.W,3) and
                 np.array_equal(bgr[:,:,0],np.frombuffer(
                     expected[:hg.YLEN],np.uint8).reshape(hg.H,hg.W)),
                 "original full-range NV12 luma altered in model bridge")
            ephemeral=model.extract_one_face(bgr)
            need(ephemeral.shape==(1,128) and np.isfinite(ephemeral).all(),
                 "original real YuNet/SFace rejected public-only HLOS C output")

        def sample(mode):
            started=time.perf_counter_ns()
            if mode=="single":
                first=None
                for _ in range(N):
                    data=hg.real_hlos_once(original,public)
                    public_model(data)
                    if first is None:first=time.perf_counter_ns()
                completed=time.perf_counter_ns()
            elif mode=="batch":
                parts=hh.run_batch(original,public,hg.NVLEN,hg.YLEN)
                first=None
                for data in parts:
                    public_model(data)
                    if first is None:first=time.perf_counter_ns()
                completed=time.perf_counter_ns()
            else:
                session=client.OfflineStream(stream_binary,N,max_seconds=50.0)
                first=None
                for index in range(1,N+1):
                    provisional=session.accept(index,public)
                    public_model(provisional)
                    if first is None:first=time.perf_counter_ns()
                terminal=session.finish()
                completed=time.perf_counter_ns()
                need(session.state=="complete" and terminal["frames_checked"]==N and
                     terminal["login_or_unlock_authorized"] is False and
                     terminal["all_outputs_provisional_until_terminal_done"] is True,
                     "stream terminal marker was not genuine offline DONE/exit0")
            need(0<first-started<=completed-started,"invalid first/terminal timing order")
            return first-started,completed-started

        # All three modes warm before timed rotations; no model init/C
        # compilation/ROI preparation is included in measured trials.
        for _ in range(WARM_ROUNDS):
            for mode in MODES:sample(mode)
        rss_before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        for cycle in range(ROUNDS):
            sequence=[MODES[(cycle+j)%3] for j in range(3)]
            rotations.append(sequence)
            for mode in sequence:
                first,total=sample(mode)
                measurements[mode]["first_feature_ns"].append(first)
                measurements[mode]["all_eight_features_and_successful_child_exit_ns"].append(total)
        rss_after=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result={
        "experiment":"E004hj",
        "status":"PASS_THREE_MODE_SAME_SESSION_REAL_ARM64_HLOS_C_REAL_YUNET_SFACE_LATENCY_ROTATION",
        "date":"2026-09-20",
        "baseline_commit":"228d9b882173d55109b1c00acc5fbb6fa90b5468",
        "arch":"aarch64","opencv":"4.12.0",
        "OMP_OPENBLAS_OPENCV_THREADS_EACH":1,
        "original_public_visible_light_fixture_sha256":hg.GROUP_SHA,
        "pinned_prior_original_stage_result_sha256":earlier,
        "original_hlos_one_shot_c_source_sha256":sha256(hg.SOURCES[0].read_bytes()).hexdigest(),
        "original_core_source_sha256":{p.name:sha256(p.read_bytes()).hexdigest()
                                       for p in hg.SOURCES[1:]},
        "uninstalled_offline_stream_c_source_sha256":sha256(hi.STREAM_C.read_bytes()).hexdigest(),
        "uninstalled_offline_stream_client_source_sha256":sha256(hi.CLIENT.read_bytes()).hexdigest(),
        "original_face_probe_source_sha256":sha256(hg.PROBE.read_bytes()).hexdigest(),
        "original_nv12_bridge_source_sha256":sha256(hg.BRIDGE.read_bytes()).hexdigest(),
        "original_identical_public_frame_bytes_per_trial":N,
        "mode_rotation_warmups":WARM_ROUNDS,
        "mode_rotation_measured_rounds":ROUNDS,
        "exact_three_mode_rotation_order":rotations,
        "total_measured_original_yunet_sface_public_feature_extractions":N*len(MODES)*ROUNDS,
        "all_three_modes_c_output_equal_original_single_frame_bytes":True,
        "each_stream_session_successful_DONE_and_exit0":True,
        "stream_earlier_output_was_provisional_until_DONE":True,
        "timing_ms":{mode:{
            "first_feature":summary(b["first_feature_ns"]),
            "all_eight_features_and_successful_child_exit":summary(
                b["all_eight_features_and_successful_child_exit_ns"]),
          } for mode,b in measurements.items()},
        "testing_python_process_peak_rss_kib_before_after":[rss_before,rss_after],
        "n6_nearest_rank_p95_is_observed_max_not_statistical_tail":True,
        "repeated_same_public_visible_light_frame_is_not_a_fresh_camera_stream":True,
        "real_sp11_illuminated_nir_or_dark_room_recognition_proven":False,
        "biometric_accuracy_replay_resistance_liveness_enrollment_login_proven":False,
        "autonomous_host_or_pmic_fault_off_proven":False,
        "actual_optical_irradiance_or_emitter_current_proven":False,
        "native_ir_emitter_or_pam_modified":False,
        "windows_kd_camera_pmic_led_or_golden_modified":False,
        "raw_image_nv12_bgr_face_feature_match_score_or_identity_saved":False,
        "benchmark_source_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_modes.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HJ_SAME_SESSION_THREE_MODE_REAL_ARM64_HLOS_C_MODEL_144_PUBLIC_EXTRACTIONS=PASS")
    for mode in MODES:
        m=result["timing_ms"][mode]
        print("E004HJ_SAME_SESSION_MEDIAN",mode,
              "first_ms",m["first_feature"]["median_ms"],
              "all_eight_and_exit_ms",m["all_eight_features_and_successful_child_exit"]["median_ms"])
    print("E004HJ_NO_REAL_IR_CAMERA_AUTH_LIVENESS_OR_WATCHDOG=PASS GOLDEN_UNCHANGED")
if __name__=="__main__":main()
