# E004ia — actual original ARM64 C transaction then real pinned public-model feature extraction

**PASS on real SP11 ARM64 protected Golden Linux, 2026-09-20.**
The new UNINSTALLED source-only
src/sp11-camera-hlos-worker/sp11-offline-public-commit-diagnostic.py
combines the E004hz all-or-nothing transaction wrapper, UNCHANGED native
E004hi HLOS C streaming worker/core, UNCHANGED full-range grayscale NV12
bridge and actual pinned YuNet/SFace OpenCV 4.12 diagnostic.

The verifier recreates the existing unprivileged, temporary /tmp OpenCV
environment and **exact SHA-pinned official OpenCV Zoo public example**
and model files; only their existing SHA256 identities are preserved.
No user photo, pixels, face embedding, comparison score or identity is
saved to the repository, result JSON or stdout.

## Explicit model-order boundary

The official **public-photo ROI selection** itself uses a coarse YuNet
detector BEFORE the native C stream transaction. We do NOT claim that
every model inference in the full demo occurs after transaction commit.

The new _committed_model_diagnostic internal function, however, calls
the real processed-frame model factory / performs any processed-frame
feature extraction **only after** the unchanged original native C worker
successfully completes every frame, sends exact DONE, closes stdout with
no trailing bytes and exits zero (enforced in the existing E004hz
transaction wrapper). A late failed worker never constructs or invokes
the processed-frame model. The wrapper returns ONLY a bounded, explicitly
non-authentication diagnostic dictionary; it never returns processed
frames, model feature vectors or similarity scores.

On actual unprivileged SP11 ARM64, completed distinct 2- and 8-frame
transactions of the pinned grayscale public visible-light face ROI
fed the original HLOS C + exact neutral full-range NV12 bridge into
real YuNet face detection/alignment and SFace 128-dimensional
feature extraction. No real SP11 sensor or NIR capture was performed.

## Failure tests

11 negative scenarios on original ARM64 Python and compiled native HLOS
C: five invalid synthetic frame inputs, four disposable fake workers that
emit a seemingly valid first provisional native frame then fail in one
of four distinct ways (late second-frame failure, wrong DONE, surplus
stdout, nonzero child exit), and two failures after a valid native commit
(model construction error and non-finite mock model feature). For the
nine precommit faults, a counted processed-frame mock model factory
and extraction methods are invoked **zero times**. Neither late nor
postcommit failures return a partial frame or feature to the caller.

Before running, existing E004hi and E004hz evidence and original
C/transaction/bridge/face source hashes are independently verified.
Original maintained C and Python transport sources are NOT modified;
all new code remains source-only and uninstalled.

Reproduction (only on protected Golden SP11; no native IR emission):

    sh experiments/E004-front-ir-vd55g0/e004gq-arm64-offline-yunet-sface-probe/prepare_offline_assets.sh
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /tmp/sp11-camera-face-venv-20260919/bin/python experiments/E004-front-ir-vd55g0/e004ia-public-model-after-commit/verify_committed_model.py
    python3 experiments/E004-front-ir-vd55g0/e004ia-public-model-after-commit/verify_result.py

**Not a production camera or login milestone:** no real VD55G0
illumination/optical/current/irradiance or host-failure automatic emitter
cutoff evidence, live frame provenance, liveness/anti-spoofing, consented
enrollment, biometric authentication, PAM/login or Windows Hello parity.
Temporary Python/OpenCV memory is not securely erased. Native IR emitter
and protected login configuration remain OFF/unchanged.
