# E004gd — offline end-to-end HLOS signal telemetry on archived generated frames

**PASS (normal and ASan/UBSan), no new hardware access.** This stage advances the E004gc standalone signal diagnostic into the entire existing, byte-pinned Linux camera data path using the **previously archived E004fe sensor-generated pattern**, not new optical or facial imagery. Neither E004fe, E004fu, E004gb nor any other consumed one-shot identity was re-run.

`src/sp11-camera-hlos-worker/test-telemetry-integration.py` SHA-pins the original 16-frame RGB888 archive and every frame's existing SHA; compiles the unchanged RGB888→NV12 bridge, maintained HLOS parity worker and E004gc signal-metrics executable; passes 16 contiguous frames in memory through all three. It checks the established full processed-buffer SHA-256 (`ea414ce89d3fdcf25f834baa3f8d13a1d04b25289ff34dba844a57986db655df`), independently recomputes all six telemetry metrics in Python from each processed frame and requires the C implementation's full JSON reports to match for all sixteen. The sensor pattern is identical in each archived frame and the reports agree for each. Corrupting RGB components or neutral chroma in only the **last** frame and short/long/count mismatch must fail before any downstream data is emitted.

Reproduce from repository root, on SP11 Linux Golden with no camera running:

```sh
python3 src/sp11-camera-hlos-worker/test-telemetry-integration.py
HLOS_SANITIZE=1 ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 python3 src/sp11-camera-hlos-worker/test-telemetry-integration.py
```

The test uses only the original archive and a temporary executable directory; no derived image buffers are written to files, no PMIC register is accessed, no device is opened, no new camera stream, Windows/KD trace, reboot or IR illumination takes place. Numerical pattern metrics are **not a face-quality threshold**, useful low-light imagery, liveness or recognition result. E004fu's real ambient optical frames were deliberately not retained and cannot be retroactively scored by this stage. E004fs independent physical pulse/current/irradiance and host-crash/stuck-trigger fail-safe cutoff remain unproven. Linux emitter OFF and biometric/PAM integration absent.
