# E004hj — same-session ARM64 comparison: original single, original batch and offline stream

**OFFLINE PASS (2026-09-20).** This stage resolves E004hi's single-trial timing ambiguity with **six rotation-balanced comparisons of all three transports in the SAME SP11 Golden ARM64 process/session** using the same original unchanged HLOS C pixel algorithm, original strict neutral grayscale NV12 bridge and actual SHA-pinned OpenCV Zoo YuNet/SFace inference objects (OpenCV 4.12, OMP/OpenBLAS/OpenCV threads all 1). No camera/PMIC/LED/Windows/biometric enrollment/login is opened; no kernel, native IR source or Golden configuration is modified. The separate new offline streaming sidecar from E004hi remains UNINSTALLED.

The original public visible-light OpenCV Zoo demo image (SHA256 `ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6`) is cropped, gray-converted and represented as an **identical 644×604 neutral NV12 frame** repeated eight times in each trial. All three modes produce exactly the same unmodified HLOS C output bytes for each input and yield one ephemeral finite 128-dimensional real model feature for every public fixture. The six cycles rotate execution order among three modes so each mode starts the rotation twice; original C compilation, model initialization, ROI creation and one warmup of each mode are excluded from the timed trials. Total measured real model extractions: **144**, all from repeated copies of the *same* public visible-light frame. There is NO new exposure, sensor cadence, native near-IR imagery, independent live person, spoof-resistance, liveness, secure camera provenance or login acceptance.

## Same-session measured CPU latency (six rotations per mode)

| Transport of eight identical public frames | Median time to first real model feature | Median time until all eight features and successful worker exit |
| --- | ---: | ---: |
| Original maintained C worker, **eight separate processes** | **107.275 ms** | **879.877 ms** |
| Original maintained C worker, **one `--frames 8` whole batch** | **347.804 ms** | **637.374 ms** |
| New **uninstalled bounded stream sidecar**, one persistent process, each frame provisional until DONE | **79.675 ms** | **815.174 ms** |

The new stream had lower **observed median** first-result and full-eight latencies than separate original C launches in this one controlled run, while the original whole-batch transport had lower observed median total-eight latency at the cost of delaying its first result. The stream's total-eight **maximum across these six trials was 958.828 ms**, compared with 901.262 ms for separate launches and 641.773 ms for whole batch; this highlights that the stream's bounded-sample median improvement is **not a guaranteed tail-latency or real-time guarantee**. For `n=6`, nearest-rank p95 is just the highest measured sample, NOT a statistically robust 95th percentile. These particular timings depend on the CPU clock/thermal/scheduling state, compiler, local pipes, model/fixture, and single-thread constraints. This is *not* a native camera FPS comparison, a producer-consumer concurrent pipeline or a declaration of production readiness. Peak RSS of the full test Python process before/after measured rounds was 193040 KiB, not an isolated model's memory footprint.

**Transport decision for the next diagnostic prototype:** preserve the original whole-batch input-atomicity behavior when full-batch completion matters; continue testing the *uninstalled, terminal-commit* per-frame sidecar only as an offline low-first-result-latency candidate. The C stream may produce several provisional earlier outputs before a malformed later frame, but the diagnostic client requires exact `DONE`/EOF/child exit zero and invalidates the whole session if it fails. The original whole-batch C mode emits no partial output for invalid full input. Neither mode can serve as a real biometric verifier, trusted camera security boundary or independent emitter watchdog from these timing results.

## Reproducible bounded run

Use the **existing E004gq original SHA-pinned public assets/models** in `/tmp` and isolated nonroot OpenCV ARM64 venv (re-prepare after reboot if necessary), then run from the camera repository root:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /tmp/sp11-camera-face-venv-20260919/bin/python experiments/E004-front-ir-vd55g0/e004hj-fair-arm64-three-transport-model-profile/benchmark_three.py
python3 experiments/E004-front-ir-vd55g0/e004hj-fair-arm64-three-transport-model-profile/verify_result.py
python3 experiments/E004-front-ir-vd55g0/e004hj-fair-arm64-three-transport-model-profile/test_modes.py
python3 experiments/E004-front-ir-vd55g0/e004hj-fair-arm64-three-transport-model-profile/test_verify_result.py
```

`evidence/RESULT.json` records **only aggregate timing/memory values, original-source/model/protocol hashes, balanced trial orders and negative capability flags**. The verifier checks original maintained C sources, C sidecar/client, strict grayscale bridge, face probe, immutable earlier E004hg/E004hh/E004hi results, balanced rotation and exclusion of authentication/hardware claims without opening any device or model asset. Six malformed timing-statistics cases and **16 evidence-scope mutation cases** fail closed. No public crop, image bytes, model feature, detection/match score or identity is saved.

**Actual SP11 dark-room unlock remains blocked by independently missing evidence:** the original PMIC idle timer byte `0x93` has no established first writer; native emitter current/irradiance, physical pulse and independent held-high/host-failure shutdown are unverified under E004fs/E004ge; real authenticated native near-IR faces, replay-resistant liveness, consented enrollment and Windows Hello-class protected trust are unproven. Native Linux IR/flash patches and PAM/login remain OFF/UNINSTALLED.
