#!/usr/bin/env python3
"""E004go: synthetic, no-camera session protocol tests against real C telemetry."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import importlib.util
import itertools
import json
import subprocess

HERE=Path(__file__).resolve().parent
SRC=HERE/"sp11-offline-session-gate.py"
spec=importlib.util.spec_from_file_location("sp11_offline_gate",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def assert_fault(op, session):
    try:op()
    except m.SessionFault:pass
    else:raise AssertionError("invalid operation was accepted")
    assert session.state==m.State.FAULT and session.count==0

def encode(frames=1):
    item={"frame":1,"mean_milli":120000,"p10":40,"p90":200,
          "dark_0_15_permille":20,"bright_240_255_permille":30,
          "neighbor_abs_diff_milli":3000}
    return json.dumps({"kind":m.KIND,"face_authentication_proven":False,
                       "frames":[{**item,"frame":i+1} for i in range(frames)]},
                      separators=(",",":"),sort_keys=True).encode()

def test_core():
    for count in range(1,17):
        s=m.OfflineSession(50)
        assert s.state==m.State.IDLE
        s.start(100)
        s.deadline_check(110)
        s.accept(120,encode(count))
        result=s.diagnostic_result()
        assert result["frames_checked"]==count
        assert result["login_or_unlock_authorized"] is False
        assert result["face_authentication_proven"] is False
        assert result["native_ir_emitter_activated"] is False
        assert result["autonomous_hardware_cutoff_proven"] is False
        assert_fault(lambda:s.start(121),s)
    for mutate in (
        lambda r:r|{"face_authentication_proven":True},
        lambda r:r|{"kind":"biometric-authentication"},
        lambda r:r|{"face_embedding":[1,2,3]},
        lambda r:r|{"frames":[]},
        lambda r:r|{"frames":r["frames"]*17},
        lambda r:r|{"frames":[{**r["frames"][0],"frame":2}]},
        lambda r:r|{"frames":[{**r["frames"][0],"p10":220}]},
        lambda r:r|{"frames":[{**r["frames"][0],"mean_milli":255001}]},
        lambda r:r|{"frames":[{**r["frames"][0],"neighbor_abs_diff_milli":255001}]},
        lambda r:r|{"frames":[{**r["frames"][0],"bright_240_255_permille":1001}]},
        lambda r:r|{"frames":[{**r["frames"][0],"frame":True}]},
        lambda r:r|{"frames":[{**r["frames"][0],"mean_milli":float("nan")}]},
        lambda r:r|{"frames":[{**r["frames"][0],"raw_image":[0,1]}]},
    ):
        data=mutate(json.loads(encode()))
        payload=json.dumps(data,allow_nan=True).encode()
        s=m.OfflineSession();s.start(0)
        assert_fault(lambda:s.accept(1,payload),s)
    bad=[
        b"", b"{}",b"null", b'{"kind":"unknown"}',
        b'{"kind":"unprotected-offline-signal-telemetry","kind":"duplicated"}',
        b"\xff", b"["*1500+b"]"*1500, b"x" * (m.MAX_TELEMETRY_BYTES+1),
    ]
    for payload in bad:
        s=m.OfflineSession();s.start(0)
        assert_fault(lambda:s.accept(1,payload),s)
    s=m.OfflineSession();assert_fault(lambda:s.accept(0,encode()),s)
    for bad_tick in (-1,True,1.0,"3"):
        s=m.OfflineSession();assert_fault(lambda:s.start(bad_tick),s)
    s=m.OfflineSession(max_ticks=2);s.start(7)
    assert_fault(lambda:s.deadline_check(10),s)
    s=m.OfflineSession();s.start(10)
    assert_fault(lambda:s.accept(9,encode()),s)
    s=m.OfflineSession();s.start(0);s.cancel()
    assert_fault(lambda:s.accept(1,encode()),s)
    s=m.OfflineSession();assert_fault(s.cancel,s)
    s=m.OfflineSession();assert_fault(s.diagnostic_result,s)
    # A diagnostic batch is one-shot. No duplicate, appended, stale or
    # post-completion frame can ever count as a new successful session.
    s=m.OfflineSession();s.start(0);s.accept(1,encode(16))
    assert_fault(lambda:s.accept(2,encode(16)),s)
    for invalid in (0,-1,1001,True,2.5,"10"):
        try:m.OfflineSession(invalid)
        except ValueError:pass
        else:raise AssertionError("invalid timeout parameter accepted")
    # State/event sequence adversarial exploration; no input sequence may
    # produce login or unlock authorization.
    cases=0
    for seq in itertools.product("SCFT",repeat=5):
        s=m.OfflineSession(max_ticks=4)
        tick=0
        for event in seq:
            try:
                if event=="S":s.start(tick)
                if event=="C":s.cancel()
                if event=="F":s.accept(tick,encode())
                if event=="T":s.deadline_check(tick)
                if s.state==m.State.COMPLETE:
                    assert s.diagnostic_result()["login_or_unlock_authorized"] is False
            except m.SessionFault:
                assert s.state==m.State.FAULT and s.count==0
            tick+=1
        cases+=1
    print("E004GO_OFFLINE_STATE_AND_JSON_ADVERSARIAL=PASS SEQUENCES="+str(cases))
    print("E004GO_NO_REARM_AFTER_FAULT_CANCEL_OR_COMPLETION=PASS NO_LOGIN_API=YES")

def test_actual_c():
    src=HERE/"sp11-ir-signal-metrics.c"
    with TemporaryDirectory(prefix="e004go-synthetic-metrics-") as folder:
        binary=Path(folder)/"signal-metrics"
        proc=subprocess.run(["clang","-std=c11","-O2","-Wall","-Wextra","-Werror",
                             str(src),"-o",str(binary)],
                            capture_output=True,timeout=45)
        assert proc.returncode==0,proc.stderr[-600:]
        y=644*604
        frame=bytes([40])*y+bytes([128])*(y//2)
        proc=subprocess.run([str(binary),"--frames","16"],input=frame*16,
                            capture_output=True,timeout=80)
        assert proc.returncode==0,proc.stderr[-300:]
        s=m.OfflineSession(max_ticks=20)
        s.start(100)
        s.accept(115,proc.stdout)
        assert s.diagnostic_result()["frames_checked"]==16
        assert s.diagnostic_result()["login_or_unlock_authorized"] is False
        print("E004GO_REAL_C_METRICS_16FRAME_SYNTHETIC_SESSION=PASS")
        print("E004GO_CAMERA=NO EMITTER=OFF BIOMETRIC_AUTH=NOT_IMPLEMENTED")
        return sha256(src.read_bytes()).hexdigest()

if __name__=="__main__":
    test_core()
    print("E004GO_C_METRICS_SOURCE_SHA256="+test_actual_c())
