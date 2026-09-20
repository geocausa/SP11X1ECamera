# E004jm — fused rear 4K Bayer→NV12 offline conversion

2026-09-20. Parent: `dba2d7f`. **Source-only work on protected SP11 Golden. No camera/IR power, hardware V4L2, reboot, GRUB modifications, system installation, Windows boot or saved optical video.** This optimizes the E004jl rear 4K software-format prototype, not the hardware camera driver.

## Scope and correctness

The exact existing E004jl format contract remains unchanged: packed rear `pgAA` 4076×2806 Bayer, 5104-byte source stride; parity-preserving crop (118,322) at 3840×2160; bilinear interpolation to 8-bit RGB followed by the existing uncalibrated integer YUV matrix and 2×2 chroma averages; 12,441,600 bytes of NV12 per output frame. The fifth MIPI RAW10 packed byte's two low bits/pixel are still discarded, as in E004jl. **This is not full 10-bit colour processing, OEM-quality demosaicing, an ISP implementation, hardware 4K stream or Windows image-quality parity.**

E004jm fuses each 2×2 output tile into one computation. Instead of redundantly sampling the same mosaic neighbours for each of four independent interpolated RGB pixels, it computes the four original bilinear RGB values from shared neighbouring samples and uses exactly the E004jl Y/U/V rounding and order. Per-row source pointers and a precomputed packed-pixel byte-index table reduce address work without changing image geometry or data exposure. It preserves all existing bounded 1–8-frame input/EOF/TTY checks. No captured optical or output frame files are written.

## Actual SP11 offline verification

- The baseline E004jl C source and E004jm fused C source both compile with GCC `-O3 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off`.
- **8 automated tests PASS**, comparing full output bytes between baseline and fused code for the archived physical rear **hardware colourbar**, two separate nonuniform *synthetic* RAW10-like frames, and two ordered distinct synthetic frames. Also checks bad count, compressed-front-sized input, extra input, output format/GStreamer compatibility and absence of boot/camera activation interfaces.
- Both original and optimized output on the archived colourbar: SHA-256 `42136b93325c8c7d76dbc25deb64740d3b10c33670f486acb0d81b639753f45d` (one 12,441,600-byte NV12 image); nonuniform synthetic frame: SHA-256 `d28f598edd6f5f8691f851419eaae258ea864e2e53111580e4067d931fe91f22`. These prove regression against the original *uncalibrated* colour algorithm only, not true-colour fidelity.
- A separate `-fsanitize=address,undefined` build consumed the archived hardware colourbar, reported no sanitizer fault and reproduced the same output SHA. GStreamer `fdsrc→rawvideoparse(3840×2160 NV12)→videoconvert→fakesink` accepted the result.
- Five isolated colourbar conversions using baseline on this SP11 measured **36.356–40.733 ms per frame**; five fused runs measured **12.148–18.086 ms per frame**. These are non-thermal-controlled, same-machine short run measurements, **not** minimum guaranteed latency, 4K30 or app throughput.
- An 8-frame repeated playback of the **same archived colourbar** (not eight independently captured optical frames), with full raw input and NV12 output redirected to a sink, measured baseline mean conversion **30.732 ms** and 0.26 s wall; fused mean **11.313 ms** and 0.10 s wall. This is a short offline buffer-throughput test only; it excludes actual sensor DMA, camera route lifecycle, V4L2 virtual-device backpressure, recording encoders, displays, long-run CPU throttling and optical image quality. No live 4K hardware stream is claimed.

## Next gates

Keep E004jl's source and fixed output digest as regression authority. Further work needs a source-locked, uniquely consumed and automatically Golden-returning **live rear 4K** camera candidate with an ordinary selectable 4K endpoint, independent consumer frames and measured sustained drop/latency/thermal behaviour, after proving 4K endpoint negotiation and safety in an isolated camera-free test. The previous 1080p E004jh virtual webcam is not silently promoted. Independently unlock front QC10C→actual image or exact safe front ISP linear-Y/C output before attempting front desktop parity; the rear converter is explicitly rear-only. Preserve protected Golden and do not rearm a consumed one-shot.
