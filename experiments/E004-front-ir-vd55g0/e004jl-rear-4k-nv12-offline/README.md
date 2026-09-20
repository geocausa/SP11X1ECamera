# E004jl — rear 4K NV12 offline delivery feasibility, not 4K camera parity

2026-09-20. Parent `725a1d4`. Scope: **source-only, protected Golden**. No reboot, sensor power, camera module, V4L2 device, image export, kernel, GRUB, Windows boot or IR illumination. New code and all execution on **SP11**.

## Why this gate matters

E004jk measured 45 CPU-accessible Windows rear **3840×2160 NV12 VideoRecord** frame handles, while E004jh previously proved only a temporary **1920×1080** selectable Linux rear video endpoint. The front Windows default video is **1920×1080 NV12** and Linux front still supplies only compressed QC10C. Advertised 30 fps is not sustained measured cadence; the Windows 4K frame acquisition also does not prove distinct frames or image-quality equivalence.

This experiment creates a separate fixed-format **3840×2160 NV12** source-only converter, using an archived SP11 rear **hardware colourbar** fixture, to resolve whether the established `pgAA` 4076×2806 Bayer producer format can produce a buffer satisfying the Windows 4K *dimensions and pixel-format* application contract. It does **not** prove a live rear 4K V4L2 webcam, 4K native hardware ISP, colour equivalence, real scene detail, 4K in-app recording, or 30fps sustained delivery.

## Source, algorithm and output boundaries

`rear-bayer-to-nv12-4k.c` is a bounded stdin→stdout C11 converter. It admits **1–8 exact** complete 14,321,824-byte rear GRBG10p frames and requires EOF immediately afterward; invalid counts, truncated input, front QC10C-size data, extra bytes and terminal raw-pixel I/O fail. With a full input, it creates **12,441,600 bytes per frame** of NV12 at 3840×2160: centered 3840×2160 crop at (118, 322), preserving even GRBG parity and one-pixel interpolation halo within 4076×2806.

It uses the upper 8 bits of each MIPI RAW10 sensor pixel, bilinear Bayer interpolation at **each output pixel**, a deliberately uncalibrated integer YUV colour proxy and 2×2 averaged chroma. This is distinct from E004iu's 1920×1080 nearest-tile preview and does not merely stretch that lower-resolution preview into a 4K buffer. It still lacks OEM colour matrices, lens correction, adaptive demosaic, noise reduction, sharpening, exposure/white balance management and matched Windows reference pixels. Conversion-time measurement covers **conversion only**; neither start-to-screen latency nor 30fps sustainability is established. Output raw pixels remain transient in private pipes; only a test-pattern digest, not the original pattern or an optical frame, is recorded.

The existing E004jh temporary 1080p virtual webcam is **untouched**. The 4K converter is **not** installed, wired into V4L2, or attached to either camera. Never label this experimental NV12 output as a native 4K ISP stream or front-camera data.

## Observed checks on SP11 Golden

- Golden overlap guard PASS before work: Golden saved GRUB entry, no next boot, no camera modules/nodes/processes and tracked repository clean.
- Strict GCC `-O3 -Wall -Wextra -Werror -pedantic` compile PASS.
- **7 Python tests PASS**: bounds, QC10C/truncation rejection, excess input rejection, archived physical rear colourbar complete 4K output SHA, two *synthetic* distinct frames, GStreamer 4K NV12 `fdsrc→rawvideoparse→videoconvert→fakesink`, and no camera/boot APIs.
- An archived real-hardware **test pattern only** (not a current optical scene) produced one complete 12,441,600-byte 3840×2160 NV12 frame SHA-256 `42136b93325c8c7d76dbc25deb64740d3b10c33670f486acb0d81b639753f45d`, accepted by installed GStreamer. A separate `-fsanitize=address,undefined` compile and colourbar replay reported the same SHA, no sanitizer report.
- One optimized offline colourbar conversion measured **36.840 ms** and a separate run **60.099 ms** (non-sustained, varying with operating conditions); sanitizer-instrumented conversion measured **213.947 ms**. At least the 36.840-ms isolated run already exceeds the 33.333-ms 30fps frame period; do not claim 4K30 throughput or image parity.

To replay (does not write any image files):

```bash
python3 -m unittest discover -s experiments/E004-front-ir-vd55g0/e004jl-rear-4k-nv12-offline -p test_rear_4k.py -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

## Next gates

1. First produce matched **private Windows 4K pixel-reference and Linux sensor-scene captures** and define calibration/scene-detail metrics. The present Windows E004jk reference is **buffer metadata only**.
2. Improve the rear pipeline's colour and temporal processing and measure **sustained** 4K frame conversion/publishing with backpressure, latency, dropped frames and power, without altering the protected Golden boot.
3. Only after source/format, bounded runtime and Golden-return gates are sound, attempt a **new unique** one-shot candidate with a real rear 4K virtual endpoint. Do not reuse any consumed E004 one-shot identity, change persistent boot defaults, or enable IR.
4. Independently recover front QC10C correctly or prove safe true-linear front ISP output before any front NV12 webcam claim.
