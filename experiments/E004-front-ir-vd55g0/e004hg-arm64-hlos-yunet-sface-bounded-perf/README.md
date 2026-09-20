# E004hg — bounded actual ARM64 HLOS C → real YuNet/SFace CPU costs (OFFLINE PASS)

**2026-09-20.** After E004hf narrowed the original OEM fixed timer-helper path without identifying the first actual PMIC timer writer, this independent, **no-emission** stage measures the actual already maintained native Linux HLOS C worker → full-range neutral-NV12-to-BGR bridge → original pinned OpenCV YuNet face detector and SFace embedder on the SP11 ARM64 CPU. This is the same real cross-language model code verified once in E004gr, now with fresh CPU cost data. It is NOT an SP11 IR face image, a new camera stream, a biometric authentication session, enrollment or an optical/PMIC safety test.

A **public visible-light OpenCV Zoo demonstration photo** is verified against original SHA256 `ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6`. The same isolated public grayscale face ROI is converted in RAM to 644×604 neutral NV12, processed by the compiled actual maintained HLOS C worker once for each trial and bridged by the strict full-range luma-preserving converter. The actual YuNet and SFace models run on the resulting HLOS-processed pixel array; each ephemeral output must have one face and finite shape (1,128). **The same input is repeated eight times:** it cannot measure capture cadence, face change, sample freshness, real-user recognition accuracy, anti-spoofing or liveness. No source image, NV12/BGR pixels, detection metadata, embedding, match score or identity is logged or committed. A separate one-time model-init clock is excluded from each measured per-frame latency.

Original pinned assets and runtime: `opencv-python-headless==4.12.0.88` (OpenCV 4.12.0), original E004gq YuNet/SFace ONNX hashes, original maintained HLOS C from eight C sources compiled `clang -O2` into an **uninstalled, automatically deleted temporary executable**; original public photo and model weights in `/tmp` only. Both `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` and `cv2.setNumThreads(1)` are explicitly checked. No system pip, kernel/firmware, camera, PMIC, Windows, KDNET, emitter or login changes.

## Measured on this protected SP11 Golden boot

| Actual sequential operation | Eight measured identical-public-fixture trials, median | Nearest-rank p95 (for n=8, the maximum) |
| --- | ---: | ---: |
| New HLOS C worker process, including start/input/output and maintained C computation | **47.888 ms** | 49.020 ms |
| Strict exact-luma neutral NV12→three-channel BGR bridge | **1.616 ms** | 2.263 ms |
| Actual YuNet detect + SFace alignment and finite 128-dimensional feature extraction | **58.846 ms** | 62.451 ms |
| Complete sequential single frame from C worker launch through model output | **109.328 ms** | **111.321 ms** |

The one-time model-object initialization was **53.465 ms** after Python/OpenCV had loaded and *not included in the per-frame samples*. CPython `ru_maxrss` was **188172 KiB** before and after the timed trials; this is the entire testing Python process's peak resident memory, not a per-model allocation measurement and not a production memory budget. These measurements apply to this exact CPU/OS/compiler/model fixture and this warm, restricted single-thread run only. With only eight repeated frames, nearest-rank 95th percentile is the maximum observed frame time; this is NOT a statistically robust tail-latency or steady-camera FPS estimate. Initial preparation, model downloads, C compilation and sample-photo ROI extraction are excluded from measured per-frame time. The C worker launches in a fresh subprocess **for each trial**, so the observed ~48-ms C step includes process startup; avoid treating all of it as irreducible HLOS compute time. A future persistent worker/batched transport should be benchmarked separately without claiming liveness from repeated input.

## Reproduce and verify

On SP11 Golden, after the ordinary camera-idle/repository guard, use the non-root isolated asset preparation from E004gq if the temporary venv/models have been cleared by a reboot. No system packages are modified:

```sh
sh experiments/E004-front-ir-vd55g0/e004gq-arm64-offline-yunet-sface-probe/prepare_offline_assets.sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /tmp/sp11-camera-face-venv-20260919/bin/python experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf/benchmark_offline.py
python3 experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf/verify_result.py
python3 experiments/E004-front-ir-vd55g0/e004hg-arm64-hlos-yunet-sface-bounded-perf/test_benchmark.py
```

The source-hash-pinned result is in `evidence/RESULT.json`; `verify_result.py` verifies the exact source/model integration evidence, all timing fields and the explicit negative authentication/hardware scope WITHOUT requiring temporary model assets. `test_benchmark.py` exercises six malformed timing-sample cases and checks that repeated public input is never promoted to liveness, actual NIR recognition or authentication. No command starts camera capture, issues SPMI/PMIC commands, enables Linux flash or mutates Golden.

**Next independent development:** reduce per-frame host overhead via a carefully isolated persistent/IPC C worker and compare actual YuNet/SFace CPU cost under a real bounded diagnostic session; later obtain consented, provenance-confirmed native NIR frames and liveness/biometric validation **only after separate hardware and privacy prerequisites**. E004fs/E004ge optical/electrical autonomous fault-off gate remains BLOCKED. Native Linux IR emitter, enrollment and PAM/login stay OFF. E004hf's original `0x93` timer-register first-writer remains UNKNOWN.
