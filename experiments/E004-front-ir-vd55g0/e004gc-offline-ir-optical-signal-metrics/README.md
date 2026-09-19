# E004gc — offline IR image signal telemetry (PASS; no camera runtime)

This is a fresh, **offline-only** HLOS diagnostic continuation after consumed E004gb. It does not reuse E004gb's Windows boot, KDNET session, capture or one-shot identity, and does not reuse E004fu's consumed Linux camera identity. It is not a replacement for the still-BLOCKED E004fs electrical/optical emitter gate.

The new `src/sp11-camera-hlos-worker/sp11-ir-signal-metrics.c` takes strictly 1..16 contiguous 644×604 NV12 frames via stdin; all chroma samples must be neutral 128. It verifies **the complete bounded batch before writing stdout**, then emits JSON containing only per-frame aggregate luma/contrast diagnostics: mean ×1000, 10th/90th percentile, fraction of very dark/bright pixels in permille, and mean horizontal/vertical neighbor absolute difference ×1000. It holds the input only in process memory and explicitly overwrites its input and histogram buffers before releasing them; stdout does not contain pixel data or images. It is intentionally not a generic color converter or a live camera application.

The synthetic regression includes black, flat dim, alternating clipped, horizontal-gradient and mixed frame-order cases; 16-frame maximum; negative tests for early EOF, overlength, invalid count, and invalid first/last-frame neutral chroma. Invalid batches are required to fail without producing partial telemetry. `HLOS_SANITIZE=1` runs AddressSanitizer and UndefinedBehaviorSanitizer over the actual compiled C implementation. Existing HLOS full-frame Windows-oracle and 16-frame archived-pattern bridge regressions also pass unchanged. See the source/test SHA-256 and discrete results in `evidence/RESULT.json`.

From the repository root, reproduce offline:

```sh
python3 src/sp11-camera-hlos-worker/test-signal-metrics-offline.py
HLOS_SANITIZE=1 python3 src/sp11-camera-hlos-worker/test-signal-metrics-offline.py
bash src/sp11-camera-hlos-worker/test-offline.sh
bash src/sp11-camera-hlos-worker/test-bridge16-offline.sh
```

**Interpretation boundary:** These metrics quantify signal characteristics, **not** whether a recognizable face is present, identity, liveness or usable image quality. No threshold is currently validated against real faces. The E004fu low-contrast optical frames were intentionally not retained, so this stage does not claim it has analyzed their pixels. No emitter, PMIC access, camera stream/boot, Windows session, enrollment, PAM/login modification, or Golden changes occurred. E004fs remains BLOCKED until independent physical pulse/current/irradiance and autonomous fault-off evidence establishes a safe Linux illumination envelope. An ordinary HLOS camera+face matcher would have a different, weaker trust model than Windows Hello's protected capture path; do not represent this stage as Windows Hello parity.
