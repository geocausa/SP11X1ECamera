#!/usr/bin/env python3
"""Offline synthetic/fault-injected all-or-nothing C stream, no device or face."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HI=ROOT/"experiments/E004-front-ir-vd55g0/e004hi-failclosed-offline-hlos-stream-transport"
HG=ROOT/"experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf"
HLOS=ROOT/"src/sp11-camera-hlos-worker"
def load(file,name):
    spec=importlib.util.spec_from_file_location(name,file)
    assert spec is not None and spec.loader is not None
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def expect_fault(op,why):
    try:op()
    except tx.TransactionFault as exc:
        assert "pixels" not in str(exc)
    else:raise AssertionError("E004HZ_FAIL_OPEN "+why)

def fake_child(folder,kind):
    # Disposable, executable child for end-of-session failures after a valid
    # first provisional frame. Does not open devices, networks or model assets.
    dest=folder/("forged-"+kind)
    dest.write_text('''#!/usr/bin/env python3
import sys
count=int(sys.argv[2])
y=644*604
size=y*3//2
frame=sys.stdin.buffer.read(8+size)
if len(frame)!=8+size:sys.exit(7)
output=frame[8:]
sys.stdout.buffer.write(b"OUT1"+(1).to_bytes(4,"little")+output)
sys.stdout.buffer.flush()
mode="'''+kind+'''"
if mode=="late-fail":
    frame=sys.stdin.buffer.read(8+size)
    if len(frame)!=8+size:sys.exit(8)
    sys.exit(9)
if mode=="bad-done":
    if sys.stdin.buffer.read(1):sys.exit(8)
    sys.stdout.buffer.write(b"DONE"+(count+1).to_bytes(4,"little"))
elif mode=="extra-byte":
    if sys.stdin.buffer.read(1):sys.exit(8)
    sys.stdout.buffer.write(b"DONE"+count.to_bytes(4,"little")+b"X")
elif mode=="exit-one":
    if sys.stdin.buffer.read(1):sys.exit(8)
    sys.stdout.buffer.write(b"DONE"+count.to_bytes(4,"little"))
sys.stdout.buffer.flush()
if mode=="exit-one":sys.exit(1)
''')
    dest.chmod(0o700)
    return dest

def run():
    global tx
    tx=load(HLOS/"sp11-offline-transaction.py","e004hz_tx")
    hi=load(HI/"verify_stream.py","e004hz_original_compile")
    hg=load(HG/"benchmark_offline.py","e004hz_original_core")
    y=644*604
    frame=bytes([40])*y+bytes([128])*(y//2)
    other=bytes([90])*y+bytes([128])*(y//2)
    malformed=frame[:y]+bytes([129])+frame[y+1:]
    wrongtype=bytearray(frame)
    faults=0
    for invalid in ((), tuple(frame for _ in range(17)), [frame],
                    (wrongtype,), (malformed,),(frame,malformed),
                    (frame,wrongtype),(frame,b"")):
        expect_fault(lambda invalid=invalid:tx.process_offline_frames(
            "/tmp/does-not-exist-e004hz",invalid), "preflight")
        faults+=1
    with TemporaryDirectory(prefix="e004hz-actual-original-") as tmp:
        folder=Path(tmp)
        worker=hi.compile_stream(folder/"actual-offline-native-C",hg)
        solo=hg.compile_worker(folder)
        baseline=hg.real_hlos_once(solo,frame)
        alternate=hg.real_hlos_once(solo,other)
        assert baseline!=alternate
        for count in (1,2,8,16):
            frames=tuple(frame if i%2==0 else other for i in range(count))
            output,receipt=tx.process_offline_frames(worker,frames,max_seconds=80)
            assert type(output) is tuple and len(output)==count
            assert output==tuple(baseline if i%2==0 else alternate for i in range(count))
            assert receipt["status"]=="complete" and receipt["frames_checked"]==count
            for k in ("login_or_unlock_authorized","native_ir_emitter_activated",
                      "autonomous_hardware_cutoff_proven",
                      "frame_capture_freshness_or_liveness_proven"):
                assert receipt[k] is False
        # Failure of a late frame is rejected before output exposure, even
        # though the unchanged original C worker can emit provisional pixels.
        for kind,count in (("late-fail",2),("bad-done",1),
                           ("extra-byte",1),("exit-one",1)):
            path=fake_child(folder,kind)
            expect_fault(lambda path=path,count=count:tx.process_offline_frames(
                path,(frame,)*count,max_seconds=20),kind)
            faults+=1
        expect_fault(lambda:tx.process_offline_frames(
            worker,(frame,),max_seconds=0.01),"invalid bounded timeout")
        faults+=1
        no_frame=folder/"missing"
        expect_fault(lambda:tx.process_offline_frames(
            no_frame,(frame,)),"missing native worker")
        faults+=1
    print("E004HZ_ACTUAL_UNCHANGED_C_SYNTHETIC_FRAME_TRANSACTION_PASS_COUNTS=1,2,8,16")
    print("E004HZ_ORIGINAL_HLOS_PIXELS_EXACT_AND_NO_PROVISIONAL_RETURN=PASS")
    print("E004HZ_PREVALIDATION_AND_LATE_CHILDEXIT_FAULT_NEGATIVES_PASS",faults)
    print("E004HZ_NO_CAMERA_IR_AUTH_ENROLLMENT_PAM_OR_HARDWARE_WATCHDOG")
    return faults

if __name__=="__main__":run()
