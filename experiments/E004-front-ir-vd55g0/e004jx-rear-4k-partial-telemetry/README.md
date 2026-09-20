# E004jx — bounded partial 4K application cadence and upstream-stall telemetry

2026-09-21. Parent `9960fdf`. **Source-only and camera-free on protected SP11 Golden**. E004jw previously streamed **180 real rear optical frames** but an independently opened 4K V4L2 reader received only **58/90** requested frames before source exhaustion and reader timeout. E004jv's former exact-count-only GStreamer application was terminated by its wrapper before EOS and therefore printed **no final app-sink count or measured wall-clock cadence**. E004jx makes that failure measurable without silently counting a partially received image as a complete frame.

The new standalone `nv12-4k-partial-telemetry-app.py` accepts 1–120 complete 3840×2160 NV12 frames through stdin and pushes them into a bounded real GStreamer `appsrc→queue→videoconvert→I420 appsink`. Exact complete 12,441,600-byte input/sample sizes and synthetic PTS ordering are validated. **The actual appsink callback** records `time.monotonic_ns()` per delivered frame, not the fabricated 30fps PTS, and emits a flushed `E004JX_APP_PROGRESS` line after every ten consumed frames with measured first-to-last wall-clock callback fps. It also reports total callback count, first-to-last fps, p95/max interarrival spacing and an in-memory three-sample pixel-variation flag without saving pixels or emitting image hashes.

To prevent an incomplete upstream from blocking indefinitely, the reader performs bounded, unbuffered pipe `os.read` with `selectors.DefaultSelector`, a configurable **0.1–15-second idle bound per next image fragment** (default 5 seconds), explicit clean EOF detection and refusal of extra bytes after the declared frame bound. If input ends early or stalls, E004jx sends GStreamer EOS for the *already complete* frames, waits for its appsink to finish, prints `PARTIAL FRAMES=N REQUESTED_FRAMES=M INPUT_SHORTFALL_REASON=...` with actual measured callback cadence and exits **nonzero**, so a future camera candidate still fails closed. It never treats an incomplete 4K frame as valid, never labels an app partial result as a complete live 4K30 run, and never opens or controls camera/IR, a V4L2 device, kernel modules or GRUB.

**Six camera-free SP11 Golden tests PASS:** three distinct synthetic NV12 images fully consumed with callback timing and image variation; early EOF after two of three full frames reports a measured two-frame partial failure; a deliberately open but stalled input pipe reports a measured partial result after a 0.2s idle bound rather than hanging; ten fully synthetic frames print an in-flight progress line before EOS; invalid counts/idle settings and trailing payloads fail; and a nonactivation source check verifies no boot/sensor/device control. No raw image files are written. The source SHA-256 is `1e129b385d9d849808eadd1e8b43224e721c19c3bb364513975604d05ce7e0b8`.

**Next use:** a **NEW** uniquely source-locked and automatically Golden-returning candidate may root-copy this tested app and capture its progress/partial lines, alongside independent physical source sequence/timestamp logs, virtual subscriber sequence logs, producer-finished time and start/stop handshake metadata. First diagnose subscriber start, virtual queue backpressure and 4K app throughput separately; do not reuse consumed E004jw, attribute its 58/90 shortfall to an unproven mechanism, or claim successful sustained 4K30. Full Windows-calibrated colour/ISP parity and independent front QC10C decoding remain open.

To replay on protected Golden (no camera is activated):

```bash
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jx-rear-4k-partial-telemetry \
  -p 'test_*.py' -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```
