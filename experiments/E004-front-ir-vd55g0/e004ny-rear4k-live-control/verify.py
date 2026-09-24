#!/usr/bin/env python3
"""E004ny: offline rear 4K WinRT delivery contrast; NO pixels/KD/DMA."""
import copy
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
NX=HERE.parent/"e004nx-rear4k-no-kd-baseline"
EXPECTED_NX_SOURCE="ca5f7e8eb30cd017e618a3835a3f3d2726a900714005c202c44da6587c321983"
EXPECTED_NY_SOURCE="98562dd2add12098313ec576619ddaf94fbdfac6c5dab2893dccd4a55990385c"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(nx,ny,nw):
    assert nx["schema"]=="sp11-e004nx-same-machine-windows-rear4k-no-KD-two-pass-scalar-v1"
    assert ny["schema"]=="sp11-e004ny-same-SP11-Windows-rear4k-two-pass-counted-frame-handle-scalar-v1"
    assert nw["schema"]=="sp11-e004nw-private-Windows-rear-4k-handle-only-v1"
    assert nx["target"]==ny["target"]==nw["target"]=="Surface Camera Rear Color VideoRecord NV12 3840x2160"
    assert nx["kd_attached_during_session"] is False
    assert ny["KD_breakpoint_attached_during_this_session"] is False
    assert len(nx["phase_results"])==len(ny["phase_results"])==2
    assert [x["frame_handles"] for x in nx["phase_results"]]==[365,366]
    assert [x["valid_rear_4k_frame_handles"] for x in ny["phase_results"]]==[1152,1154]
    assert nx["total_valid_4k_frame_handles"]==731
    assert ny["total_valid_4k_frame_handles"]==2306
    assert all(35000<=x["elapsed_ms"]<=35200 for x in nx["phase_results"])
    assert all(110000<=x["elapsed_ms"]<=110200 for x in ny["phase_results"])
    assert all(x["at_least_12_4k_handles_before_KD_Attempt"] is True and x["stop_succeeded"] is True
               for x in ny["phase_results"])
    assert nx["source_started_and_stopped_twice"] is True
    assert nx["no_camera_pixel_bytes_read_or_saved"] is True
    assert ny["no_optical_pixel_bytes_or_windows_DMA_addresses_stored"] is True
    assert ny["prior_E004nw_KD_session_startasync_succeeded_but_zero_frames"] is True
    assert ny["prior_E004nx_no_KD_valid_4k_frames"]==[365,366]
    assert nw["start_status"]=="Success"
    assert nw["frame_handles"]==nw["valid_4k_frame_handles"]==0
    assert nw["no_pixel_bytes_read_or_stored"] is True
    assert "frame-handle count insufficient" in nw["error"]
    assert nx["BF_event_0x0f_live_during_rear_capture_observed"] is False
    assert ny["BF_event_0x0f_live_recording_observed"] is False
    assert ny["new_Linux_native_rear_4k_ISP_optical_frame_proven"] is False
    assert nx["Linux_native_rear_4k_ISP_optical_frame_proven"] is False
    return True

if __name__=="__main__":
    nx=json.loads((NX/"RESULT.json").read_text())
    ny=json.loads((HERE/"RESULT.json").read_text())
    nw=json.loads((NX/"E004NW-PRIOR-FAILED-REAR4K-SCALAR.json").read_text())
    validate(nx,ny,nw)
    nxs=(NX/"WINDOWS-RUN-SOURCE.ps1")
    nys=(HERE/"hold-rear4k-then-KD-singleentry.ps1")
    assert sha(nxs)==EXPECTED_NX_SOURCE and sha(nys)==EXPECTED_NY_SOURCE
    for p in (nxs,nys):
        src=p.read_text()
        assert "FileMode]::CreateNew" in src
        assert "TryAcquireLatestFrame()" in src
        assert ".Dispose()" in src
        assert "3840" in src and "2160" in src
        assert "SoftwareBitmap.LockBuffer" not in src and "CopyToBuffer" not in src
    assert "TWELVE-VALID-HANDLES" in nys.read_text()
    assert " 110 $reader" in nys.read_text()
    assert " 35 $reader" in nxs.read_text()
    negative=(
      ("prior_zero_start_is_not_failed",lambda a,b,c:c.__setitem__("start_status","Failed")),
      ("prior_no_frames_is_not_4k",lambda a,b,c:c.__setitem__("valid_4k_frame_handles",1)),
      ("nx_replaced_pass1",lambda a,b,c:a["phase_results"][0].__setitem__("frame_handles",0)),
      ("nx_replaced_pass2",lambda a,b,c:a["phase_results"][1].__setitem__("frame_handles",0)),
      ("nx_faked_BF_live",lambda a,b,c:a.__setitem__("BF_event_0x0f_live_during_rear_capture_observed",True)),
      ("nx_faked_KD_connected",lambda a,b,c:a.__setitem__("kd_attached_during_session",True)),
      ("ny_pass1_missing",lambda a,b,c:b["phase_results"].pop(0)),
      ("ny_pass2_wrong_count",lambda a,b,c:b["phase_results"][1].__setitem__("valid_rear_4k_frame_handles",0)),
      ("ny_false_BF",lambda a,b,c:b.__setitem__("BF_event_0x0f_live_recording_observed",True)),
      ("ny_false_KD_attached",lambda a,b,c:b.__setitem__("KD_breakpoint_attached_during_this_session",True)),
      ("ny_false_native_Linux",lambda a,b,c:b.__setitem__("new_Linux_native_rear_4k_ISP_optical_frame_proven",True)),
      ("ny_pixel_export",lambda a,b,c:b.__setitem__("no_optical_pixel_bytes_or_windows_DMA_addresses_stored",False)),
      ("ny_corrupted_12_precondition",lambda a,b,c:b["phase_results"][0].__setitem__("at_least_12_4k_handles_before_KD_Attempt",False)),
      ("ny_BF_prior_wrong",lambda a,b,c:b.__setitem__("prior_E004nw_KD_session_startasync_succeeded_but_zero_frames",False)),
    )
    for name,f in negative:
        a,b,c=copy.deepcopy(nx),copy.deepcopy(ny),copy.deepcopy(nw)
        f(a,b,c)
        try:validate(a,b,c)
        except (AssertionError,KeyError,IndexError):
            pass
        else:raise SystemExit("E004NY_FAIL_OPEN_MUTANT "+name)
    print("E004NX_PRIOR_KD_DETACHED_TWO_PASS_365_366_4K_HANDLES_PASS")
    print("E004NY_PREVERIFIED_12_FRAMES_KD_DETACHED_TWO_PASS_1152_1154_4K_HANDLES_PASS")
    print("E004NW_KD_ARMED_BUT_ZERO_FRAMES_STARTASYNC_SUCCEEDED_COMPARISON_PASS")
    print("E004NY_14_NEGATIVE_TESTS_PASS_LIVE_BF_NOT_PROVEN_NATIVE_LINUX4K_NOT_PROVEN")
