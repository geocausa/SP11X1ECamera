#!/usr/bin/env python3
"""E004ia fail-closed model order after real C transaction; public/synthetic only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HLOS=ROOT/"src/sp11-camera-hlos-worker"
HZ=ROOT/"experiments/E004-front-ir-vd55g0/e004hz-transactional-hlos-offline-gate"
HI=ROOT/"experiments/E004-front-ir-vd55g0/e004hi-failclosed-offline-hlos-stream-transport"

def load(file,name):
    s=importlib.util.spec_from_file_location(name,file)
    assert s and s.loader
    m=importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

def run():
    ia=load(HLOS/"sp11-offline-public-commit-diagnostic.py","ia_committed_model")
    hi=load(HI/"verify_stream.py","ia_original_compile")
    hz=load(HZ/"test_transaction.py","ia_original_fake_worker")
    np=ia.bridge.np
    y=644*604
    synthetic=bytes([40])*y+bytes([128])*(y//2)
    calls={"constructed":0,"extracted":0}
    class FakeProbe:
        def __init__(self):
            calls["constructed"]+=1
        def extract_one_face(self,image):
            calls["extracted"]+=1
            assert image.shape==(604,644,3)
            return np.zeros((1,128),np.float32)
    failed=0
    def reject(work,frames,count,why):
        nonlocal failed
        calls["constructed"]=calls["extracted"]=0
        try:ia._committed_model_diagnostic(work,frames,FakeProbe,20.0)
        except ia.DiagnosticFault as exc:
            assert "pixels" not in str(exc) and "feature" not in str(exc)
        else:raise AssertionError("E004IA_FAIL_OPEN "+why)
        assert calls["constructed"]==calls["extracted"]==0,(why,calls)
        failed+=1
    for invalid in ((), tuple(synthetic for _ in range(9)),(bytearray(synthetic),),
                    (synthetic[:-1],),(synthetic[:y]+bytes([129])+synthetic[y+1:],)):
        reject("/tmp/e004ia-invalid-do-not-open",invalid,0,"preflight")
    with TemporaryDirectory(prefix="e004ia-commit-order-") as temp:
        folder=Path(temp)
        real=hi.compile_stream(folder/"original-HLOS-stream",ia.hg)
        for case,count in (("late-fail",2),("bad-done",1),
                           ("extra-byte",1),("exit-one",1)):
            bogus=hz.fake_child(folder,case)
            reject(bogus,(synthetic,)*count,count,case)
        receipt=ia._committed_model_diagnostic(real,(synthetic,)*2,FakeProbe,30.0)
        assert calls=={"constructed":1,"extracted":2},calls
        assert receipt["status"]=="complete" and receipt["frames_checked"]==2
        assert receipt["processed_frame_feature_inference_only_after_native_C_transaction_commit"] is True
        for field in ("temporary_model_features_or_frame_pixels_returned_or_persisted",
                      "native_live_camera_frames_validated",
                      "near_ir_illuminated_or_darkness_face_tested",
                      "face_identity_or_anti_spoofing_proven",
                      "real_user_enrolled_or_authenticated",
                      "login_or_unlock_authorized",
                      "native_ir_emitter_activated",
                      "autonomous_hardware_emitter_cutoff_proven"):
            assert receipt[field] is False,field
        # Model crashes after a valid native commit still fail without
        # returning partial results or a biometric acceptance signal.
        def bad_factory():
            raise RuntimeError("synthetic model construction fault")
        try:ia._committed_model_diagnostic(real,(synthetic,),bad_factory,30.0)
        except ia.DiagnosticFault as exc:
            assert "synthetic" not in str(exc)
        else:raise AssertionError("E004IA_FAIL_OPEN_MODELINIT")
        failed+=1
        class BadFeature:
            def extract_one_face(self,image):
                return np.full((1,128),np.nan,np.float32)
        try:ia._committed_model_diagnostic(real,(synthetic,),BadFeature,30.0)
        except ia.DiagnosticFault:
            pass
        else:raise AssertionError("E004IA_FAIL_OPEN_NONFINITE_FEATURE")
        failed+=1
    assert failed==11,failed
    print("E004IA_NATIVE_C_SYNTHETIC_COMMIT_BEFORE_PROCESSED_FRAME_INFERENCE=PASS")
    print("E004IA_PRECOMMIT_LATE_FAILURE_MODEL_FACTORY_AND_INFERENCE_CALLS_ZERO=PASS COUNT=9")
    print("E004IA_MODEL_CONSTRUCTION_OR_NONFINITE_FEATURE_AFTER_COMMIT_FAIL_CLOSED=PASS COUNT=2")
    print("E004IA_NO_NATIVE_IR_CAMERA_AUTH_OR_HARDWARE_WATCHDOG")
    return failed

if __name__=="__main__":run()
