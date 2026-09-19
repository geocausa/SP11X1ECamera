#!/usr/bin/env python3
"""E004gq: unprivileged OFFLINE YuNet/SFace diagnostic, not an authenticator.

The only purpose is to prove ARM64 model inference, one-face isolation,
alignment and finite embeddings. No camera or LED access; no enrollment,
storage, anti-spoofing, PAM/login or authentication decision.
"""
from pathlib import Path
from hashlib import sha256
import math

DETECTOR_FILE="face_detection_yunet_2023mar.onnx"
RECOGNIZER_FILE="face_recognition_sface_2021dec.onnx"
MODEL_SHA256={
    DETECTOR_FILE:"8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
    RECOGNIZER_FILE:"0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79",
}
MAX_PIXELS=2048*2048

class ProbeRejected(Exception):
    """No image contents, model features, confidence or identity in errors."""

def _sha(path):
    digest=sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()

class OfflineFaceProbe:
    __slots__=("_detector","_recognizer","_cv","_np")

    def __init__(self,model_dir):
        root=Path(model_dir)
        for name,pinned in MODEL_SHA256.items():
            file=root/name
            if not file.is_file() or file.is_symlink() or _sha(file)!=pinned:
                raise ProbeRejected("offline model unavailable or changed")
        import cv2
        import numpy as np
        if cv2.__version__!="4.12.0":
            raise ProbeRejected("unvalidated offline OpenCV version")
        try:
            self._detector=cv2.FaceDetectorYN.create(
                str(root/DETECTOR_FILE),"",(320,320),
                0.87,0.3,5000)
            self._recognizer=cv2.FaceRecognizerSF.create(
                str(root/RECOGNIZER_FILE),"")
        except cv2.error as exc:
            raise ProbeRejected("offline model load rejected") from exc
        self._cv=cv2
        self._np=np

    def extract_one_face(self,image):
        """Ephemeral model feature in RAM, never a biometric authorization."""
        cv=self._cv
        np=self._np
        if (type(image) is not np.ndarray or image.dtype!=np.uint8 or
            image.ndim!=3 or image.shape[2]!=3 or
            image.shape[0]<32 or image.shape[1]<32 or
            image.shape[0]*image.shape[1]>MAX_PIXELS):
            raise ProbeRejected("invalid offline BGR frame")
        image=np.ascontiguousarray(image)
        try:
            self._detector.setInputSize((image.shape[1],image.shape[0]))
            _,faces=self._detector.detect(image)
        except cv.error as exc:
            raise ProbeRejected("offline detection failed") from exc
        if faces is None or len(faces)!=1:
            raise ProbeRejected("offline frame must contain exactly one detected face")
        if (faces.shape!=(1,15) or not np.isfinite(faces).all() or
            float(faces[0,14])<0.87):
            raise ProbeRejected("invalid offline detection metadata")
        x,y,w,h=(float(v) for v in faces[0,:4])
        if not (w>0 and h>0 and x>=0 and y>=0 and
                x+w<=image.shape[1]+1 and y+h<=image.shape[0]+1):
            raise ProbeRejected("face geometry outside frame")
        try:
            aligned=self._recognizer.alignCrop(image,faces[0])
            feature=self._recognizer.feature(aligned)
        except cv.error as exc:
            raise ProbeRejected("offline alignment or feature extraction failed") from exc
        if (type(feature) is not np.ndarray or feature.shape!=(1,128) or
            feature.dtype!=np.float32 or not np.isfinite(feature).all()):
            raise ProbeRejected("invalid offline feature")
        return feature

    def similarity_diagnostic_only(self,feature_a,feature_b):
        """Scalar self-consistency diagnostic, NOT a match/identity decision."""
        np=self._np
        for feature in (feature_a,feature_b):
            if (type(feature) is not np.ndarray or feature.shape!=(1,128) or
                feature.dtype!=np.float32 or not np.isfinite(feature).all()):
                raise ProbeRejected("invalid offline feature input")
        try:
            value=float(self._recognizer.match(
                feature_a,feature_b,self._cv.FaceRecognizerSF_FR_COSINE))
        except self._cv.error as exc:
            raise ProbeRejected("offline feature comparison failed") from exc
        if not math.isfinite(value) or not (-1.00001<=value<=1.00001):
            raise ProbeRejected("invalid offline comparison")
        return value

    @staticmethod
    def diagnostic_result():
        return {
            "kind":"offline-raw-model-diagnostic-only",
            "native_ir_emitter_activated":False,
            "real_sp11_nir_face_capture_validated":False,
            "face_recognition_accuracy_or_liveness_proven":False,
            "consented_user_enrolled":False,
            "login_or_unlock_authorized":False,
            "autonomous_hardware_cutoff_proven":False,
        }
