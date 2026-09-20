#!/usr/bin/env python3
"""E004hi: actual C streaming sidecar with original maintained HLOS pixel core.

Public visible-light fixture/model ONLY. Eight provisional live IPC outputs are
never a committed session until EOF, the exact DONE index AND child exit zero.
No real camera, near IR, PMIC, emitter, liveness, enrollment or login.
"""
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HG=ROOT/"experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf"
HH=ROOT/"experiments/E004-front-ir-vd55g0/e004hh-bounded-actual-hlos-batch-throughput"
HLOS=ROOT/"src/sp11-camera-hlos-worker"
STREAM_C=HLOS/"sp11-offline-nv12-stream.c"
CLIENT=HLOS/"sp11-offline-stream-client.py"
N=8

def need(ok,why):
    if not ok:raise AssertionError("E004HI_FAIL_CLOSED "+why)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    need(spec is not None and spec.loader is not None,"source absent")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def compile_stream(path,hg):
    originals=list(hg.SOURCES)
    need(originals[0].name=="sp11-hlos-ir.c" and
         len(originals)==9,"original maintained pixel algorithm files changed")
    args=["clang","-std=c11","-O2","-Wall","-Wextra","-Werror",
          str(STREAM_C),*(str(file) for file in originals[1:]),
          "-o",str(path)]
    result=subprocess.run(args,capture_output=True,text=True,timeout=75)
    need(result.returncode==0 and path.is_file(),
         "original source plus offline sidecar did not compile: "+result.stderr[-350:])
    return path

def packet(index,payload):
    return b"IN01"+index.to_bytes(4,"little")+payload

def original_c_negative(worker,payload,expected):
    """Raw C protocol error behavior, no Python client or model involvement."""
    fail_first=(
        ("bad first index",2,packet(2,payload)),
        ("bad first header",1,b"BAD1"+(1).to_bytes(4,"little")+payload),
        ("partial first frame",1,packet(1,payload)[:-1]),
        ("unexpected nonneutral chroma",1,packet(1,payload[:len(payload)-len(payload)//3]+b"")),
    )
    # Construct exact malformed nonneutral NV12 with same total length.
    y=644*604
    bad_uv=payload[:y]+bytes([129])+payload[y+1:]
    fail_first=fail_first[:-1]+(("unexpected nonneutral chroma",1,packet(1,bad_uv)),)
    for why,count,data in fail_first:
        p=subprocess.run([str(worker),"--frames",str(count)],input=data,
                         capture_output=True,timeout=35)
        need(p.returncode!=0 and p.stdout==b"",
             "malformed FIRST frame emitted image bytes: "+why)
    for val in (0,17):
        p=subprocess.run([str(worker),"--frames",str(val)],input=b"",
                         capture_output=True,timeout=12)
        need(p.returncode!=0 and p.stdout==b"",
             "unbounded/zero original C stream count accepted")
    for why,data,count in (
        ("late invalid second index",packet(1,payload)+b"IN01"+(3).to_bytes(4,"little"),2),
        ("extra data after final provisional frame",packet(1,payload)+b"X",1),
        ("truncated second frame",packet(1,payload)+packet(2,payload)[:-1],2),
    ):
        p=subprocess.run([str(worker),"--frames",str(count)],input=data,
                         capture_output=True,timeout=45)
        need(p.returncode!=0 and p.stdout==
             b"OUT1"+(1).to_bytes(4,"little")+expected,
             "partial session was falsely committed or emitted bad frame: "+why)
        need(b"DONE" not in p.stdout,
             "failure after provisional frame got terminal success")
    return len(fail_first)+2+3

def client_faults(client,worker,payload):
    """Caller-abort must remain terminal; no reusable session after failure."""
    badcount=0
    for bad in (0,17,True):
        try:client.OfflineStream(worker,bad)
        except client.StreamFault:badcount+=1
        else:raise AssertionError("client accepted invalid frame count")
    for kind in ("wrong-order","wrong-type","nonneutral-UV","caller-timeout",
                 "late-bad-second-frame"):
        session=client.OfflineStream(worker,2,max_seconds=20.0)
        if kind=="late-bad-second-frame":
            provisional=session.accept(1,payload)
            need(len(provisional)==len(payload),
                 "offline provisional frame unexpectedly missing")
        try:
            if kind=="wrong-order":session.accept(2,payload)
            elif kind=="wrong-type":session.accept(1,bytearray(payload))
            elif kind=="nonneutral-UV":
                y=644*604
                session.accept(1,payload[:y]+bytes([129])+payload[y+1:])
            elif kind=="caller-timeout":
                session._deadline=time.monotonic()-1
                session.accept(1,payload)
            else:session.accept(2,bytearray(payload))
        except client.StreamFault:badcount+=1
        else:raise AssertionError("offline stream client accepted "+kind)
        need(session.state=="fault","failed stream was not terminal")
        try:session.accept(session.next_index,payload)
        except client.StreamFault:pass
        else:raise AssertionError("terminal fault permitted rearm")
    return badcount

def main():
    need(platform.machine()=="aarch64" and os.geteuid()!=0 and
         os.getenv("OMP_NUM_THREADS")=="1" and
         os.getenv("OPENBLAS_NUM_THREADS")=="1",
         "only bounded unprivileged single-thread ARM64 diagnostic allowed")
    import cv2
    import numpy as np
    need(cv2.__version__=="4.12.0","pinned model runtime changed")
    cv2.setNumThreads(1)
    need(cv2.getNumThreads()==1,"CPU OpenCV threads not capped")
    hg=load(HG/"benchmark_offline.py","e004hi_original_hg_public_fixture")
    bridge=load(hg.BRIDGE,"e004hi_original_gray_bridge")
    face=load(hg.PROBE,"e004hi_original_face_probe")
    client=load(CLIENT,"e004hi_one_shot_stream_client")
    prior=json.loads((HH/"evidence/RESULT.json").read_text())
    need(prior["status"]==
         "PASS_ORIGINAL_ARM64_HLOS_C_BATCH8_VS_EIGHT_PROCESS_PUBLIC_MODEL_CADENCE_OFFLINE" and
         prior["original_single_vs_batch_hlos_output_byte_equal"] is True and
         prior["native_linux_emitter_or_login_modified"] is False,
         "previous original HLOS pixel-parity evidence invalid")
    public=hg.public_only_nv12(cv2,np)
    need(len(public)==client.FRAME_LEN,"strict C/client frame geometry mismatch")
    model=face.OfflineFaceProbe(hg.ASSETS)
    with TemporaryDirectory(prefix="e004hi-native-stream-") as scratch:
        folder=Path(scratch)
        binary=compile_stream(folder/"offline-stream",hg)
        standalone=hg.compile_worker(folder)
        expected=hg.real_hlos_once(standalone,public)
        prewarm=bridge.nv12_full_range_gray_to_bgr(expected)
        feature=model.extract_one_face(prewarm)
        need(feature.shape==(1,128) and np.isfinite(feature).all(),
             "actual YuNet/SFace public single-face warmup failed")
        negatives=original_c_negative(binary,public,expected)
        client_negative_count=client_faults(client,binary,public)
        stream=client.OfflineStream(binary,N,max_seconds=40.0)
        start=time.perf_counter_ns()
        first_ready=None
        for idx in range(1,N+1):
            untrusted=stream.accept(idx,public)
            need(untrusted==expected,"maintained HLOS C streaming pixel parity failure")
            image=bridge.nv12_full_range_gray_to_bgr(untrusted)
            feature=model.extract_one_face(image)
            need(feature.shape==(1,128) and np.isfinite(feature).all(),
                 "original actual YuNet/SFace rejected streamed public ROI")
            if first_ready is None:first_ready=time.perf_counter_ns()
        last_feature=time.perf_counter_ns()
        proof=stream.finish()
        complete=time.perf_counter_ns()
        need(stream.state=="complete" and proof["frames_checked"]==N and
             proof["all_outputs_provisional_until_terminal_done"] is True and
             all(proof[key] is False for key in (
                 "frame_capture_freshness_or_liveness_proven",
                 "face_authentication_or_enrollment_proven",
                 "login_or_unlock_authorized","native_ir_emitter_activated",
                 "autonomous_hardware_cutoff_proven")),
             "offline terminal result falsely became an authenticator")
        try:stream.accept(1,public)
        except client.StreamFault:pass
        else:raise AssertionError("completed worker rearmed after DONE")
    result={
        "experiment":"E004hi",
        "status":"PASS_BOUNDED_PROVISIONAL_HLOS_C_FRAME_STREAM_FINAL_COMMIT_AND_REAL_MODEL_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"30128962a778d6f41c8f472408d800004134af72",
        "arch":"aarch64","opencv":"4.12.0",
        "cpu_threads_per_library":1,
        "original_public_image_sha256":hg.GROUP_SHA,
        "prior_e004hh_result_sha256":sha256((HH/"evidence/RESULT.json").read_bytes()).hexdigest(),
        "original_maintained_hlos_core_source_sha256":{
            file.name:sha256(file.read_bytes()).hexdigest() for file in hg.SOURCES[1:]},
        "original_unchanged_single_frame_worker_sha256":
            sha256(hg.SOURCES[0].read_bytes()).hexdigest(),
        "isolated_offline_stream_sidecar_source_sha256":sha256(STREAM_C.read_bytes()).hexdigest(),
        "isolated_offline_stream_client_source_sha256":sha256(CLIENT.read_bytes()).hexdigest(),
        "original_full_range_gray_bridge_source_sha256":sha256(hg.BRIDGE.read_bytes()).hexdigest(),
        "original_actual_face_probe_source_sha256":sha256(hg.PROBE.read_bytes()).hexdigest(),
        "frames_per_stream":N,
        "original_C_input_first_frame_or_count_negative_cases":negatives,
        "stream_client_terminal_fault_negative_cases":client_negative_count,
        "stream_c_output_exact_original_maintained_one_frame_bytes":True,
        "actual_yunet_sface_all_provisional_public_stream_frames_128d":True,
        "provisional_output_committed_before_exact_DONE_and_child_exit_zero":False,
        "malformed_late_session_can_deliver_prior_provisional_frame":True,
        "late_session_failure_invalidates_all_previous_provisional_frames":True,
        "deadline_requires_caller_to_invoke_a_client_method":True,
        "independent_host_failure_watchdog_proven":False,
        "one_stream_first_provisional_public_feature_ready_ms":round(
            (first_ready-start)/1e6,3),
        "one_stream_last_provisional_public_feature_ready_ms":round(
            (last_feature-start)/1e6,3),
        "one_stream_terminal_commit_ready_ms":round((complete-start)/1e6,3),
        "single_stream_timings_are_bounded_diagnostic_not_camera_fps":True,
        "real_camera_frame_freshness_near_ir_darkness_or_liveness_proven":False,
        "real_user_enrollment_match_or_login_authorized":False,
        "raw_image_nv12_bgr_embedding_match_scores_saved":False,
        "native_linux_emitter_or_pam_modified":False,
        "windows_kd_camera_pmic_led_or_golden_modified":False,
        "actual_optical_current_pulse_autonomous_fault_off_proven":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_stream.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HI_ACTUAL_HLOS_C_STREAM_8_PROVISIONAL_FRAMES_DONE_EXIT0=PASS")
    print("E004HI_ORIGINAL_HLOS_PIXELS_EXACT_AND_REAL_ARM64_YUNET_SFACE=PASS")
    print("E004HI_ORIGINAL_C_NEGATIVES",negatives,"CLIENT_TERMINAL_NEGATIVES",client_negative_count)
    print("E004HI_FIRST_FEATURE_MS",result["one_stream_first_provisional_public_feature_ready_ms"],
          "LAST_FEATURE_MS",result["one_stream_last_provisional_public_feature_ready_ms"],
          "TERMINAL_COMMIT_MS",result["one_stream_terminal_commit_ready_ms"])
    print("E004HI_NO_PROVEN_LIVENESS_NIR_AUTH_WATCHDOG_OR_LED=PASS")

if __name__=="__main__":main()
