# Full-precision RAW10 pixel interpretation (offline only)

The accepted front and rear RAW-to-NV12 publishers currently extract
only the first four (upper-eight) bytes of each MIPI RAW10 five-byte
group. E004mc/E004md therefore could not verify what the discarded
2-bit planes contain or whether an uncalibrated optical black level
removes the little remaining visible scene signal.

`raw10_unpack.h` is a stand-alone, strict, 10-bit row-pixel primitive
for both front 3840x2160 pRAA and rear 4076x2806 pgAA. It preserves
the low two bits, validates group/stride limits and never opens a device
or changes the accepted output path. Use it as the basis for a fresh
source-pinned, bounded in-memory per-channel source/black-level and
RAW-to-NV12 analysis; do not infer black level, lens occlusion or colour
accuracy from upper-8-bit percentiles alone. No existing Golden or
one-shot live publisher is modified by this offline component.

`raw10_profile.h` adds an in-memory, per-channel (R/G0/G1/B) exact
10-bit histogram, p01/p50/p95/p99, min/max and low-two-bit frequency
sampler for strictly specified native front RGGB3840x2160/4800-stride
and rear GRBG4076x2806/5104-stride frames. It fails closed on unexpected
sensor format, short payload, unknown Bayer phase or unbounded sampling.
Its returned histograms are memory-only: a future camera candidate may
persist a few channel percentiles and bit counts, not image pixels or a
spatial mosaic. These are raw code values, NOT calibrated optical black,
measured lux, recognizable detail, proper white balance or inferred AE.

The maintained direct publishers optionally emit these scalars for
source frames 1/30/90/180/600/630 before requeue via an explicitly
source-pinned `-DSP11_CAMERA_ALLOW_RAW_PROFILE=1` build. Normal builds
compile the instrumentation OUT and still deny real capture unless an
independent fresh one-shot boot token is embedded and verified. The
existing RAW8→NV12 output bytes are NOT changed. Both modes have passed
camera-free fake-device STREAMOFF/lifecycle tests; no physical camera
has yet been accessed with this new diagnostic. Only a fresh isolated
RGB candidate, exact native format guard, IR-off and Golden rollback
may subsequently exercise it on hardware.

An independent pure integer `nv12_range.h` maps the current provisional
full-scale 8-bit Bayer-converted Y/UV codes into nominal studio-range
NV12 with explicit build opt-in. This is NOT optical black-level
calibration or automatic tone/exposure adjustment. Its exhaustive
256-value test and separate SP11 synthetic GStreamer appsrc→RGB test
show the expected range and clipped-near-video-black consumer behavior.
Existing default publisher binary behavior remains byte-identical.
