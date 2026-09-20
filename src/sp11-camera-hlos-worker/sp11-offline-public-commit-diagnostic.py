#!/usr/bin/env python3
"""E004ia: public-image OFFLINE model diagnostic *after* native C stream commit.

NOT a camera driver, authenticator, biometric enrollment, near-IR test,
liveness check, PAM/login integration or independent emitter safety watchdog.
Only public OpenCV Zoo example photo and exact pinned model assets are used.
No raw images, scores, model features or identity leave RAM as result metadata.
"""
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CORE=ROOT/"src/sp11-camera-hlos-worker"
HG=ROOT/"experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf"

def _load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise RuntimeError("offline diagnostic dependency unavailable")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

tx=_load(CORE/"sp11-offline-transaction.py","e004ia_unchanged_transaction")
bridge=_load(CORE/"sp11-offline-nv12-face-bridge.py","e004ia_unchanged_bridge")
face=_load(CORE/"sp11-offline-face-probe.py","e004ia_unchanged_face_probe")
hg=_load(HG/"benchmark_offline.py","e004ia_pinned_public_fixture")
class DiagnosticFault(Exception):
    """Sanitized rejection; no pixels, face confidence, feature or score."""

def _committed_model_diagnostic(worker,frames,probe_factory,max_seconds):
    """Internal test seam: no processed-frame probe/extract before full C commit.

    The model factory is accepted only by this internal offline function for
    testing gate order; even a caller-supplied mock never receives a login
    decision or an authentication-capable result.
    """
    if type(frames) is not tuple or not 1<=len(frames)<=8:
        raise DiagnosticFault("offline demo count out of bounds")
    try:
        output,receipt=tx.process_offline_frames(worker,frames,max_seconds=max_seconds)
    except tx.TransactionFault:
        raise DiagnosticFault("offline processing transaction rejected") from None
    if not (type(output) is tuple and len(output)==len(frames) and
            receipt.get("status")=="complete" and
            receipt.get("frames_checked")==len(frames) and
            receipt.get("login_or_unlock_authorized") is False and
            receipt.get("native_ir_emitter_activated") is False):
        raise DiagnosticFault("offline transaction completion receipt invalid")
    try:
        # Critical order: processed-frame probe construction and extraction
        # follow successful native C IPC commit. Public fixture preparation
        # separately uses a coarse detector BEFORE this transaction.
        probe=probe_factory()
        np=bridge.np
        for payload in output:
            bgr=bridge.nv12_full_range_gray_to_bgr(payload)
            feature=probe.extract_one_face(bgr)
            if (type(feature) is not np.ndarray or
                feature.shape!=(1,128) or feature.dtype!=np.float32 or
                not np.isfinite(feature).all()):
                raise DiagnosticFault("offline model feature rejected")
            del feature,bgr
    except Exception:
        raise DiagnosticFault("offline committed public model diagnostic rejected") from None
    finally:
        # No strong references retained to the processed output tuple after
        # return, but Python memory is NOT securely erased.
        del output
    return {
        "kind":"public-visible-light-offline-model-diagnostic-only",
        "status":"complete",
        "frames_checked":len(frames),
        "processed_frame_feature_inference_only_after_native_C_transaction_commit":True,
        "temporary_model_features_or_frame_pixels_returned_or_persisted":False,
        "native_live_camera_frames_validated":False,
        "near_ir_illuminated_or_darkness_face_tested":False,
        "face_identity_or_anti_spoofing_proven":False,
        "real_user_enrolled_or_authenticated":False,
        "login_or_unlock_authorized":False,
        "native_ir_emitter_activated":False,
        "autonomous_hardware_emitter_cutoff_proven":False,
    }

def run_pinned_public_demo(worker,model_dir,*,count=2,max_seconds=40.0):
    """Only known public photo + checksum-pinned offline models, no user data."""
    if type(count) is not int or not 1<=count<=8:
        raise DiagnosticFault("offline public demo count out of bounds")
    import cv2
    import numpy as np
    if cv2.__version__!="4.12.0":
        raise DiagnosticFault("offline model runtime changed")
    cv2.setNumThreads(1)
    if cv2.getNumThreads()!=1:
        raise DiagnosticFault("offline model CPU budget not bounded")
    # SHA-pinned public example ROI preparation uses a separate detector
    # before native C; do not claim ALL model inference follows C commit.
    source=hg.public_only_nv12(cv2,np)
    if type(source) is not bytes or len(source)!=tx._original.FRAME_LEN:
        raise DiagnosticFault("offline public example geometry changed")
    return _committed_model_diagnostic(
        worker,tuple(source for _ in range(count)),
        lambda:face.OfflineFaceProbe(model_dir),max_seconds)
