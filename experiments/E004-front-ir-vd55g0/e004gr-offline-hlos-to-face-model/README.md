# E004gr — maintained SP11 HLOS C pixel pipeline to actual ARM64 face models

PASS, offline and unprivileged. This checkpoint joins two previously separate, reproducibly validated code paths: the actual maintained Windows-oracle-backed Linux HLOS C NV12 processing core and the real OpenCV Zoo YuNet/SFace ARM64 inference model prototype. The bridge is strictly offline and refuses input unless it is one exact 644×604 full-range 8-bit neutral-chroma NV12 frame. No camera, LED, PMIC, SecurePD, enrollment or login service is opened or modified.

## What it proves

- src/sp11-camera-hlos-worker/sp11-offline-nv12-face-bridge.py converts the existing HLOS worker's full-range grayscale luma directly to identical B/G/R channels without video-range YUV brightness remapping. Only length-exact immutable bytes with all neutral 0x80 chroma are accepted. Corrupted UV, truncated/overlong frames and alternate frame objects fail before image output.
- In a temporary build, the real eight-file HLOS C worker compiles, processes an in-memory grayscale 644×604 visible-light crop of OpenCV Zoo's pinned public group-photo fixture, changes luma while keeping neutral chroma, and passes the resulting original-worker output through the strict bridge. Actual YuNet detects exactly one face; actual SFace aligns and extracts a finite 128-element feature in RAM. A repeated identical frame gives a self-consistency diagnostic, not an identity or security result.
- The same maintained C worker passes a whole public multi-face photo and a synthetic blank frame to the same model bridge, and the standalone face probe rejects both. The native C worker rejects short/long NV12 input with no partial output.
- The only real-person pixels are from the upstream OpenCV public demo image, stored strictly outside Git under /tmp. The stage saves no photos, crop, face features, score, claimed identity or personal biometric data. The fixture is reflected visible light, not real near-IR sensor data; no user was enrolled.

## Reproduce on the ARM64 SP11 Golden without devices

    sh experiments/E004-front-ir-vd55g0/e004gq-arm64-offline-yunet-sface-probe/prepare_offline_assets.sh
    /tmp/sp11-camera-face-venv-20260919/bin/python experiments/E004-front-ir-vd55g0/e004gr-offline-hlos-to-face-model/verify_result.py

The preexisting E004gq preparation script installs OpenCV only into an isolated /tmp virtual environment and pins original OpenCV Zoo YuNet/SFace model hashes and the public sample hash. E004gr also pins the C worker's exact source-file bytes, new source/verification scripts, image geometry and strict bridge behavior. All compiled code is temporary and removed after the tests. No kernel patches are installed.

Boundaries: This proves a viable software interface from the native HLOS worker to actual ARM64 face inference, not actual face unlock, Windows Hello/secure-camera parity, performance with genuine VD55G0 illuminated near-IR optical images, unknown-person accuracy, calibrated matching thresholds, anti-spoofing/liveness or trusted camera-to-model provenance. E004fs/E004ge native emitter current, optical irradiance, actual pulse and autonomous host-fault/stuck-strobe cutoff remain BLOCKED. No IR light, camera/PMIC I/O, Windows/KD, Golden or login modification occurred.
