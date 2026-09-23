# Next physical acceptance gate: fixed visible target, dark reference and RAW temporal evidence

Status: SOURCE-ONLY PLAN. No user target placement, illumination calibration,
new camera boot, modified Golden or auto-exposure approval has occurred.
E004mf/mg/mh/mp and Windows E004kt/wn identities are CONSUMED; never
rearm/replay them or silently reuse their user Scheduled Tasks.

## Why another uncontrolled corner image is not the next acceptance test

E004mp rear RAW10 green G0 P01/P99=64/70 at baseline vs73/140 with
supported analogue gain, and the near-black RGB PNG p99=15→30. Two
separately captured gain images have coarse spatial correlation ~0.977.
The pattern might be actual corner texture OR persistent sensor FPN.
The fresh E004wn Windows colour oracle auto-exposed the rear corner to
NV12 mean Y≈148, whereas Linux used fixed native gain/exposure and had
RGB near black. The Windows/Linux times, optical field of view, exposure
readback units, illumination and pixel summary metrics were not matched.
No white/black sensor reference, measured noise or recognizable scene
has been validated.

## Admission gate before consuming another unique RGB camera boot

A visible-light, non-IR fixed target with distinguishable dark, mid-gray
and bright geometric features must be physically in each camera's
field of view. Rear-facing wall/corner placement is not proof that a
target is visible. Its illumination, camera pointing and occlusion
should remain as stable as practical through a bounded Linux trial and
any subsequently justified fresh Windows oracle. Do not claim a
matched-scene comparison unless these facts are actually checked.
Obtain a distinct intentionally dark optical reference, not a guessed
RAW10 p01 or a live camera's unknown corner. Do not activate IR,
illuminators, Windows Hello, camera test pattern or OS-level Linux
suspend/standby/resume/hibernate to create a reference.

Any future physical run requires fresh single-use boot identity,
source/ELF SHA pinning, current overlap guard, IR-off and ordinary
front1080/rear4K app user+format checks, exact RGB subdevice control
range/readback/restore, bounded timestamps and explicit Golden fallback.
Use documented supported native controls only, no direct register writes
or implicit frame-rate/VBLANK change. Rear exposure 3200 already leaves
6 lines against current 3206-line mode maximum; front 3546 leaves
4 against active maximum3550. An altered 4K FPS/exposure mode would be a
separate design/review/validation, not part of this camera gate.

## Data to record locally without exporting images

1. A same-boot, same-control pair of source-locked native RAW10 frames
   from the same visible RGB camera at one known sensor exposure/gain,
   with bounded inter-frame timestamps. The pure-memory green
   raw10_temporal_spatial.h can compute global spatial and aligned
   temporal-change scalars from these frames; it has not yet been used
   on real hardware. Keep all pixel buffers and per-tile arrays private
   and transient. Its Pearson correlation and delta RMS are neither a
   calibrated signal-to-noise ratio nor proof of scene detail.
2. Separate illuminated-target and known dark-reference RAW10 channel
   distributions at identical controls, spatial/noise summaries,
   independent UID1000 NV12 luminance distribution (same metric as
   Windows), and root-only local RGB visual images. Do not subtract a
   fixed code64 or use an uncalibrated p01 as optical black.
3. Verify physical target recognizability in locally viewed private
   front/rear 1080p/4K images, not just higher Y, increasing tile std,
   auto-exposure status or RAW gain response. Keep all original photos
   on SP11 in a 0700 user-private folder with 0600 files. No optical
   pixels, thumbnails or hashes need be sent to Git, ChatGPT or other
   hosts.
4. If and only if a specific Linux ambiguity remains, create a new
   guarded Windows colour NV12 oracle while the same optical target is
   demonstrably fixed. Compare like-for-like native frame luminance
   quantiles and dark fractions with timestamps/control metadata.
   WinRT ExposureControl.Auto=true and nominal 5000 ticks do not
   prove the underlying sensor's register exposure or gain.
5. Retire the new candidate once, check protected Golden and no camera
   nodes/modules/processes, archive scalar-only accepted/failure
   evidence and document any unproven optical assumptions.

Only after a measured dark reference and stable lit target distinguish
actual scene structure from fixed/temporal sensor noise should a
separately opt-in exposure controller or RAW10-aware tone/colour
correction be implemented and given a new physical acceptance test.
The current read-only exposure_envelope.py intentionally does not
generate a sensor write target.
