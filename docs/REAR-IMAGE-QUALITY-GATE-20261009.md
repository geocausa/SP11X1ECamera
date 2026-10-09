## 2026-10-09 rear statistics transport and IPA source qualification

Rear56 remains the latest hardware result: live exposure/gain changes and
their scoped response timing passed;56 is consumed/retired/unarmed. No new
camera Start, reboot or candidate arm occurred in this statistics source work.

New source E-NATIVE-REAR-STATISTICS-SOURCE-01 passes in quarantined source04.
The original all-ten-WM completed-generation/replacement-address proof is
unchanged. Six statistics allocations (WM11/12/13/14/16/18) are copied before
AUX zero/free into an independent V4L2 metadata buffer. Image WM0/1/2/3 are
not copied. Envelope stream/owner/request generation/sequence/completion
timestamp bind the copied allocations to the public completion. This transport
association does not establish same optical exposure/sensor-frame provenance. Timestamp is not SOF or
exposure time. Capacities are opaque allocation spans, NOT decoded active
grid lengths or a metering result. Raw/spatial statistics stay SAME SP11 only.

Rear libcamera joins each successful image with the generated native IPA's
validated receipt before completing its application Request. Duplicate,
foreign-owner/stream, skipped sequence, dropped statistics, malformed lengths
and mismatched timestamps are rejected. Metadata requeues only after the
IPA callback; synchronous IPA stop precedes mapping release. Unpaired final
tails are cancelled instead of fabricating a statistics association.

Actual shared producer/receiver117 assertions/59 negatives and actual kernel
copy hook30/23 passed under GCC and Clang with ASAN/UBSAN. ARM64 CAMSS W=1,
KCFLAGS=-Werror compiled; generated IPA interface/proxy, pipeline and module
compiled with zero warnings. Seven real libcamera tests passed, including
the actual rear IPA with shared memfd maps, callbacks, rejection and restart.
No photometric decoder, adaptive IPA, AE or image-quality parity is proven.
Source-only stage explicitly disables rear runtime authorization and has no
valid private profile. NEVER install/arm the source-only module.

Source-only failed01 fixture indentation, failed02 unused WM constant and
failed03 IPA option staging are preserved in original logs. Parent builder
guard initially refused before any stage; exact source-only declaration was
then added. Fresh04 passed; no hardware identities/counts changed.
Native105 streams/88 IDs/176 boots; Windows8 streams/8 IDs/16 boots.
Golden remains f8af5d50-9fab-4e7d-8489-4884c01a8e37. No OS sleep.

User update2026-10-09 18:30 BST: rear is still aimed at SP7 LCD; evening
outside light is shifting. This is contemporaneous subject information,
not independent illumination stability or output quality proof. Healthy
upper LCD ROI only for private comparisons; known dark lower display band
must not be diagnosed as a camera/lens defect. Reassess lighting per capture.

NEXT fresh57 runtime integration/qualification of statistics-to-IPA delivery
and clean cancellation/stop, then verify actual payload format/grid/counts
and exposure response before enabling bounded AE. Do not reuse56 or pretend
opaque statistics transport is decoded photometry. Performance deferred.
Evidence docs/NATIVE-REAR-STATISTICS-SOURCE-20261009.json.
Earlier entries are historical.

## 2026-10-09 current gate after native live-control qualification

Windows01/Linux55 reference comparison showed a native photometric gap.
Linux56 now proves twelve real libcamera exposure/gain changes reached
sensor registers during1200 Requests, with reversible global Y response.
Observed response2-3 frame-sequence counts after scheduled changes is a
scoped diagnostic measurement. Do not publish fictitious per-request
exposure metadata or claim universal SOF-latch timing from it.

Next: owner-bound hardware ISP statistics delivered to native libcamera
IPA, then bounded automatic exposure/gain with qualified settling and
stale-statistics rejection. The diagnostic completed-image Y reader stays
a qualification tool; it does not substitute for production ISP statistics.
Adaptive IPA/automatic exposure and visual/color/focus/Windows parity
remain unqualified. Native images and previews remain private on SP11.
Independent camera lifecycle safeguards stay mandatory; performance and
front calibration stay deferred. Earlier evidence below is historical.

# Rear image quality is the next release gate

User direction, 2026-10-09: prioritize actual image quality before further
performance optimization. This supersedes the independent-boot repeat and
longer soak as the immediate next milestone. Existing lifecycle/owner/DMA
safety checks remain mandatory for every capture.

## Current evidence

Candidate48 completed three400 public-libcamera Requests at29.9543/
29.9619/29.9609fps with no >50ms gaps and clean release. The capture probe
explicitly performs no pixel mapping, reading or file output. Transport
qualification therefore does not establish image integrity or quality.
Rear Windows optical parity, adaptive3A and focus behavior remain unproven.
Historical e004mg loopback/software-conversion previews cannot qualify this
current native hardware-ISP/libcamera NV12 path.

## Next bounded capture

Use a fresh one-use identity, current48 transport behavior, and a short
public-libcamera capture. Read selected completed buffers only after the
existing exact-owner/all10 retirement proof. Respect DMA-BUF CPU access
synchronization, per-plane offsets, stride and negotiated color space.
Validate output sizes before reading. Preserve normal Request reuse,
STREAMOFF/release, all4 physical stops, Golden fallback and watchdog.
Do not reuse consumed48 or silently change its immutable probe.

Save a small set of native NV12 frames and decoded previews in a sealed
0700 private folder with0600 files on the SAME SP11. Decode for inspection;
do not introduce a software ISP or a new camera daemon. No photos, RAW,
NV12, previews, spatial arrays or image-derived hashes may leave SP11 or
enter Git/chat. Only derived scalar diagnostics and independent code may
be exported. Do not claim visual inspection from frame metadata alone.

## Acceptance order

1. Image integrity: correct Y/UV layout and lengths; absence of constant,
   all-black, saturated, torn or repeated-corrupt output; clipping and
   luminance/chroma sanity. Scalar checks are screening, not visual parity.
2. Geometry: crop, orientation, Bayer interpretation, alignment and
   artifacts against a known target viewed locally on SP11.
3. Exposure and color: plausible brightness, neutral whites, color patches,
   clipping, black level and shading under recorded illumination.
4. Detail and focus: blur, sharpening artifacts, noise, lens/focus state.
   Static startup settings do not establish autofocus or adaptive3A.
5. Matched Windows comparison on this same SP11: same target, framing,
   lighting and documented exposure/focus conditions where controllable.
   Distinguish fixed-setting output from automatic-control behavior.
   If SP7 supplies the target, use its registered healthy upper screen ROI;
   its dark lower band is a display defect, not a camera defect.

Record the first dominant defect and fix it before doing cosmetic tuning.
Separate format/Bayer/crop/ISP configuration faults from exposure, white
balance, focus and tuning gaps. Keep Windows originals private on SP11.
A usable baseline plus an explicit defect list is required before resuming
longer performance/soak optimization. No full quality-parity claim from
one scene, global histogram, readable dimensions or frame counts alone.

## Remaining milestones

After rear image integrity and baseline quality are established: implement
and qualify missing IPA/3A/controls and matched optical parity, then return
to independent-boot reliability and longer soak. Front calibration stays
deferred until the rear gate is understood. No OS sleep/suspend testing.
