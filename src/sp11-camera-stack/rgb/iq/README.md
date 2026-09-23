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

## E004mp read-only native exposure envelope and source quantile gate

`exposure_envelope.py` is an **offline-only** interpretation and validator
for the immutable E004mp scalar `RGB-SELECTOR-ACCEPTANCE.json` and
`RAW10-AND-PRIVATE-RGB-SCALAR-COMPARISON.json`. It cannot open camera
nodes, images or hardware-control APIs. It checks exact front/rear
native baseline, candidate trial and restored controls; recorded native
control bounds and steps; fixed IMX681 frame-length3554/margin4 and
OV13858 frame-length3214/margin8; ordered four-channel RAW10 quantiles.
It **refuses** to interpret p01 as calibrated optical black, to infer
recognizable scene from histograms, or to approve additional gain,
exposure, VBLANK/FPS, auto-exposure or live tone-map writes before
independent optical target and dark/noise evidence. For E004mp the
trial leaves only 4 front and 6 rear exposure lines under the accepted
frame timing: this is not the much larger front hardware-advertised
exposure max. The rear G0 p01 shift64→73 under gain makes an arbitrary
fixed code64 subtraction unsafe.

Run `python3 src/sp11-camera-stack/rgb/iq/exposure_envelope.py
--selector-json /path/to/E004mp/evidence/RGB-SELECTOR-ACCEPTANCE.json
--scalar-json /path/to/E004mp/evidence/RAW10-AND-PRIVATE-RGB-SCALAR-COMPARISON.json`.
Stdout is scalar JSON only; six camera-free refusal/acceptance tests
are integrated with maintained `rgb/tests/test.sh`. It is strictly a
read-only diagnostic, NOT an automatic controller or permission to
write sensor registers. No Golden or consumed one-shot binary changes.

## Experimental TWO-FRAME full10 green temporal/spatial aggregate (offline)

`raw10_temporal_spatial.h` is a separate **camera-free** primitive for
exact front RGGB3840x2160/4800-stride or rear GRBG4076x2806/5104-stride
MIPI RAW10 payloads. It requires two distinct complete private in-memory
frames from the SAME Bayer format and a bounded stride/step, samples
both physical green sites of each selected 2x2 block retaining low
RAW10 bits, and returns **only global numerical aggregates**: frame
means/sample standard deviations, 12x16 tile-mean aggregate spread,
scalar spatial Pearson correlation, pixel-aligned green mean delta,
absolute delta and temporal delta RMS. Each frame's per-tile sums are
stored only transiently on the process stack and NEVER included in
its output. The primitive contains no device, image file, boot,
control or network operation and is NOT compiled into live publishers.

This prepares the *next* source-locked guarded one-shot to distinguish
spatially stable patterns from changing noise/flicker when consecutive
same-control RAW10 frames and a fixed lit/dark target are genuinely
available. **No such temporal RAW10 acquisition or dark-reference
calibration has been performed yet.** A constant synthetic fixed
pattern yields perfect spatial correlation but proves no optical
scene detail: stable sensor FPN, flicker, camera motion or changes in
lighting can contaminate either statistic. Never infer image quality,
calibrated black/SNR or approve gain/AE/tone mapping from these values
alone. The front/rear synthetic zero-noise, fixed-pattern, checker-jitter
and fail-closed geometry tests run camera-free with `rgb/tests/test.sh`.

## Read-only exploratory rear NV12 preview-tone curve (E004mr)

`rear_preview_tone.h` is a **pure in-memory, opt-in** bounded 4K rear
NV12 VIDEO-RANGE Y-only candidate. The maintained release and protected
Golden camera have NO tone integration and NO extra camera authorization.
Only an independent NEW source-pinned one-shot may opt in. For a
verified 3840x2160 full NV12 buffer, a sparse p01/p50/p99 Y histogram
requires input p01 in20..50, p99<=65, and p99-p01>=8. Nearly uniform
unilluminated/baseline and already bright scenes are passed through
unchanged. When enabled, output Y = clamp(125 + 3.5*(inputY-p01),16,235),
while preserving every UV/chroma byte and the full original RAW source.
This exploratory display mapping does NOT set native sensor exposure,
change gain/FPS/IR, infer black, prove scene detail/colour, or implement
OEM Windows ISP/AE. The y=125 anchor and slope3.5 are display heuristics
for the observed E004mp rear gain sample (app p01≈33, p99≈48), NOT
physical measurements of light or calibrated black. A positive pixel
spread may be fixed-pattern noise and should NEVER be accepted as
recognized scene.

Synthetic front-safe/dark-flat/bright-scene/refused-geometry/gated-gain
video-range and UV-preservation tests run camera-free as part of
`rgb/tests/test.sh`. E004mr additionally source-locks an isolated rear
only build using explicit SP11_RGB_NV12_VIDEO_RANGE=1 AND
SP11_RGB_REAR_PREVIEW_TONE=1 with an exact NEW boot token. The default
maintained converter is unchanged. Any actual optical PNGs stay local
SP11, not Git/chat/another device.

## Camera-free default-OFF rear 4K temporal preview prototype

rear_temporal_preview.h implements a separate, opt-in, one-prior
filtered-Y-frame luma temporal filter for ONLY exact 3840x2160 NV12 video
range. The maintained front/rear publishers, Golden camera,
native sensor/IR controls and ordinary application output remain UNCHANGED.
A new independently source-pinned candidate must explicitly call the
primitive; it never opens a device, allocates a frame, saves pixels,
changes UV/colour, touches RAW10 or delays source frames. Its caller
supplies and clears one private previous-filtered-Y buffer, source
sequence/timestamp, a nonzero caller-selected epoch (NOT native sensor
control readback), and the actual already-opted-in tone gate.
No tone -> reset/no transform; the first active frame seeds the
private prior Y without altering output. Dropped/out-of-order/slow
frames, changed epoch, large median shift or widespread pixel changes
reset history and copy current without blending. Stable 2x2 blocks
with all four pixel differences no greater than eight display Y
blend current/previous 50:50; high-contrast motion blocks bypass.
UV bytes are unchanged.

This is NOT calibrated motion segmentation: low-contrast movement
may still blur or ghost; filtering noise in a static corner cannot
create identifiable scene detail; fixed sensor patterns remain.
No auto-exposure or Windows ISP is implemented. Full-4K synthetic
tests cover malformed frames, tone-off/scene-cut/sequence/profile
reset, moving high-contrast edge and unchanged UV. The independent
synthetic CPU benchmark cannot establish true camera conversion
overhead or physical quality, which need a newly guarded live trial
before any user-facing or production activation.


### Candidate-only AArch64 NEON 4K luma temporal acceleration

The separate explicit SP11_REAR_TEMPORAL_ENABLE_NEON=1 build provides
AArch64 16-lane vector processing of eight exact 2x2 motion gates at
once; default-OFF front/rear maintained Golden camera remains unchanged.
The AArch64 test runs scalar and NEON in the same executable over only
synthetic full 4K NV12, comparing the entire output, Y history and
statistics bit-for-bit across noise, moved contrast edges, scene cuts,
source frame gaps and tone reset. A standalone synthetic benchmark on
SP11 measured NEON ~1.1ms versus scalar ~17.5ms for that fixture in
three repeated interleaved runs. Different runtime loads change times;
this does not prove live 29-30fps or scene detail. Prior physical E004mu
scalar rear temporal candidate failed at28.8485fps; DO NOT lower the
29fps requirement, or rearm that consumed candidate. New physical
SIMD testing requires its own source-locked one-shot.

### Offline-only bounded native sensor brightness *planning* gate

preview_brightness_policy.py has no device, file, image, network or
sensor-writing API. Its synthetic tests exercise a hypothetical
one-time selection between ONLY the front/rear baseline and trial
native RGB V4L2 exposure/gain tuples already physically tested, with
an unchanged active fixed frame/30fps sensor mode, an independent
real-source 29fps-or-higher gate, 30 consecutive frames, exact
source/control readback, IR off and exclusive route prerequisites.
It can output scalar TRIAL_ELIGIBLE or REVERT_ELIGIBLE but every
decision has eligible_for_live_control_write=False. A live driver
must NEVER treat this report as authorization to write the sensor.

In particular, a truly dark/occluded or overexposed scene must not
cause unbounded gain/black-level lift, a front scene that remains
dim after the known trial must not be labeled usable, and missing
sensor readback/FPS/sequence or route safety poisons the proposal.
No neutral color or known-dark reference has been observed:
scene recognition, raw black/SNR, automatic exposure/white balance
and OEM Windows ISP are still unproven. The E004mv real front/rear
published scalar baseline/trial values can inform a separate,
source-only decision audit, not a claimed live closed-loop result.


E004mx isolated default-OFF FRONT1080 gain-only NV12 luma tone helper: front_preview_tone.h is camera-free and never invoked by normal maintained front/rear camera. For the supported front gain source p01~30/p99~61, an opt-in 1080p Y-only test maps p01 to100 with 2x contrast, preserving all UV bytes and source RAW10. Flat/black baseline, already bright, clipped and unsupported geometry bypass unchanged. This is NOT ISP/AE/colour calibration, recovered detail, true SNR, or released camera quality. Full-1080p synthetic tests verify gate, chroma and geometry before a fresh source-locked physical one-shot.

### Candidate-only BT.601 metadata mismatch and experimental solution

Current source RAW10->NV12 front/rear converters use approximately
BT.601 RGB/YUV integer coefficients and nominal studio-range YUV.
Through E004my the loopback publisher S_FMT left colorspace unspecified.
SP11 actual camera-free synthetic GStreamer appsrc->videoconvert->RGB
appsink selected BT.601 for unspecified 128x64, but BT.709 at BOTH
1920x1080 and 3840x2160. Synthetic RGB(192,32,32) converted to
BT.601-style studio YUV was decoded by default as RGB(203,44,29) at
both HD/UHD, while an explicit BT.601 decoder produced RGB(190,29,31).
Other neutral/red/green/blue/warm test patterns at explicit
BT.601 showed only tiny integer rounding differences. No real
optical pixel or image entered any synthetic experiment.

The opt-in-only helper iq/nv12_colorimetry.h is compiled into BOTH
front/rear existing source publishers ONLY with
SP11_RGB_NV12_BT601_TAG=1, and requests/validates exact V4L2
SMPTE170M colorspace, YCBCR_601, limited quantization and
XFER_709 before any camera STREAMON. If driver S_FMT fails to echo
metadata, fail closed. Normal maintained camera build defaults
remain unchanged. Standalone fake camera lifecycle C tests for
both cameras and synthetic GStreamer HD/UHD contract PASS.
Source v4l2loopback v0.15.3 showed explicit valid colorspace is
preserved in its VIDIOC_S_FMT implementation; actual physical
UID1000 app negotiated caps still need separate real evidence
from a new source-locked Golden-guarded single-use candidate.
Sensor primaries, Bayer green mismatch, gamma, white balance,
noise, true detail and Windows native ISP parity remain unproven.
