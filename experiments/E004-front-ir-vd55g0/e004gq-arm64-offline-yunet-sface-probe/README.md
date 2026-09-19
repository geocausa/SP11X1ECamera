# E004gq — actual offline ARM64 YuNet/SFace model inference (PASS; no IR or login)

This stage moves beyond a handwritten facial-recognition algorithm or synthetic vector matching: on **actual SP11 Linux AArch64** we installed OpenCV 4.12.0 into an **isolated temporary Python virtual environment**, downloaded the official OpenCV Zoo YuNet face detector and SFace recognition-model ONNX assets into /tmp, verified their SHA256, and executed both original neural networks. No software was installed into the Golden system Python or kernel. All original third-party models, user-facing images, and binary assets stay out of the camera Git repository.

Official model/documentation sources and license references:

- YuNet: https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet (model/directory licensed MIT)
- SFace: https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface (model/directory licensed Apache 2.0)
- OpenCV's bundled public demo sample: https://github.com/opencv/opencv_zoo/blob/main/models/face_detection_yunet/example_outputs/largest_selfie.jpg (used in memory as an algorithm fixture, not as anyone's enrollment or claimed identity).

**Pinned files in a temporary, untracked cache:** YuNet model SHA256 8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4; SFace model SHA256 0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79; public demo fixture SHA256 ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6. The verifier rejects changed weights, linked assets, substitute images, OpenCV version drift, non-finite/wrong-sized model features and malformed frames.

The exact, **real** YuNet network rejects a blank synthetic 644×604 neutral frame and the official multi-person sample as unsuitable for single-face processing. An isolated face region of that public sample is processed *only in memory*: YuNet detects one face, SFace aligns it using the network's five landmarks and extracts a finite 128-element feature vector. Duplicate same-photo features pass a self-consistency check; neutral three-channel copies of a visible-light gray conversion also reach the feature extractor. These are execution/format tests, **not** a genuine independent-face verification benchmark. Neither a visible-light group photo nor its grayscale conversion establishes how the model performs on VD55G0 near-IR imagery, working in complete darkness, demographics, masks, replay attacks or liveness. No facial identity is named or labeled; no feature/template, raw image or derived match score is written into Git or evidence JSON.

The new `src/sp11-camera-hlos-worker/sp11-offline-face-probe.py` is an unprivileged standalone **diagnostic prototype**. Its in-memory feature and cosine similarity functions are explicitly NOT an authentication decision or login integration. It has no camera access, enrollment store, liveness model, PAM/system unlock, privilege escalation or LED control. The existing E004go one-shot aggregate diagnostic controller remains independent; it is not silently combined with a biometric acceptance path.

## Reproduce on SP11 Golden without camera or firmware interaction

Use only a disposable temporary environment, not root or system pip:

    sh experiments/E004-front-ir-vd55g0/e004gq-arm64-offline-yunet-sface-probe/prepare_offline_assets.sh
    /tmp/sp11-camera-face-venv-20260919/bin/python experiments/E004-front-ir-vd55g0/e004gq-arm64-offline-yunet-sface-probe/verify_result.py

The preparation script installs only into /tmp, fetches the three exact official source URLs, verifies all three pinned SHA256 checksums, rejects modified upstream assets and refuses to run as root. It has no camera, driver, device or login APIs.

Any asset drift fails closed; the URLs are provenance, not an invitation to replace pinned weights with a different model. Downloaded public-photo and face-model bytes are not committed. This stage can be reproduced afresh after a reboot by recreating /tmp assets from the officially published filenames, provided their hashes still match.

**Safety/quality:** No IR emitter has been activated or authorized; no captured user face or consented enrollment was available; no authenticated face match or anti-spoofing has been established. E004fs/E004ge still block native illumination until independent current/irradiance/actual pulse/autonomous off tests are verified on the exact SP11 emitter. This prototype must not be connected to PAM, Windows Hello trust assertions, a login gate or a real camera device on the strength of these offline tests.
