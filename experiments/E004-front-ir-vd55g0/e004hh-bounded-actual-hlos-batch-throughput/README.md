# E004hh — unchanged bounded 8-frame HLOS C batch vs 8 process launches with real models

**OFFLINE PASS (2026-09-20), real SP11 ARM64, protected Golden unchanged.** This stage follows E004hg's measured single-frame CPU cost and tests an **existing** transport capability in the actual maintained `src/sp11-camera-hlos-worker/sp11-hlos-ir.c`: `--frames 8` performs one bounded subprocess invocation that receives **exactly eight full 644×604 NV12 frames**, validates the *entire input/EOF*, executes the same original C pixel core eight times, and returns all eight complete frames **only after all eight were processed**. No new C worker or kernel/PMIC/camera device is deployed.

We compare that original all-at-once batch with eight consecutive launches of the same maintained C worker using the **exact same repeated public OpenCV Zoo visible-light grayscale face ROI** (original pinned photo SHA256 `ab8413ad9bb4f53068f4fb63c6747e5989991dd02241c923d5595b614ecf2bf6`). The original exact HLOS pixel outputs are verified **byte-for-byte identical** in single and batch modes, including neutral UV. Each is converted by the strict full-range NV12 grayscale bridge and processed by the same original pinned OpenCV 4.12 YuNet detector and SFace recognizer on SP11 ARM64; all 64 measured real model runs return ephemeral finite (1,128) features. No frame/photo, facial feature, score, claimed identity or private biometric data is persisted. Model initialization, public fixture generation, C compilation, and one warmup pair were excluded from timed sessions. CPU threads for OpenCV, OpenBLAS and OMP were all limited to one, and the four measured mode pairs alternate which mode runs first.

## Observed trade-off on this one Golden CPU session

| Eight repeated public-frame operation | Eight fresh C processes (median of four runs) | One original C `--frames 8` process (median of four runs) |
| --- | ---: | ---: |
| Time spent in actual maintained HLOS C invocations | **362.453 ms** | **278.794 ms** |
| Time until *first* public sample's real model feature is ready | **82.220 ms** | **344.158 ms** |
| Total elapsed time until all eight real public sample features are ready | **817.692 ms** | **634.121 ms** |

A batch therefore reduces repeated process-launch/IPC overhead in this limited workload and reduces time to **all eight** processed model features, but incurs **much higher first-result latency** because original C's whole-batch semantics withhold all output until all input is validated and processed. It is NOT a persistent streaming worker, not a proposed interactive unlock design, not a measured 60-fps sensor stream, and not evidence that every deployment benefits from batching. With just four paired runs, nearest-rank p95 is the single observed maximum per mode and is not a reliable production tail-latency prediction. Whole-test Python peak RSS before/after measured pairs: **192148/198284 KiB** (entire process, not model allocation). Extrapolating these public-image timing measurements to true illuminated VD55G0 NIR image quality, secure-camera cost, end-to-end capture scheduling, liveness or biometric accuracy would be incorrect.

**Original C input atomicity:** with `--frames 8`, both a truncated eighth frame and an overlong ninth byte are rejected with nonzero exit and **zero stdout**, rather than leaking a partially processed batch. The malformed-input test runs only the compiled unmodified C worker with synthetic public-fixture byte strings in a temporary sandbox. This stronger **input batch contract** does not provide an independently operating hardware watchdog, anti-spoofing or capture provenance. Repeating an identical public photo eight times cannot establish frame freshness or liveness.

Run the isolated original E004gq temporary asset preparation if needed, then:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /tmp/sp11-camera-face-venv-20260919/bin/python experiments/E004-front-ir-vd55g0/e004hh-bounded-actual-hlos-batch-throughput/benchmark_batch.py
python3 experiments/E004-front-ir-vd55g0/e004hh-bounded-actual-hlos-batch-throughput/verify_result.py
python3 experiments/E004-front-ir-vd55g0/e004hh-bounded-actual-hlos-batch-throughput/test_batch.py
python3 experiments/E004-front-ir-vd55g0/e004hh-bounded-actual-hlos-batch-throughput/test_verify_result.py
```

The archived CPU timing result `evidence/RESULT.json` pins the original maintained HLOS C source, previous E004hg proof, strict BGR bridge, face probe, official public fixture, four paired single/batch timing groups, total 64 **public fixture** model extractions and explicit non-authentication flags. Offline verification needs no model assets or camera. Six malformed CPU-statistics negative cases and **13 in-memory evidence-scope negative cases** pass. No images, embeddings, model binary, OpenCV package, proprietary OEM PE or hardware logs are committed.

**Next software development:** a strictly isolated, bounded *persistent* HLOS worker could offer both low first-result latency and reduce per-frame process-start overhead; implement explicit frame framing, no partial output on malformed frames, terminal-fault/no-rearm semantics and process teardown before considering its use with any sensor. The existing offline controller has no autonomous watchdog: nothing in this stage changes that. The PMIC idle timer value `0x93` still has **no identified first writer**, and E004fs/E004ge independently verified emitter current/irradiance/pulse/autonomous fault-off remains BLOCKED. Native Linux emitter, camera, enrollment and login/PAM stay OFF.
