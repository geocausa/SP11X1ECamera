# Bounded native RGB publishers

Self-contained source package for the accepted front RAW10 to1080p NV12 and rear RAW10 to4K NV12 publishers. Conversion files are byte-identical copies with committed provenance; native capture/lifecycle remains the E004la implementation. No build-time include depends on experiments or local Windows-derived assets.

Run bash build.sh NEW_OUTPUT_DIRECTORY or bash tests/test.sh. Default binaries deny all live capture, including consumed boot identities. Tests admit only a fake token with linker-wrapped device operations; they do not load modules or access cameras. A future fresh, source-pinned one-shot candidate must explicitly bind its admission token and retain the existing host/boot/manifest/consumption guards. This consolidation grants no production/default activation.

Fixed accepted input/output geometries, strict V4L2 validation,
bounded polls, signals and STREAMOFF checks are retained. Normal/default
builds remain limited to 2400 frames and 210 seconds; a newly guarded
candidate may opt in at **compile time** with
\`-DSP11_CAMERA_ALLOW_CONTINUOUS=1\` and pass the exact argument
\`continuous\` instead of a frame count. That mode has a 4-hour hard
deadline which counts as FAIL rather than a hidden restart; only an
intentional SIGTERM and verified STREAMOFF is a normal
\`STOPPED\`=143 end. It is disabled in normal builds; it has only
camera-free fake-device tests and HAS NOT BEEN physically accepted
as a long-lived SP11 camera service. The owner must preserve the
fresh-boot token guard, closed reader/FD proof and media-neutral
checkpoint before switching or stopping. Do not turn this flag on in
a default Golden build. It remains uncalibrated software processing, not a libcamera pipeline or Windows ISP equivalent. This userspace package is self-contained; the separate hardware/bootstrap package still has its documented local R4 requirement.

Full-precision MIPI RAW10 low-two-bit unpacking is now separately available
for offline analysis under `iq/raw10_unpack.h`; its synthetic-row regression
runs with `tests/test.sh`. It is NOT installed into the accepted live
RAW→NV12 converter, which still discards those bits, and is NOT by itself
evidence of visible scene detail, calibrated black level or ISP parity.

A further source-only optional `SP11_CAMERA_ALLOW_RAW_PROFILE=1` compile
flag records sparse in-memory full-precision Bayer channel statistics
from the SAME captured mmap frame before converter/QBUF, with no RAW
photo export and no default/Golden activation. `rgb/iq/README.md`
describes the strictly bounded diagnostics and their limits.

## Camera-free opt-in NV12 studio-range contract

E004mg private baseline PNGs are effectively black (front downsampled
p99=9, rear=0) despite independent same-boot NV12 app Y p99 27/17.
The existing RAW-upper8 Bayer converter generates full-range luma code
values but the NV12 consumer's video-range conversion treats Y near16 as
black. A SP11-local camera-free synthetic GStreamer test proves NV12
Y=16 and 17 become RGB=0, Y=27 becomes RGB=11 and Y=39 becomes RGB=25.

`rgb/iq/nv12_range.h` provides a bounded integer full8→nominal
video-range Y/UV transform (Y16..235, C16..240), wired into both
maintained front/rear converters ONLY when compiled with
`-DSP11_RGB_NV12_VIDEO_RANGE=1`. Default builds remain binary-exact
against the previously accepted E004mg-era copies with this macro
absent, and the maintained opt-in publisher fake-device lifecycle/STOP
cases and 256-level numeric-range tests pass. An additional standalone
SP11-only camera-free GStreamer test lives at
`rgb/tests/test_nv12_gst_range.py`; it verifies low-level dark values
survive the synthetic studio-range→RGB round trip, without real camera
access. No physical live RGB sensor trial has exercised this option.

This corrects an output-range convention only: no calibrated optical
black reference, supported automatic exposure target, RAW10 bit-depth
processing, proper colour-space conversion or recognizable image is
established. In particular, rear native sensor signal remains weak.
Any physical assessment requires a completely FRESH single-use,
source-pinned, IR-off and Golden-reversible camera candidate; NEVER
rearm the consumed E004mg identity or silently enable this mode for
normal/Golden builds.
