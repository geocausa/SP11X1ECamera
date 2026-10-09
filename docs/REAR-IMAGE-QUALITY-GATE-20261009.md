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
